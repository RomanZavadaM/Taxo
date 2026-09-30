# -*- coding: utf-8 -*-
import sqlite3
import unittest
from datetime import date, timedelta

import vehicle_maintenance as maint


class StoIRR5Tests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.executescript(
            "CREATE TABLE vehicles (id INTEGER PRIMARY KEY, name TEXT, plate TEXT, make_model TEXT, active INTEGER DEFAULT 1);"
            "CREATE TABLE vehicle_odometer_readings (id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle_id INTEGER NOT NULL, reading_km INTEGER, reading_at TEXT, source_type TEXT, worklog_id INTEGER, notes TEXT DEFAULT '');"
            "INSERT INTO vehicles(id,name,plate,make_model,active) VALUES(1,'Bus','BC0001AA','Test Bus',1);"
        )
        maint.ensure_schema_on_connection(self.con)

    def tearDown(self):
        self.con.close()

    def test_no_history_means_no_forecast(self):
        plan = maint.vehicle_plan(self.con, 1)
        self.assertIsNone(plan["average_daily_km"])
        self.assertEqual(plan["to1"]["status"], "unknown")
        self.assertIsNone(plan["to1"]["forecast_date"])

    def test_average_and_due_date(self):
        start = date.today() - timedelta(days=20)
        self.con.execute("INSERT INTO vehicle_odometer_readings(vehicle_id,reading_km,reading_at,source_type) VALUES(1,10000,?,'waybill')", (start.isoformat(),))
        self.con.execute("INSERT INTO vehicle_odometer_readings(vehicle_id,reading_km,reading_at,source_type) VALUES(1,11000,?,'waybill')", (date.today().isoformat(),))
        maint.record_event(self.con, 1, maint.MAINTENANCE_TO1, start.isoformat(), odometer_km=10000)
        self.con.commit()
        plan = maint.vehicle_plan(self.con, 1)
        self.assertAlmostEqual(plan["average_daily_km"], 50.0, places=1)
        self.assertEqual(plan["to1"]["due"]["remaining_km"], 4000)
        self.assertEqual(plan["to1"]["forecast_date"], date.today() + timedelta(days=80))

    def test_repair_request_lifecycle(self):
        request_id = maint.create_repair_request(self.con, 1, "Сторонній шум у передній підвісці", priority="high", reporter="водій")
        self.con.commit()
        rows = maint.repair_requests(self.con, 1, include_closed=False)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], maint.REQUEST_OPEN)
        maint.update_repair_request(self.con, request_id, status=maint.REQUEST_IN_PROGRESS, assignee="механік")
        self.con.commit()
        self.assertEqual(maint.repair_requests(self.con, 1)[0]["assignee"], "механік")
        maint.update_repair_request(self.con, request_id, status=maint.REQUEST_CLOSED, resolution="усунуто")
        self.con.commit()
        self.assertEqual(len(maint.repair_requests(self.con, 1, include_closed=False)), 0)
        self.assertTrue(maint.repair_requests(self.con, 1)[0]["closed_at"])


if __name__ == "__main__":
    unittest.main()
