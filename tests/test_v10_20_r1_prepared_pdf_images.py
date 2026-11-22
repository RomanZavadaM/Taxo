# -*- coding: utf-8 -*-
"""10.20-r1 functional slice: inline images survive prepared DOCX -> PDF."""
from __future__ import annotations

import io
import inspect
import tempfile
import unittest
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from PIL import Image as PillowImage
from pypdf import PdfReader

from company_template_draft import CompanyTemplateDraft
from output_files import report_font_candidates
from paper_document_store import list_documents
from prepared_document_pdf import build_prepared_revision_pdf
from prepared_document_pdf_images import ensure_supported_drawing_scope
from prepared_document_registry import register_prepared_document
from prepared_document_revision import import_prepared_document_revision
from prepared_document_store import create_prepared_snapshot


def _draft():
    rendered = {
        "format": "taxo.template.v1",
        "template_id": "images.r1",
        "title": "Документ із зображенням",
        "document_kind": "instruction",
        "scenario": "prepared-image-pdf",
        "language": "uk",
        "status": "proposed",
        "source_refs": [],
        "variables": [],
        "blocks": [
            {"id": "p", "type": "paragraph", "text": "Початкова редакція"},
        ],
        "appendices": [],
    }
    return CompanyTemplateDraft(
        company_template_id="ct-" + "a" * 32,
        source_sha256="b" * 64,
        edit_revision=1,
        title="Документ із зображенням",
        content="Початкова редакція",
        variables=(),
        normalized_facts={},
        rendered_template=rendered,
    )


def _png_bytes(width=96, height=48):
    stream = io.BytesIO()
    image = PillowImage.new("RGB", (width, height), (220, 80, 40))
    image.save(stream, format="PNG")
    return stream.getvalue()


def _pdf_image_count(path):
    reader = PdfReader(str(path))
    count = 0
    for page in reader.pages:
        resources = page.get("/Resources")
        if resources is None:
            continue
        resources = resources.get_object()
        xobjects = resources.get("/XObject")
        if xobjects is None:
            continue
        xobjects = xobjects.get_object()
        for item in xobjects.values():
            obj = item.get_object()
            if obj.get("/Subtype") == "/Image":
                count += 1
    return count


class PreparedPdfImagesR1Tests(unittest.TestCase):
    def test_revision_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.23-r10\n",
        )
        self.assertIn(
            'APP_VERSION = "10.23-r10"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.23-r10",
            (root / "START.bat").read_text("utf-8"),
        )

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.work = self.root / "Work"
        self.work.mkdir()

    def _font(self):
        for value in report_font_candidates():
            path = Path(value)
            if path.is_file():
                return path
        self.fail("No Ukrainian-capable report font found")

    def _registered(self):
        snapshot = create_prepared_snapshot(self.work, _draft())
        path = register_prepared_document(
            self.work, snapshot.snapshot_id
        )
        row = list_documents(self.work)[0]
        return snapshot, path, row

    def _import_docx(self, row, document, name="edited.docx"):
        target = self.root / name
        document.save(str(target))
        return import_prepared_document_revision(
            self.work, row["id"], target
        )

    def test_inline_body_image_is_present_in_pdf_and_history_is_unchanged(self):
        _snapshot, r1_path, r1 = self._registered()
        r1_bytes = r1_path.read_bytes()

        doc = Document()
        doc.add_paragraph("Текст перед зображенням")
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.add_run().add_picture(
            io.BytesIO(_png_bytes()), width=Inches(1.2)
        )
        doc.add_paragraph("Текст після зображення")
        r2 = self._import_docx(r1, doc)

        before = list_documents(self.work)
        pdf = self.root / "body-image.pdf"
        build_prepared_revision_pdf(
            self.work,
            r2.document_id,
            pdf,
            font_path=self._font(),
        )

        self.assertGreaterEqual(_pdf_image_count(pdf), 1)
        reader = PdfReader(str(pdf))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        self.assertIn("Текст перед зображенням", text)
        self.assertIn("Текст після зображення", text)
        self.assertEqual(r1_path.read_bytes(), r1_bytes)
        self.assertEqual(
            [row["id"] for row in list_documents(self.work)],
            [row["id"] for row in before],
        )

    def test_inline_image_inside_table_cell_is_present_in_pdf(self):
        _snapshot, _r1_path, r1 = self._registered()
        doc = Document()
        table = doc.add_table(rows=1, cols=2)
        table.cell(0, 0).text = "Логотип"
        paragraph = table.cell(0, 1).paragraphs[0]
        paragraph.add_run().add_picture(
            io.BytesIO(_png_bytes(64, 64)), width=Inches(0.6)
        )
        r2 = self._import_docx(r1, doc, "table-image.docx")
        pdf = self.root / "table-image.pdf"
        build_prepared_revision_pdf(
            self.work,
            r2.document_id,
            pdf,
            font_path=self._font(),
        )
        self.assertGreaterEqual(_pdf_image_count(pdf), 1)

    def test_header_image_remains_fail_closed(self):
        doc = Document()
        paragraph = doc.sections[0].header.paragraphs[0]
        paragraph.add_run().add_picture(
            io.BytesIO(_png_bytes()), width=Inches(0.7)
        )
        with self.assertRaisesRegex(ValueError, "колонтитулі"):
            ensure_supported_drawing_scope(doc)

    def test_floating_drawing_remains_fail_closed(self):
        doc = Document()
        run = doc.add_paragraph().add_run()
        run.add_picture(io.BytesIO(_png_bytes()), width=Inches(0.7))
        inline = doc.element.body.xpath(".//wp:inline")[0]
        inline.tag = inline.tag.replace("}inline", "}anchor")
        with self.assertRaisesRegex(ValueError, "плаваюче"):
            ensure_supported_drawing_scope(doc)

    def test_safety_limits_and_external_image_policy_are_explicit(self):
        import prepared_document_pdf_images as images
        source = inspect.getsource(images)
        self.assertLessEqual(images.MAX_INLINE_IMAGES, 100)
        self.assertLessEqual(images.MAX_IMAGE_BLOB_BYTES, 32 * 1024 * 1024)
        self.assertLessEqual(images.MAX_IMAGE_PIXELS, 40_000_000)
        self.assertIn('blip.get(qn("r:link"))', source)
        self.assertIn("Taxo не завантажує зовнішній вміст", source)

    def test_start_guards_image_renderer_module(self):
        root = Path(__file__).resolve().parents[1]
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn("prepared_document_pdf_images.py", start)


if __name__ == "__main__":
    unittest.main()
