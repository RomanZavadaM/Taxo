# -*- coding: utf-8 -*-
import inspect
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from pypdf import PdfReader
from reportlab.pdfgen import canvas

import v9_release


class _NoFontCore:
    @staticmethod
    def report_font_candidates():
        return []


class TaxoV90Tests(unittest.TestCase):
    def test_report_date_parser_and_datetime_keep_selected_date(self):
        chosen = v9_release.parse_report_date("17.09.2026")
        self.assertEqual(chosen, date(2026, 9, 17))
        stamp = v9_release.report_datetime(
            chosen, datetime(2026, 9, 20, 14, 35, 27, 999999)
        )
        self.assertEqual(stamp, datetime(2026, 9, 17, 14, 35, 27))

    def test_work_analysis_pdf_receives_formation_date_stamp(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "analysis.pdf"
            c = canvas.Canvas(str(target))
            c.drawString(72, 760, "Taxo 9.0")
            c.showPage()
            c.save()

            v9_release.stamp_work_analysis_pdf(
                _NoFontCore, target, date(2026, 9, 17)
            )
            doc = PdfReader(target)
            text = "\n".join((page.extract_text() or "") for page in doc.pages)
            self.assertIn("17.09.2026", text)
            self.assertEqual(len(doc.pages), 1)

    def test_ui_exposes_driver_and_report_date_controls(self):
        source = inspect.getsource(v9_release.install)
        self.assertIn('text="Водій:"', source)
        self.assertIn('text="Дата формування:"', source)
        self.assertIn('text="Дата формування"', source)
        self.assertIn('<<ComboboxSelected>>', source)
        self.assertIn('Сформувати й відкрити PDF', source)


if __name__ == "__main__":
    unittest.main()
