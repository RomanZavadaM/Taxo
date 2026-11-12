# -*- coding: utf-8 -*-
"""10.16-r6 — документи стажування відокремлені від Tk-UI."""
from __future__ import annotations

import inspect
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

import driver_internship_document_service as internship_documents
import driver_internship_ui
import main

ROOT = Path(__file__).resolve().parents[1]


class DriverInternshipDocumentServiceR6Tests(unittest.TestCase):
    def test_version_and_start_require_internship_document_service(self):
        self.assertIn(main.APP_VERSION, ("10.16-r6", "10.16-r7", "10.16-r8", "10.16-r9", "10.16-r10", "10.17-r1", "10.17-r2", "10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6", "10.17-r7", "10.17-r8", "10.17-r9", "10.17-r10", "10.18-r1"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        start = (ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("driver_internship_document_service.py", start)

    def test_internship_ui_delegates_document_work_to_service(self):
        source = inspect.getsource(driver_internship_ui)
        self.assertIn(
            "import driver_internship_document_service as internship_documents",
            source,
        )
        self.assertNotIn("import paper_documents as paperwork", source)
        self.assertNotIn("import paper_document_store as document_store", source)
        self.assertIn("internship_documents.save_internship_document(", source)
        self.assertIn("internship_documents.open_internship_document(", source)

    def test_service_preserves_existing_paper_catalog_contract(self):
        data = {
            "driver": "Стажист Один",
            "personnel_no": "001",
            "instructor": "Наставник Два",
            "vehicle": "Автобус AA0000AA",
            "training_kind": "Контрольна поїздка",
            "order": "12 від 11.11.2026",
            "period": "11.11.2026 — 12.11.2026",
            "hours": "8",
            "licence": "ABC 123456, D",
            "experience_since": "2020",
            "driver_id": 1,
            "vehicle_id": 5,
        }
        document = object()
        target = object()
        workspace_root = object()

        with mock.patch.object(
            internship_documents.paperwork,
            "build_training_docx",
            return_value=document,
        ) as build_docx, mock.patch.object(
            internship_documents.document_store,
            "save_document",
            return_value=target,
        ) as save_document, mock.patch.object(
            internship_documents,
            "date",
        ) as mocked_date:
            mocked_date.today.return_value = date(2026, 11, 11)
            result = internship_documents.save_internship_document(
                workspace_root,
                data,
            )

        self.assertIs(result, target)
        build_docx.assert_called_once_with(data)
        save_document.assert_called_once_with(
            workspace_root,
            document,
            "Стажування",
            "Контрольна поїздка: Стажист Один",
            "2026-11-11",
            "Стажист Один",
        )

    def test_open_delegates_to_existing_cross_platform_handler(self):
        target = object()
        with mock.patch.object(
            internship_documents.document_store,
            "open_file",
            return_value="opened",
        ) as open_file:
            result = internship_documents.open_internship_document(target)
        self.assertEqual(result, "opened")
        open_file.assert_called_once_with(target)


if __name__ == "__main__":
    unittest.main()
