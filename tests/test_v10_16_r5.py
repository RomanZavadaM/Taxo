# -*- coding: utf-8 -*-
"""10.16-r5 — формування документа інструктажу відокремлене від Tk-UI."""
from __future__ import annotations

import inspect
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

import main
import paper_document_store
import safety_instruction_document_service as instruction_documents
import safety_instructions_ui

ROOT = Path(__file__).resolve().parents[1]


class SafetyInstructionDocumentServiceR5Tests(unittest.TestCase):
    def test_version_and_start_require_instruction_document_service(self):
        self.assertIn(main.APP_VERSION, ("10.16-r5", "10.16-r6", "10.16-r7", "10.16-r8", "10.16-r9", "10.16-r10", "10.17-r1", "10.17-r2"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        start = (ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("safety_instruction_document_service.py", start)

    def test_instruction_ui_delegates_document_work_to_service(self):
        source = inspect.getsource(safety_instructions_ui)
        self.assertIn(
            "import safety_instruction_document_service as instruction_documents",
            source,
        )
        self.assertNotIn("import paper_documents as paperwork", source)
        self.assertNotIn("import paper_document_store as document_store", source)
        self.assertIn("instruction_documents.save_briefing_document(", source)
        self.assertIn("instruction_documents.open_briefing_document(", source)

    def test_service_preserves_existing_paper_catalog_contract(self):
        prepared = {
            "topic": "Безпека руху",
            "day": date(2026, 11, 11),
            "people": ("Іваненко Іван", "Петренко Петро"),
            "program_text": "Перевірена програма",
        }
        document = object()
        target = object()
        workspace_root = object()

        with mock.patch.object(
            instruction_documents.paperwork,
            "build_briefing_docx",
            return_value=document,
        ) as build_docx, mock.patch.object(
            instruction_documents.document_store,
            "save_document",
            return_value=target,
        ) as save_document:
            result = instruction_documents.save_briefing_document(
                workspace_root,
                prepared,
            )

        self.assertIs(result, target)
        build_docx.assert_called_once_with(prepared)
        save_document.assert_called_once_with(
            workspace_root,
            document,
            "Інструктаж",
            "Безпека руху",
            "2026-11-11",
            "Іваненко Іван, Петренко Петро",
        )

    def test_service_does_not_store_empty_program(self):
        prepared = {
            "topic": "Тема",
            "day": date(2026, 11, 11),
            "people": ("Працівник",),
            "program_text": "   ",
        }
        with mock.patch.object(
            instruction_documents.document_store,
            "save_document",
        ) as save_document:
            with self.assertRaisesRegex(ValueError, "Текст програми порожній"):
                instruction_documents.save_briefing_document(object(), prepared)
        save_document.assert_not_called()

    def test_paper_catalog_prefers_later_append_when_timestamps_match(self):
        records = [
            {"id": "older", "created_at": "2026-11-11T12:00:00+00:00"},
            {"id": "newer", "created_at": "2026-11-11T12:00:00+00:00"},
        ]
        with mock.patch.object(paper_document_store, "_index", return_value=records):
            result = paper_document_store.list_documents(object())
        self.assertEqual([row["id"] for row in result], ["newer", "older"])

    def test_open_delegates_to_existing_cross_platform_handler(self):
        target = object()
        with mock.patch.object(
            instruction_documents.document_store,
            "open_file",
            return_value="opened",
        ) as open_file:
            result = instruction_documents.open_briefing_document(target)
        self.assertEqual(result, "opened")
        open_file.assert_called_once_with(target)


if __name__ == "__main__":
    unittest.main()
