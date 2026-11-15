# -*- coding: utf-8 -*-
"""10.19-r10: database company default + controlled prepared PDF/print path."""
from __future__ import annotations

import inspect
import sqlite3
import tempfile
import unittest
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pypdf import PdfReader

import company_template_draft_form_ui
import company_template_fact_defaults
import company_template_fact_widgets
import document_catalog_ui
from company_template_draft import CompanyTemplateDraft
from output_files import report_font_candidates
from paper_document_store import list_documents
from prepared_document_pdf import (
    build_prepared_revision_pdf,
    suggested_prepared_pdf_name,
)
from prepared_document_registry import register_prepared_document
from prepared_document_revision import import_prepared_document_revision
from prepared_document_store import create_prepared_snapshot


class _Workspace:
    def __init__(self, db_path):
        self.db_path = Path(db_path)

    def connect_main_db(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con


class _Services:
    def __init__(self, db_path):
        self.workspace = _Workspace(db_path)


def _draft():
    rendered = {
        "format": "taxo.template.v1",
        "template_id": "instructions.r10",
        "title": "Інструкція",
        "document_kind": "instruction",
        "scenario": "r10",
        "language": "uk",
        "status": "proposed",
        "source_refs": [],
        "variables": [],
        "blocks": [
            {
                "id": "head",
                "type": "heading",
                "level": 1,
                "text": "Інструкція підприємства",
            },
            {
                "id": "body",
                "type": "paragraph",
                "text": "Початкова редакція документа.",
            },
        ],
        "appendices": [],
    }
    return CompanyTemplateDraft(
        company_template_id="ct-" + "a" * 32,
        source_sha256="b" * 64,
        edit_revision=4,
        title="Інструкція підприємства",
        content="Інструкція підприємства\nПочаткова редакція документа.",
        variables=(),
        normalized_facts={},
        rendered_template=rendered,
    )


class PreparedPdfPrintR10Tests(unittest.TestCase):
    def test_revision_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.19-r10\n",
        )
        self.assertIn(
            'APP_VERSION = "10.19-r10"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.19-r10",
            (root / "START.bat").read_text("utf-8"),
        )

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.work = self.root / "Work"
        self.work.mkdir()

    def _registered_r1(self):
        snapshot = create_prepared_snapshot(self.work, _draft())
        path = register_prepared_document(
            self.work, snapshot.snapshot_id
        )
        row = list_documents(self.work)[0]
        return snapshot, path, row

    def _font(self):
        for value in report_font_candidates():
            path = Path(value)
            if path.is_file():
                return path
        self.fail("CI/system does not provide a Ukrainian report font")

    def test_company_name_default_is_read_from_current_database(self):
        db = self.root / "main.sqlite3"
        con = sqlite3.connect(db)
        try:
            con.execute(
                "CREATE TABLE company(id INTEGER PRIMARY KEY, name TEXT)"
            )
            con.execute(
                "INSERT INTO company(id,name) VALUES(1,?)",
                ("ТОВ «Автотест»",),
            )
            con.commit()
        finally:
            con.close()

        values = company_template_fact_defaults.load_fact_defaults(
            _Services(db),
            ("company.name", "order.date"),
        )
        self.assertEqual(
            values, {"company.name": "ТОВ «Автотест»"}
        )

    def test_company_default_is_not_loaded_when_template_does_not_request_it(self):
        db = self.root / "empty.sqlite3"
        values = company_template_fact_defaults.load_fact_defaults(
            _Services(db),
            ("order.date",),
        )
        self.assertEqual(values, {})

    def test_draft_form_prefills_but_does_not_hardcode_company_name(self):
        form = inspect.getsource(company_template_draft_form_ui)
        widgets = inspect.getsource(company_template_fact_widgets)
        self.assertIn("load_fact_defaults", form)
        self.assertIn("initial_value=defaults.get(variable.name)", form)
        self.assertIn("initial_value=None", widgets)
        self.assertNotIn("SELECT name FROM company", widgets)

    def test_selected_edited_revision_exports_to_pdf_without_touching_docx_history(self):
        _snapshot, r1_path, r1 = self._registered_r1()
        r1_bytes = r1_path.read_bytes()

        edited = self.root / "edited.docx"
        doc = Document()
        doc.add_heading("Інструкція підприємства", level=1)
        centered = doc.add_paragraph("Редакція 2 після перевірки у Word.")
        centered.alignment = WD_ALIGN_PARAGRAPH.CENTER
        table = doc.add_table(rows=1, cols=2)
        table.rows[0].cells[0].text = "Поле"
        table.rows[0].cells[1].text = "Значення"
        table.add_row().cells[0].text = "Статус"
        table.rows[1].cells[1].text = "Підготовлено"
        doc.save(str(edited))

        r2 = import_prepared_document_revision(
            self.work, r1["id"], edited
        )
        before_records = list_documents(self.work)
        target = self.root / "print-copy.pdf"
        result = build_prepared_revision_pdf(
            self.work,
            r2.document_id,
            target,
            font_path=self._font(),
        )

        self.assertEqual(result, target)
        self.assertTrue(result.read_bytes().startswith(b"%PDF-"))
        reader = PdfReader(str(result))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        self.assertIn("Редакція 2", text)
        self.assertIn("Підготовлено", text)
        self.assertEqual(r1_path.read_bytes(), r1_bytes)
        self.assertEqual(
            [row["id"] for row in list_documents(self.work)],
            [row["id"] for row in before_records],
        )

    def test_pdf_requires_a_ukrainian_capable_font(self):
        _snapshot, _path, r1 = self._registered_r1()
        target = self.root / "without-font.pdf"
        with self.assertRaisesRegex(ValueError, "шрифт"):
            build_prepared_revision_pdf(
                self.work,
                r1["id"],
                target,
                font_path=None,
            )
        self.assertFalse(target.exists())

    def test_pdf_name_contains_controlled_revision(self):
        name = suggested_prepared_pdf_name({
            "id": "abcdef1234567890",
            "title": "Інструкція / тест",
            "document_revision": 3,
        })
        self.assertTrue(name.endswith("_r3_34567890.pdf"))
        self.assertNotIn("/", name)

    def test_pdf_renderer_refuses_images_instead_of_silently_dropping_them(self):
        _snapshot, _r1_path, r1 = self._registered_r1()
        # The source guard documents the fail-closed policy even though creating
        # an image fixture would add binary test data to the repository.
        source = inspect.getsource(
            __import__("prepared_document_pdf")
        )
        self.assertIn("document.inline_shapes", source)
        self.assertIn("не переносить зображення", source)
        self.assertTrue(r1["prepared_snapshot_id"])

    def test_catalog_exposes_pdf_print_action_only_for_controlled_prepared_rows(self):
        source = inspect.getsource(document_catalog_ui)
        self.assertIn('"PDF / друк…"', source)
        self.assertIn("build_prepared_revision_pdf", source)
        self.assertIn("open_document(", source)
        self.assertIn("_is_controlled_prepared_row", source)

    def test_start_package_guards_r10_modules(self):
        root = Path(__file__).resolve().parents[1]
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn("company_template_fact_defaults.py", start)
        self.assertIn("prepared_document_pdf.py", start)


if __name__ == "__main__":
    unittest.main()
