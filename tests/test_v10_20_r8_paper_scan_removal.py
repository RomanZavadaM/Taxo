# -*- coding: utf-8 -*-
import hashlib
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path

from docx import Document

from document_vault_paper_scans import (
    list_paper_scans,
    list_removed_paper_scans,
    load_paper_scan,
    paper_scan_root,
    register_paper_scan,
    remove_paper_scan,
)
from document_vault_store import (
    list_document_vault,
    register_prepared_revision,
)
from paper_document_store import list_documents, save_docx_bytes
from workspace import (
    create_workspace_backup_archive,
    restore_workspace_backup_archive,
)


class PaperScanRemovalHistoryR8Tests(unittest.TestCase):
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
            self.workspace,
            payload,
            "Інструкція",
            "Безпека руху",
            "2026-11-17",
            metadata=metadata,
        )
        row = next(
            item for item in list_documents(self.workspace)
            if item["file"] == path.name
        )
        return register_prepared_revision(self.workspace, row["id"])

    def _scan(self, name="scan.pdf"):
        payload = b"%PDF-1.4\nsynthetic paper scan r8\n%%EOF\n"
        path = self.base / name
        path.write_bytes(payload)
        return path, payload

    def test_r8_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.23-r5\n",
        )
        self.assertIn(
            'APP_VERSION = "10.23-r5"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.23-r5",
            (root / "START.bat").read_text("utf-8"),
        )

    def test_remove_hides_scan_but_preserves_immutable_bytes_and_history(self):
        vault = self._vault_document()
        source, payload = self._scan()
        scan = register_paper_scan(self.workspace, vault.vault_id, source)
        stored = load_paper_scan(self.workspace, scan.attachment_id)
        stored_path = stored.path

        removed = remove_paper_scan(self.workspace, scan.attachment_id)

        self.assertEqual(removed.record.attachment_id, scan.attachment_id)
        self.assertEqual(removed.history.action, "removed")
        self.assertEqual(list_paper_scans(self.workspace, vault.vault_id), ())
        history = list_removed_paper_scans(self.workspace, vault.vault_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].record.sha256, scan.sha256)
        self.assertTrue(stored_path.is_file())
        self.assertEqual(stored_path.read_bytes(), payload)
        with self.assertRaisesRegex(ValueError, "не знайдено"):
            load_paper_scan(self.workspace, scan.attachment_id)

    def test_remove_is_explicit_once_only_and_does_not_change_document_state(self):
        vault = self._vault_document()
        source, _ = self._scan()
        scan = register_paper_scan(self.workspace, vault.vault_id, source)

        remove_paper_scan(self.workspace, scan.attachment_id)
        with self.assertRaisesRegex(ValueError, "уже прибрано"):
            remove_paper_scan(self.workspace, scan.attachment_id)

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
        self.assertNotIn("verification", history_text)

    def test_removed_scan_is_still_integrity_checked(self):
        vault = self._vault_document()
        source, _ = self._scan()
        scan = register_paper_scan(self.workspace, vault.vault_id, source)
        stored = load_paper_scan(self.workspace, scan.attachment_id)
        remove_paper_scan(self.workspace, scan.attachment_id)
        stored.path.write_bytes(b"%PDF-1.4\nchanged after removal\n")

        with self.assertRaisesRegex(ValueError, "розмір|цілісність"):
            list_removed_paper_scans(self.workspace, vault.vault_id)

    def test_full_backup_restores_removed_history_and_bytes(self):
        vault = self._vault_document()
        source, payload = self._scan()
        scan = register_paper_scan(self.workspace, vault.vault_id, source)
        remove_paper_scan(self.workspace, scan.attachment_id)

        data = self.workspace / "Data"
        data.mkdir(exist_ok=True)
        db = data / "driver_worktime.sqlite3"
        con = sqlite3.connect(str(db))
        try:
            con.execute("CREATE TABLE backup_probe(id INTEGER PRIMARY KEY)")
            con.commit()
        finally:
            con.close()

        archive = self.base / "backup.zip"
        create_workspace_backup_archive(
            self.workspace,
            archive,
            app_version="10.21-r7",
        )
        restored = self.base / "Restored"
        restore_workspace_backup_archive(archive, restored)

        self.assertEqual(list_paper_scans(restored, vault.vault_id), ())
        history = list_removed_paper_scans(restored, vault.vault_id)
        self.assertEqual(len(history), 1)
        record = history[0].record
        stored_path = paper_scan_root(restored).joinpath(
            *record.storage_key.split("/")
        )
        self.assertEqual(stored_path.read_bytes(), payload)

    def test_ui_exposes_remove_and_history_without_physical_delete_wording(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "src" / "taxo" / "document_vault_paper_scans_ui.py"
        ).read_text("utf-8")
        self.assertIn('text="Прибрати", state="disabled"', source)
        self.assertIn('text="Історія…"', source)
        self.assertIn("remove_paper_scan(", source)
        self.assertIn("list_removed_paper_scans(", source)
        self.assertIn('start_background("remove", worker)', source)
        self.assertIn('"history",', source)
        self.assertIn("Taxo НЕ видалить незмінний файл", source)
        self.assertIn("не змінює статус документа", source)


if __name__ == "__main__":
    unittest.main()
