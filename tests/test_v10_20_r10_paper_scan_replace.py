# -*- coding: utf-8 -*-
import hashlib
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from docx import Document

import document_vault_paper_scans as scans
from document_vault_paper_scans import (
    list_paper_scans,
    list_removed_paper_scans,
    load_paper_scan,
    paper_scan_root,
    register_paper_scan,
    replace_paper_scan,
)
from document_vault_store import list_document_vault, register_prepared_revision
from paper_document_store import list_documents, save_docx_bytes
from workspace import create_workspace_backup_archive, restore_workspace_backup_archive


class PaperScanReplaceR10Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.workspace = self.base / "Work"
        self.workspace.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _docx_bytes(text="Документ"):
        document = Document()
        document.add_paragraph(text)
        stream = io.BytesIO()
        document.save(stream)
        return stream.getvalue()

    def _vault_document(self):
        payload = self._docx_bytes()
        metadata = {
            "origin": "prepared_snapshot",
            "document_status": "prepared",
            "prepared_snapshot_id": "pd-" + "1" * 32,
            "company_template_id": "ct-" + "2" * 32,
            "template_revision": 3,
            "template_source_sha256": "a" * 64,
            "content_sha256": hashlib.sha256(payload).hexdigest(),
        }
        path = save_docx_bytes(
            self.workspace, payload, "Інструкція", "Безпека руху",
            "2026-11-17", metadata=metadata,
        )
        row = next(
            item for item in list_documents(self.workspace)
            if item["file"] == path.name
        )
        return register_prepared_revision(self.workspace, row["id"])

    def _pdf(self, name, marker):
        path = self.base / name
        payload = b"%PDF-1.4\n" + marker.encode("ascii") + b"\n%%EOF\n"
        path.write_bytes(payload)
        return path, payload

    def test_r10_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.24-r3\n",
        )
        self.assertIn(
            'APP_VERSION = "10.24-r3"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.24-r3",
            (root / "START.bat").read_text("utf-8"),
        )

    def test_replace_keeps_old_bytes_and_new_scan_active(self):
        vault = self._vault_document()
        old_source, old_payload = self._pdf("old.pdf", "old-r10")
        new_source, new_payload = self._pdf("new.pdf", "new-r10")
        old = register_paper_scan(self.workspace, vault.vault_id, old_source)
        old_path = load_paper_scan(self.workspace, old.attachment_id).path

        result = replace_paper_scan(
            self.workspace, old.attachment_id, new_source,
        )

        self.assertEqual(result.previous.history.action, "replaced")
        self.assertEqual(
            result.previous.record.attachment_id, old.attachment_id,
        )
        self.assertNotEqual(result.current.attachment_id, old.attachment_id)
        active = list_paper_scans(self.workspace, vault.vault_id)
        self.assertEqual(
            [item.attachment_id for item in active],
            [result.current.attachment_id],
        )
        self.assertEqual(
            load_paper_scan(
                self.workspace, result.current.attachment_id
            ).path.read_bytes(),
            new_payload,
        )
        self.assertEqual(old_path.read_bytes(), old_payload)
        history = list_removed_paper_scans(self.workspace, vault.vault_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].history.action, "replaced")
        with self.assertRaisesRegex(ValueError, "не знайдено"):
            load_paper_scan(self.workspace, old.attachment_id)

    def test_invalid_or_duplicate_replacement_leaves_old_scan_active(self):
        vault = self._vault_document()
        old_source, _ = self._pdf("same.pdf", "same-r10")
        old = register_paper_scan(self.workspace, vault.vault_id, old_source)

        with self.assertRaisesRegex(ValueError, "уже додано"):
            replace_paper_scan(
                self.workspace, old.attachment_id, old_source,
            )

        invalid = self.base / "invalid.pdf"
        invalid.write_text("not a pdf", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "не схожий|відповідає"):
            replace_paper_scan(
                self.workspace, old.attachment_id, invalid,
            )

        active = list_paper_scans(self.workspace, vault.vault_id)
        self.assertEqual(
            [item.attachment_id for item in active],
            [old.attachment_id],
        )
        self.assertEqual(
            list_removed_paper_scans(self.workspace, vault.vault_id), ()
        )

    def test_history_write_failure_rolls_back_new_scan(self):
        vault = self._vault_document()
        old_source, _ = self._pdf("old-rollback.pdf", "old-rollback")
        new_source, _ = self._pdf("new-rollback.pdf", "new-rollback")
        old = register_paper_scan(self.workspace, vault.vault_id, old_source)
        original_atomic_write = scans._atomic_write

        def fail_history(path, payload):
            if path.name == scans.HISTORY_NAME:
                raise OSError("synthetic history failure")
            return original_atomic_write(path, payload)

        with patch.object(
            scans, "_atomic_write", side_effect=fail_history
        ):
            with self.assertRaisesRegex(
                OSError, "synthetic history failure"
            ):
                replace_paper_scan(
                    self.workspace, old.attachment_id, new_source,
                )

        active = list_paper_scans(self.workspace, vault.vault_id)
        self.assertEqual(
            [item.attachment_id for item in active],
            [old.attachment_id],
        )
        self.assertEqual(
            list_removed_paper_scans(self.workspace, vault.vault_id), ()
        )
        root = paper_scan_root(self.workspace)
        objects = [
            path for path in (root / "objects").rglob("*")
            if path.is_file()
        ]
        self.assertEqual(len(objects), 1)

    def test_replace_does_not_change_document_business_state(self):
        vault = self._vault_document()
        old_source, _ = self._pdf("state-old.pdf", "state-old")
        new_source, _ = self._pdf("state-new.pdf", "state-new")
        old = register_paper_scan(self.workspace, vault.vault_id, old_source)
        replace_paper_scan(
            self.workspace, old.attachment_id, new_source,
        )
        current = next(
            item for item in list_document_vault(self.workspace)
            if item.vault_id == vault.vault_id
        )
        self.assertEqual(current.status, "ready")
        history_text = (
            paper_scan_root(self.workspace) / "history.json"
        ).read_text("utf-8").casefold()
        self.assertNotIn("signed", history_text)
        self.assertNotIn("signature", history_text)

    def test_full_backup_restores_replacement_history_and_both_bytes(self):
        vault = self._vault_document()
        old_source, old_payload = self._pdf(
            "backup-old.pdf", "backup-old"
        )
        new_source, new_payload = self._pdf(
            "backup-new.pdf", "backup-new"
        )
        old = register_paper_scan(self.workspace, vault.vault_id, old_source)
        result = replace_paper_scan(
            self.workspace, old.attachment_id, new_source,
        )

        data = self.workspace / "Data"
        data.mkdir(exist_ok=True)
        db = data / "driver_worktime.sqlite3"
        con = sqlite3.connect(str(db))
        try:
            con.execute(
                "CREATE TABLE backup_probe(id INTEGER PRIMARY KEY)"
            )
            con.commit()
        finally:
            con.close()

        archive = self.base / "backup.zip"
        create_workspace_backup_archive(
            self.workspace, archive, app_version="10.21-r7",
        )
        restored = self.base / "Restored"
        restore_workspace_backup_archive(archive, restored)

        active = list_paper_scans(restored, vault.vault_id)
        self.assertEqual(len(active), 1)
        self.assertEqual(
            active[0].attachment_id, result.current.attachment_id,
        )
        self.assertEqual(
            load_paper_scan(
                restored, active[0].attachment_id
            ).path.read_bytes(),
            new_payload,
        )
        history = list_removed_paper_scans(restored, vault.vault_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].history.action, "replaced")
        old_path = paper_scan_root(restored).joinpath(
            *history[0].record.storage_key.split("/")
        )
        self.assertEqual(old_path.read_bytes(), old_payload)

    def test_ui_exposes_one_step_replace_and_visible_history_action(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "src" / "taxo" / "document_vault_paper_scans_ui.py"
        ).read_text("utf-8")
        self.assertIn('text="Замінити…", state="disabled"', source)
        self.assertIn("replace_paper_scan(", source)
        self.assertIn('start_background("replace", worker)', source)
        self.assertIn('"Замінено"', source)
        self.assertIn(
            "Старий файл НЕ буде фізично стерто", source
        )
        self.assertIn("не змінює статус документа", source)


    def test_inactive_scan_cannot_be_replaced_again(self):
        vault = self._vault_document()
        old_source, _ = self._pdf("inactive-old.pdf", "inactive-old")
        new_source, _ = self._pdf("inactive-new.pdf", "inactive-new")
        old = register_paper_scan(self.workspace, vault.vault_id, old_source)
        replacement = replace_paper_scan(
            self.workspace, old.attachment_id, new_source,
        )
        with self.assertRaisesRegex(ValueError, "неактивний"):
            replace_paper_scan(
                self.workspace, old.attachment_id, new_source,
            )
        self.assertEqual(
            [item.attachment_id for item in list_paper_scans(self.workspace)],
            [replacement.current.attachment_id],
        )
        self.assertEqual(len(list_removed_paper_scans(self.workspace)), 1)

    def test_failed_history_and_failed_rollback_preserve_both_copies(self):
        vault = self._vault_document()
        old_source, old_bytes = self._pdf("fail-old.pdf", "fail-old")
        new_source, new_bytes = self._pdf("fail-new.pdf", "fail-new")
        old = register_paper_scan(self.workspace, vault.vault_id, old_source)
        original_write = scans._atomic_write
        index_writes = []

        def fail_history_and_rollback(path, payload):
            if path.name == scans.HISTORY_NAME:
                raise OSError("history unavailable")
            if path.name == scans.INDEX_NAME:
                index_writes.append(path)
                if len(index_writes) == 2:
                    raise OSError("rollback unavailable")
            return original_write(path, payload)

        with patch.object(
            scans, "_atomic_write", side_effect=fail_history_and_rollback,
        ):
            with self.assertRaisesRegex(RuntimeError, "безпечно відкотити"):
                replace_paper_scan(
                    self.workspace, old.attachment_id, new_source,
                )
        active = list_paper_scans(self.workspace)
        self.assertEqual(len(active), 2)
        self.assertEqual(
            {load_paper_scan(self.workspace, row.attachment_id).path.read_bytes()
             for row in active},
            {old_bytes, new_bytes},
        )
        self.assertEqual(list_removed_paper_scans(self.workspace), ())

    def test_tampering_with_replaced_scan_is_still_detected(self):
        vault = self._vault_document()
        old_source, _ = self._pdf("tamper-old.pdf", "tamper-old")
        new_source, _ = self._pdf("tamper-new.pdf", "tamper-new")
        old = register_paper_scan(self.workspace, vault.vault_id, old_source)
        old_path = load_paper_scan(self.workspace, old.attachment_id).path
        replace_paper_scan(self.workspace, old.attachment_id, new_source)
        old_path.write_bytes(b"%PDF-1.4\\ntampered\\n%%EOF")
        with self.assertRaises(ValueError):
            list_paper_scans(self.workspace)
        with self.assertRaises(ValueError):
            list_removed_paper_scans(self.workspace)


class PaperScanReplaceUiR10Tests(unittest.TestCase):
    def test_cancel_and_decline_do_not_replace_and_buttons_fit(self):
        import threading
        import time
        import tkinter as tk
        from tkinter import font, ttk
        from types import SimpleNamespace
        from unittest.mock import Mock
        import document_vault_paper_scans_ui as ui

        try:
            root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk display unavailable: %s" % exc)
        root.withdraw()
        self.addCleanup(root.destroy)
        default_font = font.Font(root=root, name="TkDefaultFont", exists=True)
        original_size = default_font.cget("size")
        self.addCleanup(lambda: default_font.configure(size=original_size))
        record = SimpleNamespace(
            attachment_id="va-" + "1" * 32,
            created_at="2026-11-17T12:00:00+00:00",
            original_name="existing.pdf",
            media_type="application/pdf",
            size_bytes=100,
            sha256="a" * 64,
        )
        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            fit_window_to_screen=lambda win, *args: win.geometry("900x600"),
            filedialog=SimpleNamespace(askopenfilename=Mock(return_value="")),
            messagebox=SimpleNamespace(
                askyesno=Mock(return_value=False),
                showinfo=Mock(),
                showerror=Mock(),
            ),
        )
        with patch.object(ui, "list_paper_scans", return_value=(record,)), \
             patch.object(ui, "replace_paper_scan") as replace, \
             patch.object(ui, "_IO_SLOT", threading.BoundedSemaphore(1)):
            win = ui.open_paper_scans_dialog(
                root, core, "synthetic-workspace", "vd-" + "2" * 32,
            )
            self.addCleanup(lambda: win.destroy() if win.winfo_exists() else None)
            deadline = time.monotonic() + 5
            while win._taxo_paper_scans_state["busy"] and time.monotonic() < deadline:
                root.update()
                time.sleep(0.01)
            self.assertFalse(win._taxo_paper_scans_state["busy"])
            win._taxo_paper_scans_replace()
            core.messagebox.askyesno.assert_not_called()
            replace.assert_not_called()
            core.filedialog.askopenfilename.return_value = "replacement.pdf"
            win._taxo_paper_scans_replace()
            core.messagebox.askyesno.assert_called_once()
            replace.assert_not_called()
            self.assertFalse(win._taxo_paper_scans_state["busy"])

            def buttons(widget):
                result = []
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        result.append(child)
                    result.extend(buttons(child))
                return result

            for size in (original_size, 16):
                default_font.configure(size=size)
                for width, height in ((900, 600), (1024, 700), (1366, 768)):
                    with self.subTest(font=size, viewport=(width, height)):
                        win.geometry("%dx%d" % (width, height))
                        root.update_idletasks()
                        found = {button.cget("text"): button for button in buttons(win)}
                        self.assertIn("Замінити…", found)
                        self.assertIn("Закрити", found)
                        for button in found.values():
                            left = button.winfo_rootx() - win.winfo_rootx()
                            top = button.winfo_rooty() - win.winfo_rooty()
                            self.assertGreaterEqual(left, 0)
                            self.assertGreaterEqual(top, 0)
                            self.assertLessEqual(left + button.winfo_width(), width)
                            self.assertLessEqual(top + button.winfo_height(), height)


if __name__ == "__main__":
    unittest.main()
