# -*- coding: utf-8 -*-
"""r9: reopen saved snapshots and append external DOCX revisions safely."""
from __future__ import annotations

import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
import unittest
from pathlib import Path

from docx import Document

from company_template_draft import CompanyTemplateDraft
from document_catalog import read_catalog
from document_catalog_ui import _is_controlled_prepared_row
from paper_document_store import list_documents, save_document
from prepared_document_registry import register_prepared_document
from prepared_document_revision import (
    copy_prepared_document_for_editing,
    import_prepared_document_revision,
)
from prepared_document_store import (
    create_prepared_snapshot,
    list_prepared_snapshots,
    load_prepared_snapshot,
)


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
            {
                "id": "p",
                "type": "paragraph",
                "text": "Правила безпечної роботи",
            }
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


class PreparedDocumentRevisionR9Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "Work"
        self.root.mkdir()
        self.outside = Path(tmp.name) / "Outside"
        self.outside.mkdir()

    def _registered(self):
        snapshot = create_prepared_snapshot(
            self.root, prepared_draft()
        )
        path = register_prepared_document(
            self.root, snapshot.snapshot_id
        )
        record = list_documents(self.root)[0]
        return snapshot, path, record

    def _edited_docx(self, name, text):
        path = self.outside / name
        doc = Document()
        doc.add_paragraph(text)
        doc.save(str(path))
        return path

    def test_revision_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertIn(
            (root / "VERSION.txt").read_text("utf-8").strip(),
            ("Version: 10.19-r9", "Version: 10.19-r10", "Version: 10.20-r1", "Version: 10.20-r2", "Version: 10.20-r3", "Version: 10.20-r4", "Version: 10.20-r5", "Version: 10.20-r6", "Version: 10.21-r7", "Version: 10.25-r6"),
        )
        main_source = (root / "main.py").read_text("utf-8")
        self.assertTrue(
            'APP_VERSION = "10.19-r9"' in main_source
            or 'APP_VERSION = "10.19-r10"' in main_source
            or 'APP_VERSION = "10.20-r1"' in main_source
            or 'APP_VERSION = "10.20-r2"' in main_source
            or 'APP_VERSION = "10.20-r3"' in main_source
            or 'APP_VERSION = "10.20-r4"' in main_source
            or 'APP_VERSION = "10.20-r5"' in main_source
            or 'APP_VERSION = "10.20-r6"' in main_source
            or 'APP_VERSION = "10.21-r7"' in main_source
            or 'APP_VERSION = "10.25-r6"' in main_source
        )
        start_source = (root / "START.bat").read_text("utf-8")
        self.assertTrue(
            "Taxo 10.19-r9" in start_source
            or "Taxo 10.19-r10" in start_source
            or "Taxo 10.20-r1" in start_source
            or "Taxo 10.20-r2" in start_source
            or "Taxo 10.20-r3" in start_source
            or "Taxo 10.20-r4" in start_source
            or "Taxo 10.20-r5" in start_source
            or "Taxo 10.20-r6" in start_source
            or "Taxo 10.21-r7" in start_source
            or "Taxo 10.25-r6" in start_source
        )

    def test_prepared_catalog_row_is_controlled_before_external_open(self):
        row = {
            "source": "paper",
            "prepared_snapshot_id": "pd-" + "a" * 32,
            "file_path": Path("controlled.docx"),
        }
        self.assertTrue(_is_controlled_prepared_row(row))
        row["prepared_snapshot_id"] = ""
        self.assertFalse(_is_controlled_prepared_row(row))

    def test_saved_snapshot_can_be_listed_and_loaded_later(self):
        snapshot = create_prepared_snapshot(
            self.root, prepared_draft()
        )
        listed = list_prepared_snapshots(self.root)
        self.assertEqual(
            [item.snapshot_id for item in listed],
            [snapshot.snapshot_id],
        )
        loaded = load_prepared_snapshot(
            self.root, snapshot.snapshot_id
        )
        self.assertEqual(
            loaded.data["rendered_content"],
            "Правила безпечної роботи",
        )

    def test_external_edit_becomes_r2_without_overwriting_r1(self):
        snapshot, original, r1 = self._registered()
        original_bytes = original.read_bytes()
        edited = self._edited_docx(
            "edited.docx", "Правила безпечної роботи — редакція 2"
        )

        result = import_prepared_document_revision(
            self.root, r1["id"], edited
        )
        self.assertEqual(result.revision, 2)
        self.assertNotEqual(result.path, original)
        self.assertEqual(original.read_bytes(), original_bytes)
        self.assertTrue(result.path.is_file())

        records = list_documents(self.root)
        self.assertEqual(len(records), 2)
        r2 = next(
            row for row in records
            if row["id"] == result.document_id
        )
        self.assertEqual(r2["prepared_snapshot_id"], snapshot.snapshot_id)
        self.assertEqual(r2["document_family_id"], r1["id"])
        self.assertEqual(r2["document_revision"], 2)
        self.assertEqual(r2["previous_document_id"], r1["id"])
        self.assertEqual(r2["origin"], "edited_docx")
        self.assertFalse(r2["paper_signed"])

        rows = read_catalog(self.root)["rows"]
        visible = next(
            row for row in rows
            if row["source_id"] == result.document_id
        )
        self.assertEqual(visible["revision_label"], "r2")

    def test_revision_chain_increments_and_preserves_all_files(self):
        _snapshot, r1_path, r1 = self._registered()
        r2_source = self._edited_docx(
            "r2.docx", "Редакція 2"
        )
        r2_result = import_prepared_document_revision(
            self.root, r1["id"], r2_source
        )
        r2_path = r2_result.path
        r3_source = self._edited_docx(
            "r3.docx", "Редакція 3"
        )
        r3_result = import_prepared_document_revision(
            self.root, r2_result.document_id, r3_source
        )
        self.assertEqual(r3_result.revision, 3)
        self.assertEqual(
            r3_result.previous_document_id,
            r2_result.document_id,
        )
        self.assertTrue(r1_path.is_file())
        self.assertTrue(r2_path.is_file())
        self.assertTrue(r3_result.path.is_file())
        self.assertEqual(len(list_documents(self.root)), 3)

    def test_parallel_catalog_writes_keep_every_record(self):
        def add(number):
            doc = Document()
            doc.add_paragraph("Паралельний документ %d" % number)
            return save_document(
                self.root,
                doc,
                "Інструктаж",
                "Паралельний %d" % number,
                "2026-11-15",
            )

        with ThreadPoolExecutor(max_workers=8) as pool:
            paths = list(pool.map(add, range(12)))
        records = list_documents(self.root)
        self.assertEqual(len(records), 12)
        self.assertEqual(len({row["id"] for row in records}), 12)
        self.assertEqual(len({row["file"] for row in records}), 12)
        self.assertTrue(all(path.is_file() for path in paths))

    def test_same_bytes_are_not_added_as_fake_new_revision(self):
        _snapshot, original, r1 = self._registered()
        same = self.outside / "same.docx"
        shutil.copyfile(original, same)
        with self.assertRaisesRegex(
            ValueError, "не містить змін"
        ):
            import_prepared_document_revision(
                self.root, r1["id"], same
            )
        self.assertEqual(len(list_documents(self.root)), 1)

    def test_catalog_file_cannot_be_imported_as_external_revision(self):
        _snapshot, original, r1 = self._registered()
        with self.assertRaisesRegex(
            ValueError, "каталогу Taxo"
        ):
            import_prepared_document_revision(
                self.root, r1["id"], original
            )

    def test_non_prepared_legacy_record_is_rejected(self):
        doc = Document()
        doc.add_paragraph("Legacy")
        path = save_document(
            self.root,
            doc,
            "Інструктаж",
            "Старий документ",
            "2026-11-15",
        )
        self.assertTrue(path.is_file())
        legacy = list_documents(self.root)[0]
        source = self._edited_docx(
            "legacy-edit.docx", "Legacy edit"
        )
        with self.assertRaisesRegex(
            ValueError, "prepared-документа"
        ):
            import_prepared_document_revision(
                self.root, legacy["id"], source
            )

    def test_editing_copy_is_external_and_exact(self):
        _snapshot, original, r1 = self._registered()
        target = self.outside / "working-copy.docx"
        copied = copy_prepared_document_for_editing(
            self.root, r1["id"], target
        )
        self.assertEqual(copied, target)
        self.assertEqual(copied.read_bytes(), original.read_bytes())
        self.assertTrue(original.is_file())

    def test_start_package_guards_new_r9_modules(self):
        root = Path(__file__).resolve().parents[1]
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn(
            "prepared_document_revision.py", start
        )
        self.assertIn(
            "prepared_document_list_ui.py", start
        )
        company_ui = (
            root / "src" / "taxo" / "company_template_list_ui.py"
        ).read_text("utf-8")
        self.assertIn(
            "open_prepared_documents", company_ui
        )


if __name__ == "__main__":
    unittest.main()
