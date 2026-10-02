# -*- coding: utf-8 -*-
import sqlite3
import unittest
from datetime import date
from pathlib import Path

import vehicle_maintenance as maint
from v1097_stoir_odometer import (
    FEATURE_VERSION,
    average_daily_mileage,
    latest_odometer,
    vehicle_plan,
)


class StoirOdometerSafetyR7Tests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys=ON")
        self.con.executescript(
            """
            CREATE TABLE vehicles(
                id INTEGER PRIMARY KEY,
                name TEXT,
                plate TEXT,
                make_model TEXT,
                active INTEGER DEFAULT 1
            );
            CREATE TABLE vehicle_odometer_readings(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                driver_id INTEGER,
                worklog_id INTEGER,
                work_date TEXT,
                reading_km INTEGER,
                reading_at TEXT,
                source_type TEXT,
                source_id INTEGER,
                notes TEXT
            );
            INSERT INTO vehicles(id,name,plate,active) VALUES(1,'Автобус','BC0001AA',1);
            """
        )

    def tearDown(self):
        self.con.close()

    def add_reading(self, km, *, reading_at="", work_date="", source_type="manual", source_id=None):
        self.con.execute(
            """INSERT INTO vehicle_odometer_readings(
                   vehicle_id,work_date,reading_km,reading_at,source_type,source_id
               ) VALUES(1,?,?,?,?,?)""",
            (work_date, km, reading_at, source_type, source_id),
        )

    def test_identity(self):
        self.assertEqual(FEATURE_VERSION, "10.9-r7")

    def test_work_date_is_fallback_when_reading_at_is_blank(self):
        self.add_reading(1000, reading_at="2026-09-01T08:00:00")
        self.add_reading(1200, work_date="2026-09-03", source_type="waybill", source_id=10)
        row = latest_odometer(self.con, 1)
        self.assertEqual(row["reading_km"], 1200)
        self.assertEqual(row["effective_date"], date(2026, 9, 3))
        self.assertEqual(row["source_type"], "waybill")

    def test_newer_waybill_fact_wins_over_older_timed_manual_reading(self):
        self.add_reading(5000, reading_at="2026-09-10T18:00:00", source_type="manual")
        self.add_reading(5300, work_date="2026-09-11", source_type="waybill", source_id=44)
        row = latest_odometer(self.con, 1)
        self.assertEqual((row["reading_km"], row["source_id"]), (5300, 44))

    def test_average_uses_work_date_fallback_and_is_anchored_to_newest_fact(self):
        # These points are intentionally historical relative to the system date.
        # A lookback anchored to date.today() would incorrectly discard them.
        self.add_reading(1000, work_date="2026-01-01")
        self.add_reading(2000, work_date="2026-01-11")
        self.assertAlmostEqual(average_daily_mileage(self.con, 1, lookback_days=60), 100.0)

    def test_single_obvious_spike_does_not_dominate_average(self):
        self.add_reading(1000, work_date="2026-09-01")
        self.add_reading(1100, work_date="2026-09-02")
        self.add_reading(1200, work_date="2026-09-03")
        self.add_reading(11200, work_date="2026-09-04")
        self.assertAlmostEqual(average_daily_mileage(self.con, 1), 100.0)

    def test_forecast_starts_from_latest_reliable_odometer_date(self):
        maint.ensure_schema_on_connection(self.con)
        self.add_reading(1000, work_date="2026-09-01")
        self.add_reading(2000, work_date="2026-09-11")
        maint.record_event(self.con, 1, maint.MAINTENANCE_TO1, "2026-09-01", odometer_km=1000)
        plan = vehicle_plan(self.con, 1)
        self.assertEqual(plan["current_odometer_date"], date(2026, 9, 11))
        self.assertAlmostEqual(plan["average_daily_km"], 100.0)
        # Passenger/bus default: 1000 + 5000 => 6000 due; 4000 km remain = 40 days.
        self.assertEqual(plan["to1"]["forecast_date"], date(2026, 10, 21))

    def test_r7_does_not_silently_make_to2_reset_to1(self):
        maint.ensure_schema_on_connection(self.con)
        self.add_reading(9000, work_date="2026-09-01")
        self.add_reading(10000, work_date="2026-09-11")
        maint.record_event(self.con, 1, maint.MAINTENANCE_TO1, "2026-08-01", odometer_km=6000)
        maint.record_event(self.con, 1, maint.MAINTENANCE_TO2, "2026-09-05", odometer_km=9500)
        plan = vehicle_plan(self.con, 1)
        self.assertEqual(plan["to1"]["last_event"]["odometer_km"], 6000)
        self.assertEqual(plan["to1"]["due"]["due_odometer_km"], 11000)
        self.assertEqual(plan["to2"]["last_event"]["odometer_km"], 9500)

    def test_start_package_will_require_r7_runtime(self):
        root = Path(__file__).resolve().parents[1]
        start = (root / "START.bat").read_text("ascii")
        pack = (root / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn('if not exist "src\\taxo\\v1097_stoir_odometer.py" goto :package_incomplete', start)
        self.assertIn("v1097_stoir_odometer.py", pack)


if __name__ == "__main__":
    unittest.main()
