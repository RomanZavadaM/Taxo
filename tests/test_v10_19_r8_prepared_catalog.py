# -*- coding: utf-8 -*-
"""r8: prepared DOCX registration in existing Taxo catalog."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from docx import Document

from company_template_draft import CompanyTemplateDraft
from document_catalog import read_catalog
from paper_document_store import list_documents, save_document
from prepared_document_registry import register_prepared_document
from prepared_document_store import create_prepared_snapshot


def prepared_draft():
    rendered = {
        "format": "taxo.template.v1",
        "template_id": "instructions.test",
        "title": "Інструкція з охорони праці",
        "document_kind": "instruction",
        "scenario": "company-instruction",
        "language": "uk",
        "status": "proposed",
        "source_refs": [],
        "variables": [],
        "blocks": [
            {"id": "p", "type": "paragraph", "text": "Правила безпечної роботи"}
        ],
        "appendices": [],
    }
    return CompanyTemplateDraft(
        company_template_id="ct-" + "a" * 32,
        source_sha256="b" * 64,
        edit_revision=3,
        title="Інструкція з охорони праці",
        content="Правила безпечної роботи",
        variables=(),
        normalized_facts={},
        rendered_template=rendered,
    )


class PreparedDocumentCatalogR8Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "Work"
        self.root.mkdir()

    def test_generated_document_is_registered_and_visible(self):
        snapshot = create_prepared_snapshot(self.root, prepared_draft())
        path = register_prepared_document(self.root, snapshot.snapshot_id)
        self.assertTrue(path.is_file())
        self.assertEqual(path.parent, self.root / "Data" / "PaperDocuments")
        document = Document(str(path))
        self.assertIn(
            "Правила безпечної роботи",
            "\n".join(p.text for p in document.paragraphs),
        )
        entries = list_documents(self.root)
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["prepared_snapshot_id"], snapshot.snapshot_id)
        self.assertEqual(entry["company_template_id"], "ct-" + "a" * 32)
        self.assertEqual(entry["template_revision"], 3)
        self.assertEqual(entry["template_source_sha256"], "b" * 64)
        self.assertEqual(entry["document_status"], "prepared")
        self.assertFalse(entry["paper_signed"])
        visible = read_catalog(self.root)["rows"]
        self.assertEqual(len(visible), 1)
        self.assertEqual(visible[0]["source"], "paper")
        self.assertEqual(visible[0]["file_state"], "Файл доступний")

    def test_repeated_registration_cannot_create_duplicate(self):
        snapshot = create_prepared_snapshot(self.root, prepared_draft())
        register_prepared_document(self.root, snapshot.snapshot_id)
        with self.assertRaisesRegex(ValueError, "вже є у каталозі"):
            register_prepared_document(self.root, snapshot.snapshot_id)
        self.assertEqual(len(list_documents(self.root)), 1)

    def test_legacy_document_is_preserved(self):
        legacy = Document()
        legacy.add_paragraph("Старий інструктаж")
        old = save_document(
            self.root, legacy, "Інструктаж", "Старий запис", "2026-11-10"
        )
        snapshot = create_prepared_snapshot(self.root, prepared_draft())
        register_prepared_document(self.root, snapshot.snapshot_id)
        self.assertTrue(old.exists())
        self.assertEqual(len(list_documents(self.root)), 2)
        self.assertEqual(
            len([row for row in read_catalog(self.root)["rows"]
                 if row["source"] == "paper"]), 2
        )

    def test_no_automatic_registration_on_snapshot_creation(self):
        create_prepared_snapshot(self.root, prepared_draft())
        self.assertEqual(list_documents(self.root), [])
        self.assertFalse((self.root / "Data" / "PaperDocuments").exists())

    def test_export_registration_does_not_claim_signature(self):
        snapshot = create_prepared_snapshot(self.root, prepared_draft())
        with mock.patch("prepared_document_registry.save_document",
                        wraps=save_document) as save:
            register_prepared_document(self.root, snapshot.snapshot_id)
        self.assertEqual(save.call_count, 1)
        self.assertEqual(
            save.call_args.kwargs["metadata"]["document_status"], "prepared"
        )
        self.assertFalse(list_documents(self.root)[0]["paper_signed"])


if __name__ == "__main__":
    unittest.main()
