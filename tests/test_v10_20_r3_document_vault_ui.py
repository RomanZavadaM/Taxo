# -*- coding: utf-8 -*-
import hashlib
import io
import queue
import tempfile
import unittest
from pathlib import Path

from docx import Document

from document_vault_store import (
    DocumentVaultRecord,
    list_document_vault,
)
from document_vault_ui import (
    format_document_vault_details,
    start_prepared_revision_registration,
)
from paper_document_store import list_documents, save_docx_bytes


class DocumentVaultUiR3Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _docx_bytes(text):
        document = Document()
        document.add_paragraph(text)
        stream = io.BytesIO()
        document.save(stream)
        return stream.getvalue()

    def _prepared_revision(self):
        payload = self._docx_bytes("Контрольована редакція для DocumentVault")
        metadata = {
            "origin": "prepared_snapshot",
            "document_status": "prepared",
            "prepared_snapshot_id": "pd-" + "1" * 32,
            "company_template_id": "ct-" + "2" * 32,
            "template_revision": 4,
            "template_source_sha256": "a" * 64,
            "content_sha256": hashlib.sha256(payload).hexdigest(),
        }
        path = save_docx_bytes(
            self.workspace,
            payload,
            "Інструкція",
            "Безпека руху",
            "2026-11-16",
            metadata=metadata,
        )
        row = next(
            item for item in list_documents(self.workspace)
            if item["file"] == path.name
        )
        return row, payload

    def test_r3_identity_and_start_guard(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.21-r10\n",
        )
        self.assertIn(
            'APP_VERSION = "10.21-r10"',
            (root / "main.py").read_text("utf-8"),
        )
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn("Taxo 10.21-r10", start)
        self.assertIn("document_vault_ui.py", start)

    def test_async_bridge_registers_exact_selected_revision(self):
        source, payload = self._prepared_revision()
        results = queue.Queue()
        thread = start_prepared_revision_registration(
            self.workspace,
            source["id"],
            results,
        )
        ok, record = results.get(timeout=10)
        thread.join(timeout=10)

        self.assertTrue(ok, record)
        self.assertFalse(thread.is_alive())
        self.assertEqual(record.source_document_id, source["id"])
        self.assertEqual(record.document_revision, 1)
        self.assertEqual(record.content_sha256, hashlib.sha256(payload).hexdigest())
        self.assertEqual(list_document_vault(self.workspace), (record,))

    def test_async_bridge_reports_duplicate_without_new_object(self):
        source, _payload = self._prepared_revision()
        first = queue.Queue()
        start_prepared_revision_registration(
            self.workspace, source["id"], first
        ).join(timeout=10)
        self.assertTrue(first.get(timeout=1)[0])

        second = queue.Queue()
        start_prepared_revision_registration(
            self.workspace, source["id"], second
        ).join(timeout=10)
        ok, error = second.get(timeout=1)
        self.assertFalse(ok)
        self.assertIn("вже є", error)
        self.assertEqual(len(list_document_vault(self.workspace)), 1)

    def test_read_only_details_show_full_provenance_and_hashes(self):
        record = DocumentVaultRecord(
            vault_id="vd-" + "f" * 32,
            title="Інструкція з безпеки",
            kind="Інструкція",
            document_date="2026-11-16",
            status="ready",
            created_at="2026-11-16T09:00:00+00:00",
            source_document_id="doc-" + "1" * 32,
            prepared_snapshot_id="pd-" + "2" * 32,
            document_family_id="family-" + "3" * 32,
            document_revision=3,
            company_template_id="ct-" + "4" * 32,
            template_revision=5,
            template_source_sha256="a" * 64,
            content_sha256="b" * 64,
            original_name="instruction.docx",
            storage_key="objects/ff/vd-" + "f" * 32 + ".docx",
            size_bytes=12345,
        )
        text = format_document_vault_details(record)
        for expected in (
            "Готовий документ",
            "Редакція документа: r3",
            record.source_document_id,
            record.prepared_snapshot_id,
            record.document_family_id,
            record.company_template_id,
            record.template_source_sha256,
            record.content_sha256,
            "12345 байт",
            "не є автоматичним підтвердженням підпису",
        ):
            self.assertIn(expected, text)

    def test_catalog_exposes_explicit_store_and_browse_actions(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn("start_prepared_revision_registration", source)
        self.assertIn("open_document_vault", source)
        self.assertIn("Зберегти вибрану редакцію у сховищі", source)
        self.assertIn("Переглянути сховище документів", source)
        self.assertIn("_taxo_catalog_vault_store", source)
        self.assertIn("_taxo_catalog_vault_open", source)
        self.assertIn("not _is_controlled_prepared_row(row)", source)
        self.assertIn("не означає, що документ підписано", source)

    def test_vault_browser_is_read_only_and_main_is_not_expanded(self):
        root = Path(__file__).resolve().parents[1]
        ui = (
            root / "src" / "taxo" / "document_vault_ui.py"
        ).read_text("utf-8")
        main_source = (root / "main.py").read_text("utf-8")
        self.assertIn('state="disabled"', ui)
        self.assertIn("list_document_vault", ui)
        self.assertNotIn("update_document_vault", ui)
        self.assertNotIn("delete_document_vault", ui)
        self.assertNotIn("document_vault_ui", main_source)


if __name__ == "__main__":
    unittest.main()
