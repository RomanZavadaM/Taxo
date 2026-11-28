# -*- coding: utf-8 -*-
"""10.25-r6 owner-acceptance fixes for briefing text, lines and paper form."""
from __future__ import annotations

import inspect
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "taxo"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import briefing_event_ui
import briefing_preparation
import briefing_program_sources as sources
import paper_documents
import safety_templates


class BriefingOwnerAcceptanceR6Test(unittest.TestCase):
    def test_program_lines_are_human_readable(self):
        self.assertEqual(
            sources.program_line("БДР", "Періодичний (повторний)"),
            sources.LINE_ANNUAL,
        )
        self.assertEqual(
            sources.program_line("Охорона праці", "Вступний"),
            sources.LINE_INITIAL,
        )
        self.assertEqual(
            sources.program_line("БДР", "Позаплановий (спеціальний)"),
            sources.LINE_EVENT,
        )
        self.assertEqual(
            sources.program_line("Охорона праці", "Цільовий"),
            sources.LINE_TARGET,
        )

    def test_year_cycle_has_four_ready_topics_for_bdr_and_osh(self):
        bdr = safety_templates.templates_for(
            "БДР", "Періодичний (повторний)"
        )
        osh = safety_templates.templates_for("Охорона праці", "Повторний")
        self.assertEqual(
            {row["id"] for row in bdr if row["id"].startswith("bdr_year_q")},
            {"bdr_year_q1", "bdr_year_q2", "bdr_year_q3", "bdr_year_q4"},
        )
        self.assertEqual(
            {row["id"] for row in osh if row["id"].startswith("osh_year_q")},
            {"osh_year_q1", "osh_year_q2", "osh_year_q3", "osh_year_q4"},
        )

    def test_built_in_sources_still_work_without_installed_library(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows, notes = sources.source_options(
                Path(tmp),
                "10.25-r6",
                "БДР",
                "Періодичний (повторний)",
            )
        self.assertTrue(rows)
        self.assertTrue(any(row.origin == "Taxo" for row in rows))
        self.assertTrue(any("I квартал" in row.topic for row in rows))
        self.assertIsInstance(notes, tuple)

    def test_prepared_payload_keeps_approval_text(self):
        prepared = briefing_preparation.prepare_list(
            "БДР",
            "Періодичний (повторний)",
            "28.11.2026",
            "Контрольна тема",
            ["Іваненко Іван"],
            program_text="1. Основний текст.",
            template_id="bp-test:r2",
            source_note="Внутрішня програма",
            approved_by="Керівник підприємства Іван Іваненко",
        )
        self.assertEqual(
            prepared["approved_by"],
            "Керівник підприємства Іван Іваненко",
        )

    def test_briefing_docx_has_approval_revision_and_event_block(self):
        prepared = {
            "direction": "БДР",
            "kind": "Позаплановий (спеціальний)",
            "day": date(2026, 11, 28),
            "topic": "Небезпечна ділянка",
            "reason": (
                "Перекриття дороги.\n\n"
                "Конкретний випадок / додатково розглянути:\n"
                "Об'їзд через вузьку вулицю."
            ),
            "program_text": "1. Базова програма.\n2. Дії водія.",
            "template_id": "bp-test:r3",
            "source_note": "Внутрішня програма підприємства",
            "approved_by": "Директор Петро Петренко",
            "people": ("Іваненко Іван",),
            "people_records": (
                {"name": "Іваненко Іван", "personnel_no": "17"},
            ),
        }
        doc = paper_documents.build_briefing_docx(prepared)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        self.assertIn("ЗАТВЕРДЖЕНО", text)
        self.assertIn("Директор Петро Петренко", text)
        self.assertIn("Редакція програми: bp-test:r3", text)
        self.assertIn("Конкретний випадок / підстава", text)
        self.assertIn("Об'їзд через вузьку вулицю", text)

    def test_event_ui_has_separate_case_addendum_without_breaking_reason_var(self):
        source = inspect.getsource(briefing_event_ui)
        self.assertIn("Конкретний випадок / що додатково розглянути", source)
        self.assertIn("_taxo_event_details_text", source)
        self.assertIn("_taxo_event_reason_var", source)

    def test_start_package_requires_new_bridge(self):
        start = (ROOT / "START.bat").read_text(
            encoding="utf-8", errors="replace"
        )
        self.assertIn("briefing_program_sources.py", start)


if __name__ == "__main__":
    unittest.main()
