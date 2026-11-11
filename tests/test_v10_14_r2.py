# -*- coding: utf-8 -*-
"""10.14-r2: real DOCX / PDF / every JPG page, without office software."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import main
from docx import Document
from reportlab.pdfgen import canvas

from order_pdf_workflow import generate_order_formats, open_order_format


class FakeOrders:
    TYPE_VEHICLE_ASSIGNMENT = "vehicle_assignment"
    @staticmethod
    def display_day(value):
        return str(value)
    @staticmethod
    def order_preview_text(order, assignments=(), entities=(), company=None, control_name=""):
        return (
            "Н А К А З\nпо Тестове підприємство\n\n"
            "09.11.2026 № 4-К\n\nН А К А З У Ю:\n"
            "1. Призначити відповідальним.\n"
            "2. Закріпити автобус за двома водіями.\n\n"
            "Директор _______________ Тест"
        )

    @staticmethod
    def export_order_pdf(path, order, assignments=(), company=None,
                         control_name="", font_path=None):
        doc = canvas.Canvas(str(path))
        for i in range(3):
            doc.drawString(30, 740, "Order page %d" % (i + 1))
            doc.showPage()
        doc.save()


def fake_core(output, saved=None, cancel=False):
    def write(writer, path, **_kwargs):
        if cancel:
            return None
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        writer(path)
        return path
    return SimpleNamespace(
        OUTPUT_DIR=output, Path=Path,
        report_font_candidates=lambda: [],
        write_output_file=write,
        open_document=Mock(),
        open_external=Mock(),
        messagebox=SimpleNamespace(showwarning=Mock(), showerror=Mock()),
    )


class OrderFormatsR2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        self.order = {
            "order_no":"4-К","order_date":"09.11.2026",
            "order_type":"generic","place":"Львів",
            "subject":"Про закріплення",
            "preamble":"Для виконання виробничих завдань",
            "body_text":"1. Закріпити автобус за двома водіями."
        }
        self.core = fake_core(self.output)

    def test_current_version_and_start_guard(self):
        self.assertIn(main.APP_VERSION, ("10.14-r2", "10.14-r3", "10.14-r4", "10.14-r5", "10.14-r6", "10.14-r7", "10.14-r8", "10.14-r9", "10.14-r10", "10.15-r1", "10.15-r2", "10.15-r3", "10.15-r4", "10.15-r5", "10.15-r7", "10.15-r8", "10.15-r9", "10.15-r10", "10.16-r1", "10.16-r2", "10.16-r3", "10.16-r4", "10.16-r5", "10.16-r6", "10.16-r7", "10.16-r8", "10.16-r9"))
        self.assertIn(main.APP_VERSION, Path("VERSION.txt").read_text(encoding="utf-8"))
        start = Path("START.bat").read_text(encoding="utf-8")
        self.assertIn("order_pdf_workflow.py", start)
        self.assertIn("order_document_formats.py", start)

    def test_word_pdf_three_jpg_pages_and_no_overwrite(self):
        first = generate_order_formats(
            self.core, FakeOrders, self.order, formats=("docx", "pdf", "jpg")
        )
        self.assertEqual(set(first), {"docx", "pdf", "jpg"})
        self.assertEqual(len(first["jpg"]), 3)
        for paths in first.values():
            self.assertTrue(all(p.exists() and p.stat().st_size for p in paths))
        word = Document(first["docx"][0])
        body = "\n".join(p.text for p in word.paragraphs)
        self.assertIn("Н А К А З У Ю", body)
        self.assertIn("двома водіями", body)
        self.assertTrue(first["pdf"][0].read_bytes().startswith(b"%PDF"))
        from PIL import Image
        for jpg in first["jpg"]:
            with Image.open(jpg) as im:
                self.assertEqual(im.format, "JPEG")
                self.assertGreater(im.width, 500)
        preserved = first["docx"][0].read_bytes()
        again = generate_order_formats(
            self.core, FakeOrders, self.order, formats=("docx", "pdf", "jpg")
        )
        self.assertNotEqual(first["docx"][0], again["docx"][0])
        self.assertNotEqual(first["pdf"][0], again["pdf"][0])
        self.assertEqual(first["docx"][0].read_bytes(), preserved)

    def test_jpg_without_selected_pdf_does_not_leave_temporary_pdf(self):
        output = generate_order_formats(
            self.core, FakeOrders, self.order, formats=("jpg",)
        )
        self.assertEqual(len(output["jpg"]), 3)
        self.assertEqual(list(self.output.glob("*.pdf")), [])

    def test_single_word_and_cancel_do_not_claim_fake_file(self):
        result = generate_order_formats(
            self.core, FakeOrders, self.order, formats=("docx",)
        )
        self.assertEqual(set(result), {"docx"})
        cancelled = fake_core(self.output, cancel=True)
        self.assertEqual(
            generate_order_formats(cancelled, FakeOrders, self.order, formats=("pdf",)),
            {},
        )

    def test_preview_and_os_app_are_separate_actions(self):
        path = self.output / "test.docx"
        path.write_bytes(b"demo")
        self.assertEqual(open_order_format(self.core, [path], None), path)
        self.core.open_document.assert_called_once()
        self.assertEqual(
            open_order_format(self.core, [path], None, external=True), path
        )
        self.core.open_external.assert_called_once_with(path)

    def test_existing_order_entries_and_format_choices_remain_visible(self):
        text = Path("src/taxo/operations_orders_ui.py").read_text(encoding="utf-8")
        text += Path("src/taxo/order_register_ui.py").read_text(encoding="utf-8")
        text += Path("src/taxo/order_editor_ui.py").read_text(encoding="utf-8")
        text += Path("src/taxo/order_preview_ui.py").read_text(encoding="utf-8")
        for required in (
            "preview_order(created_order)", "Переглянути / друк",
            "Сформувати PDF / друк", "Створити DOCX", "Створити PDF",
            "Створити JPG", "Створити все", "Перегляд ",
            "Відкрити у програмі:", "generate_order_formats(",
        ):
            self.assertIn(required, text)

    def test_no_agpl_pdf_library_added(self):
        requirement_files = ["requirements.txt", "requirements-win7.txt"]
        for req in requirement_files:
            lines = Path(req).read_text(encoding="utf-8").lower().splitlines()
            self.assertFalse(any(line.startswith(("pymupdf", "fitz")) for line in lines))


if __name__ == "__main__":
    unittest.main()
