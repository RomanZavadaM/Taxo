# -*- coding: utf-8 -*-
"""10.15-r3 — printable paper forms, catalog, and backup-safe location."""
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

import main
import safety_instructions_ui as brief
import paper_documents as paper

ROOT = Path(__file__).resolve().parents[1]


class PaperDocumentsR3Tests(unittest.TestCase):
    def test_version_and_live_controls(self):
        self.assertEqual(main.APP_VERSION, "10.15-r3")
        self.assertIn("Version: 10.15-r3", (ROOT / "VERSION.txt").read_text("utf-8"))
        start = (ROOT / "START.bat").read_text("utf-8")
        for filename in ("paper_documents.py", "paper_documents_ui.py", "driver_internship_ui.py"):
            self.assertIn(filename, start)
        instructions = (ROOT / "src/taxo/safety_instructions_ui.py").read_text("utf-8")
        self.assertIn("Створити комплект DOCX для друку", instructions)
        self.assertIn("Каталог документів…", instructions)
        operations = (ROOT / "src/taxo/operations_orders_ui.py").read_text("utf-8")
        self.assertIn("install_internship_tab(app, core, book)", operations)

    def test_briefing_complete_printable_material_preserves_people_and_text(self):
        prepared = brief.prepare_list(
            "БДР", "Передрейсовий (цільовий)", "09.11.2026",
            "Безпечний рух на маршруті",
            ["Водій Один", "Водій Два"],
            people_records=(
                {"id": 12, "name": "Водій Один", "personnel_no": "012"},
                {"id": 19, "name": "Водій Два", "personnel_no": "019"},
            ),
            program_text="1. Перевірити дорожні умови.\n2. Дотримуватися дистанції.",
            source_note="Наказ №975",
        )
        doc = paper.build_briefing_docx(prepared)
        self.assertEqual(len(doc.tables), 1)
        self.assertEqual(len(doc.tables[0].rows), 3)
        flattened = "\n".join(p.text for p in doc.paragraphs)
        self.assertIn("Перевірити дорожні умови", flattened)
        self.assertIn("ЛИСТ ОЗНАЙОМЛЕННЯ", flattened)
        tabletext = " ".join(cell.text for row in doc.tables[0].rows for cell in row.cells)
        self.assertIn("Водій Один", tabletext)
        self.assertIn("Водій Два", tabletext)
        self.assertIn("Підпис працівника", tabletext)
        self.assertNotIn("проведено", json.dumps(prepared, default=str).lower())
        with tempfile.TemporaryDirectory() as directory:
            first = paper.save_document(directory, doc, "Інструктаж", prepared["topic"],
                                        prepared["day"].isoformat(), "Водій Один, Водій Два")
            second = paper.save_document(directory, doc, "Інструктаж", prepared["topic"],
                                         prepared["day"].isoformat(), "Водій Один, Водій Два")
            self.assertNotEqual(first, second)
            self.assertTrue(first.is_file() and second.is_file())
            self.assertTrue(str(first).startswith(str(Path(directory) / "Data")))
            found = paper.list_documents(directory, "Безпечний")
            self.assertEqual(len(found), 2)
            self.assertFalse(any(row["paper_signed"] for row in found))
            self.assertEqual(paper.document_path(directory, found[0]), second)

    def test_internship_form_contains_regulatory_sections_without_auto_admission(self):
        doc = paper.build_training_docx({
            "driver": "Стажист Один", "instructor": "Наставник Два",
            "vehicle": "Автобус АА0000АА", "training_kind": "Контрольна поїздка",
            "hours": "", "order": "№17 від 09.11.2026",
        })
        text = "\n".join(p.text for p in doc.paragraphs)
        for section in paper.TRAINING_SECTIONS:
            self.assertIn(section, text)
        self.assertIn("Наставник Два", text)
        self.assertIn("Автобус АА0000АА", text)
        self.assertIn("Допустити / не допустити", text)
        self.assertEqual(len(doc.tables), 3)
        self.assertEqual(len(doc.tables[0].rows), 5)
        self.assertIn("Підпис інструктора", doc.tables[0].rows[0].cells[-1].text)
        with tempfile.TemporaryDirectory() as directory:
            target = paper.save_document(directory, doc, "Стажування", "Контрольна поїздка",
                                         date(2026, 11, 9).isoformat(), "Стажист Один")
            self.assertTrue(target.exists())
            rows = paper.list_documents(directory, "Стажист")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["kind"], "Стажування")

    def test_catalog_blocks_path_traversal_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertRaises(ValueError, paper.document_path, directory,
                              {"file": "../secret.docx"})
            self.assertRaises(ValueError, paper.document_path, directory,
                              {"file": "/absolute.docx"})
            self.assertEqual(paper.list_documents(directory), [])


if __name__ == "__main__":
    unittest.main()
