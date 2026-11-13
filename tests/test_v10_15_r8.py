# -*- coding: utf-8 -*-
"""10.15-r8 — відокремлення UI-звіту документів ТЗ від main.py."""
from __future__ import annotations

import inspect
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

import main
import vehicle_documents_report_ui as report_ui

ROOT = Path(__file__).resolve().parents[1]


class VehicleDocumentReportSeparationR8Tests(unittest.TestCase):
    def test_version_and_start_require_new_module(self):
        self.assertIn(main.APP_VERSION, ("10.15-r8", "10.15-r9", "10.15-r10", "10.16-r1", "10.16-r2", "10.16-r3", "10.16-r4", "10.16-r5", "10.16-r6", "10.16-r7", "10.16-r8", "10.16-r9", "10.16-r10", "10.17-r1", "10.17-r2", "10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6", "10.17-r7", "10.17-r8", "10.17-r9", "10.17-r10", "10.18-r1", "10.18-r2", "10.18-r3", "10.18-r4", "10.18-r5"))
        self.assertEqual((ROOT / "VERSION.txt").read_text("utf-8"), "Version: " + main.APP_VERSION + "\n")
        start = (ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("vehicle_documents_report_ui.py", start)

    def test_report_date_parser_keeps_existing_contract(self):
        self.assertEqual(report_ui.parse_report_date("11.11.2026"), date(2026, 11, 11))
        with self.assertRaisesRegex(ValueError, "ДД.ММ.РРРР"):
            report_ui.parse_report_date("2026-11-11")

    def test_report_snapshot_keeps_filter_and_vehicle_summary(self):
        rows = [
            {"vehicle_id": 1, "overall": "Проблема", "rank": 1},
            {"vehicle_id": 1, "overall": "Проблема", "rank": 3},
            {"vehicle_id": 2, "overall": "Увага", "rank": 2},
            {"vehicle_id": 3, "overall": "Актуально", "rank": 3},
        ]
        visible, summary = report_ui.report_snapshot(rows, only_issues=True)
        self.assertEqual([row["rank"] for row in visible], [1, 2])
        self.assertIn("Авто: 3", summary)
        self.assertIn("Проблема: 1", summary)
        self.assertIn("Увага: 1", summary)
        self.assertIn("Актуально: 1", summary)
        self.assertIn("Позицій у таблиці: 2", summary)

    def test_main_keeps_only_thin_report_adapter(self):
        source = inspect.getsource(main.App.show_vehicle_documents_report)
        self.assertIn("open_vehicle_documents_report", source)
        self.assertNotIn("vehicle_document_report_rows", source)
        app = object.__new__(main.App)
        with mock.patch.object(main, "open_vehicle_documents_report", return_value="opened") as opener:
            result = main.App.show_vehicle_documents_report(app)
        self.assertIsNone(result)
        args, kwargs = opener.call_args
        self.assertIs(args[0], app)
        self.assertIs(args[1], main.db)
        self.assertEqual(args[2], main.OUTPUT_DIR)
        self.assertIs(kwargs["calendar_button"], main.calendar_button)
        self.assertIs(kwargs["fit_window_to_screen"], main.fit_window_to_screen)
        self.assertIs(kwargs["write_output_file"], main.write_output_file)

    def test_report_module_does_not_import_main(self):
        source = (ROOT / "src/taxo/vehicle_documents_report_ui.py").read_text("utf-8")
        self.assertNotIn("import main", source)


if __name__ == "__main__":
    unittest.main()
