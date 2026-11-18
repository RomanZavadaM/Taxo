# -*- coding: utf-8 -*-
"""10.22-r4: safe opening of immutable DocumentVault documents."""
import hashlib
import io
import stat
import tempfile
import unittest
from pathlib import Path

from docx import Document

from document_vault_store import (
    document_vault_root,
    load_document_vault_object,
    register_prepared_revision,
)
from document_vault_ui import prepare_document_vault_view_copy
from paper_document_store import list_documents, save_docx_bytes


class DocumentVaultOpenR4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _docx_bytes(text="Перевірений документ"):
        document = Document()
        document.add_paragraph(text)
        stream = io.BytesIO()
        document.save(stream)
        return stream.getvalue()

    def _register(self):
        payload = self._docx_bytes()
        metadata = {
            "origin": "prepared_snapshot",
            "document_status": "prepared",
            "prepared_snapshot_id": "pd-" + "4" * 32,
            "company_template_id": "ct-" + "5" * 32,
            "template_revision": 1,
            "template_source_sha256": "a" * 64,
            "content_sha256": hashlib.sha256(payload).hexdigest(),
        }
        path = save_docx_bytes(
            self.workspace,
            payload,
            "Інструкція",
            "Перегляд зі сховища",
            "2026-11-18",
            metadata=metadata,
        )
        source = next(
            row for row in list_documents(self.workspace)
            if row["file"] == path.name
        )
        record = register_prepared_revision(
            self.workspace, source["id"]
        )
        return record, payload

    def test_verified_view_copy_is_exact_read_only_and_outside_vault(self):
        record, payload = self._register()
        stored = load_document_vault_object(
            self.workspace, record.vault_id
        )

        view = prepare_document_vault_view_copy(
            self.workspace, record.vault_id
        )

        self.assertTrue(view.is_file())
        self.assertEqual(view.suffix.lower(), ".docx")
        self.assertEqual(view.read_bytes(), payload)
        self.assertNotEqual(view.resolve(), stored.path.resolve())
        with self.assertRaises(ValueError):
            view.resolve().relative_to(
                document_vault_root(self.workspace).resolve()
            )
        self.assertEqual(view.stat().st_mode & stat.S_IWUSR, 0)

    def test_tampered_vault_object_is_not_materialized_for_viewing(self):
        record, _payload = self._register()
        stored = load_document_vault_object(
            self.workspace, record.vault_id
        )
        stored.path.write_bytes(b"tampered")

        with self.assertRaisesRegex(ValueError, "розмір|цілісність"):
            prepare_document_vault_view_copy(
                self.workspace, record.vault_id
            )

    def test_catalog_opens_verified_copy_instead_of_immutable_object(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn("prepare_document_vault_view_copy(", source)
        self.assertIn("view_path = prepare_document_vault_view_copy", source)
        self.assertIn("open_document(", source)
        self.assertNotIn(
            "Taxo не відкриває її напряму для редагування", source
        )


if __name__ == "__main__":
    unittest.main()
