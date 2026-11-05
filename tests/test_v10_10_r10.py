# -*- coding: utf-8 -*-
"""Regression: Ukrainian shift labels and report-only driver selection (10.10-r10)."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import load_workbook
import main


def report_database():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE drivers (
            id INTEGER PRIMARY KEY, active INTEGER,
            last_name TEXT, first_name TEXT, middle_name TEXT
        );
        CREATE TABLE worklog (
            id INTEGER PRIMARY KEY, driver_id INTEGER, work_date TEXT
        );
        CREATE TABLE company (id INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO drivers VALUES(1,1,'Перший','Водій','');
        INSERT INTO drivers VALUES(2,1,'Другий','Водій','');
        INSERT INTO company VALUES(1,'Тестове підприємство');
    """)
    return db


class DriverReportSelectionR10Tests(unittest.TestCase):
    def test_month_collection_filters_only_explicitly_selected_driver_ids(self):
        with patch.object(main, "db", side_effect=report_database), \
             patch.object(main, "driver_role_active_on", return_value=True), \
             patch.object(main, "_driver_role_mode", return_value="driver"), \
             patch.dict(main.__dict__, {"TAXO_NONWORK_OVERRIDE_TYPES": set()}):
            all_data = main.collect_monthly_shift_schedule(2026, 11)
            selected = main.collect_monthly_shift_schedule(2026, 11, driver_ids=[2])
            empty = main.collect_monthly_shift_schedule(2026, 11, driver_ids=[])
        self.assertEqual(sorted(row["id"] for row in all_data["drivers"]), [1, 2])
        self.assertEqual([row["id"] for row in selected["drivers"]], [2])
        self.assertEqual(empty["drivers"], [])

    def test_multisegment_uses_ukrainian_abbreviation(self):
        day = {"day_type": "Робота"}
        segs = [
            {"segment_no": 1, "start_time": "07:55", "end_time": "09:45"},
            {"segment_no": 2, "start_time": "12:30", "end_time": "15:30"},
            {"segment_no": 3, "start_time": "17:20", "end_time": "19:40"},
        ]
        cell = main._monthly_shift_cell(day, segs)
        self.assertEqual(cell, "07:55\n19:40\n3 част.")
        self.assertNotIn("3ч", cell)

    def test_excel_for_selected_drivers_only(self):
        with patch.object(main, "db", side_effect=report_database), \
             patch.object(main, "driver_role_active_on", return_value=True), \
             patch.object(main, "_driver_role_mode", return_value="driver"), \
             patch.dict(main.__dict__, {"TAXO_NONWORK_OVERRIDE_TYPES": set()}):
            with tempfile.TemporaryDirectory() as tmp:
                file = Path(tmp) / "selected.xlsx"
                main.export_monthly_shift_schedule_xlsx(2026, 11, file, driver_ids=[2])
                wb = load_workbook(file, read_only=True, data_only=True)
                try:
                    text = " ".join(str(v) for ws in wb for row in ws for v in (c.value for c in row) if v is not None)
                finally:
                    wb.close()
        self.assertIn("Другий Водій", text)
        self.assertNotIn("Перший Водій", text)


if __name__ == "__main__":
    unittest.main()
