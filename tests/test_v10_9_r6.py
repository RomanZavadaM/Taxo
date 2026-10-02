# -*- coding: utf-8 -*-
import sqlite3
import unittest
from datetime import date
from pathlib import Path

import personnel_v91 as personnel
from feature_layers import feature_layer_ids
from v1096_personnel_balance import (
    FEATURE_VERSION,
    dated_absence_rows,
    employee_employed_on_row,
    norm_reduction_day_type,
)
from v91_features import PATTERN_2_2, PATTERN_CUSTOM, pattern_dates


class PersonnelBalanceR6Tests(unittest.TestCase):
    def test_r6_identity_and_runtime_registration_is_historical(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(FEATURE_VERSION, "10.9-r6")
        version = (root / "VERSION.txt").read_text("utf-8").strip()
        self.assertRegex(version, r"^Version: 10\.9-r(?:[6-9]|10)$")
        ids = feature_layer_ids()
        self.assertIn("v1096-personnel-balance", ids)
        self.assertGreaterEqual(ids.index("v1096-personnel-balance"), 0)
        current = version.removeprefix("Version: ")
        main = (root / "main.py").read_text("utf-8")
        self.assertIn(f'APP_VERSION = "{current}"', main)

    def test_start_package_requires_r6_runtime(self):
        root = Path(__file__).resolve().parents[1]
        start = (root / "START.bat").read_text("ascii")
        workflow = (root / ".github" / "workflows" / "source-test-archive.yml").read_text("utf-8")
        self.assertIn("v1096_personnel_balance.py", start)
        self.assertIn("v1096_personnel_balance.py", workflow)

    def test_weekend_and_rest_do_not_reduce_norm(self):
        self.assertIn("Вихідний", personnel.NONWORK_OVERRIDE_TYPES)
        self.assertIn("Відпочинок", personnel.NONWORK_OVERRIDE_TYPES)
        self.assertFalse(norm_reduction_day_type("Вихідний"))
        self.assertFalse(norm_reduction_day_type("Відпочинок"))
        self.assertTrue(norm_reduction_day_type("Основна щорічна відпустка"))
        self.assertTrue(norm_reduction_day_type("Оплачувана тимчасова непрацездатність"))

    def test_employment_check_is_historical_not_current_active_flag(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT '2026-01-10' employment_date,'2026-03-20' dismissal_date,0 active"
        ).fetchone()
        self.assertFalse(employee_employed_on_row(row, date(2026, 1, 9)))
        self.assertTrue(employee_employed_on_row(row, date(2026, 2, 15)))
        self.assertFalse(employee_employed_on_row(row, date(2026, 3, 21)))

    def test_dated_absence_does_not_use_today_active_preference(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.executescript(
            """
            CREATE TABLE employees(
                id INTEGER PRIMARY KEY,
                driver_id INTEGER,
                employment_date TEXT,
                dismissal_date TEXT,
                active INTEGER
            );
            CREATE TABLE employee_time_entries(
                id INTEGER PRIMARY KEY,
                employee_id INTEGER,
                work_date TEXT,
                day_type TEXT
            );
            """
        )
        con.execute("INSERT INTO employees VALUES(1,77,'2026-01-01','2026-03-31',0)")
        con.execute("INSERT INTO employees VALUES(2,77,'2026-06-01','',1)")
        con.execute("INSERT INTO employee_time_entries VALUES(1,1,'2026-02-10','Лікарняний')")
        con.execute("INSERT INTO employee_time_entries VALUES(2,2,'2026-06-10','Основна щорічна відпустка')")
        rows = dated_absence_rows(con, date(2026, 2, 1), date(2026, 6, 30), [77])
        self.assertEqual(rows[(77, "2026-02-10")]["employee_id"], 1)
        self.assertEqual(rows[(77, "2026-06-10")]["employee_id"], 2)

    def test_two_on_two_cycle_remains_anchored(self):
        rows = pattern_dates(date(2026, 10, 1), date(2026, 10, 10), PATTERN_2_2)
        self.assertEqual(rows, [date(2026,10,1),date(2026,10,2),date(2026,10,5),date(2026,10,6),date(2026,10,9),date(2026,10,10)])

    def test_custom_three_on_three_off_cycle(self):
        rows = pattern_dates(date(2026,10,1), date(2026,10,12), PATTERN_CUSTOM, work_days=3, rest_days=3)
        self.assertEqual(rows, [date(2026,10,1),date(2026,10,2),date(2026,10,3),date(2026,10,7),date(2026,10,8),date(2026,10,9)])


if __name__ == "__main__":
    unittest.main()
