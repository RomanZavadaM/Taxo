# -*- coding: utf-8 -*-
import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from docx import Document
import document_catalog
from document_vault_paper_scans import load_paper_scan, register_paper_scan, remove_paper_scan
from document_vault_store import register_prepared_revision
from paper_document_store import list_documents, save_docx_bytes

class CatalogPaperScanIndicatorR9Tests(unittest.TestCase):
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
        path = save_docx_bytes(self.workspace, payload, "Інструкція", "Безпека руху", "2026-11-17", metadata=metadata)
        row = next(item for item in list_documents(self.workspace) if item["file"] == path.name)
        return register_prepared_revision(self.workspace, row["id"])

    def _scan(self, name, marker):
        path = self.base / name
        path.write_bytes(b"%PDF-1.4\n" + marker.encode("ascii") + b"\n%%EOF\n")
        return path

    def _catalog_row(self, vault_id):
        snapshot = document_catalog.read_sources(self.workspace)
        row = next(item for item in snapshot["rows"] if item.get("vault_id") == vault_id)
        return snapshot, row

    def test_r9_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.21-r7\n")
        self.assertIn('APP_VERSION = "10.21-r7"', (root / "main.py").read_text("utf-8"))
        self.assertIn("Taxo 10.21-r7", (root / "START.bat").read_text("utf-8"))

    def test_catalog_shows_only_active_scan_count(self):
        vault = self._vault_document()
        first = register_paper_scan(self.workspace, vault.vault_id, self._scan("one.pdf", "scan-one"))
        register_paper_scan(self.workspace, vault.vault_id, self._scan("two.pdf", "scan-two"))
        snapshot, row = self._catalog_row(vault.vault_id)
        self.assertEqual(row["paper_scan_count"], 2)
        self.assertEqual(row["paper_scan_state"], "Є: 2")
        self.assertIn("Активні скани: 2.", snapshot["paper_scan_status"])
        remove_paper_scan(self.workspace, first.attachment_id)
        _, row = self._catalog_row(vault.vault_id)
        self.assertEqual(row["paper_scan_count"], 1)
        self.assertEqual(row["paper_scan_state"], "Є: 1")

    def test_removed_only_scan_is_shown_as_no_active_scan(self):
        vault = self._vault_document()
        scan = register_paper_scan(self.workspace, vault.vault_id, self._scan("removed.pdf", "scan-removed"))
        remove_paper_scan(self.workspace, scan.attachment_id)
        _, row = self._catalog_row(vault.vault_id)
        self.assertEqual(row["paper_scan_count"], 0)
        self.assertEqual(row["paper_scan_state"], "Немає")

    def test_broken_scan_does_not_hide_document_catalog(self):
        vault = self._vault_document()
        scan = register_paper_scan(self.workspace, vault.vault_id, self._scan("broken.pdf", "scan-before-damage"))
        stored = load_paper_scan(self.workspace, scan.attachment_id)
        stored.path.write_bytes(b"%PDF-1.4\ndamaged\n")
        snapshot, row = self._catalog_row(vault.vault_id)
        self.assertIn("Помилка перевірки сканів:", snapshot["paper_scan_status"])
        self.assertIsNone(row["paper_scan_count"])
        self.assertEqual(row["paper_scan_state"], "Помилка перевірки")

    def test_catalog_ui_has_scan_column_without_signed_wording(self):
        root = Path(__file__).resolve().parents[1]
        source = (root / "src" / "taxo" / "document_catalog_ui.py").read_text("utf-8")
        self.assertIn('("scans", "Скани", 90)', source)
        self.assertIn('row.get("paper_scan_state", "—")', source)
        self.assertNotIn('text="Підписано"', source)

if __name__ == "__main__":
    unittest.main()
