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
            "Version: 10.20-r10\n",
        )
        self.assertIn(
            'APP_VERSION = "10.20-r10"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.20-r10",
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
            self.workspace, archive, app_version="10.20-r10",
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


if __name__ == "__main__":
    unittest.main()
