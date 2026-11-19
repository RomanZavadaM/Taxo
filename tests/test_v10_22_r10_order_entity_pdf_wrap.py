# -*- coding: utf-8 -*-
"""Regression for order PDF appendix with long employee names, roles and VINs."""
import unittest
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Table, TableStyle


class OrderEntityPdfTableWrapTests(unittest.TestCase):
    def test_production_pdf_uses_wrapping_flowables_in_every_cell(self):
        text = (
            Path(__file__).resolve().parents[1] /
            "src" / "taxo" / "v1073_features.py"
        ).read_text("utf-8")
        self.assertIn('wordWrap="CJK"', text)
        self.assertIn("return Paragraph(xml_escape(str(value or", text)
        self.assertIn("cell(view[\"role\"])", text)
        self.assertIn("cell(view[\"display\"])", text)
        self.assertIn("cell(view[\"identifier\"])", text)
        self.assertIn("repeatRows=1", text)

    def test_long_cells_in_a4_width_wrap_into_rows(self):
        style = ParagraphStyle(
            "OrderLongCell", fontName="Helvetica", fontSize=8.1,
            leading=10.3, wordWrap="CJK",
        )
        data = [[
            Paragraph(escape(value), style)
            for value in ("1", "Працівник",
                "Відповідальний / виконавець за контроль технічного стану",
                "Завада Роман Михайлович", "VIN Y7FA0792380004945")
        ]]
        table = Table(data, colWidths=[10*mm, 18*mm, 38*mm, 54*mm, 45*mm])
        table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), .4, colors.black),
            ("LEFTPADDING", (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
        ]))
        width, height = table.wrap(165*mm, 240*mm)
        self.assertLessEqual(width, 165*mm + .01)
        self.assertGreater(height, 10.3)
        self.assertTrue(all(isinstance(cell, Paragraph) for cell in data[0]))


if __name__ == "__main__":
    unittest.main()
