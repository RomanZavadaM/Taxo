# -*- coding: utf-8 -*-
import re
import sqlite3
import unittest
from datetime import date, datetime
from pathlib import Path

import military_transport_statement as statement
import v1083_features as r3


class StatementDateNormalizationTests(unittest.TestCase):
    def test_accepts_taxo_display_date(self):
        self.assertEqual(statement.normalize_report_date("30.09.2026"), "2026-09-30")

    def test_accepts_iso_date(self):
        self.assertEqual(statement.normalize_report_date("2026-09-30"), "2026-09-30")

    def test_accepts_date_objects(self):
        self.assertEqual(statement.normalize_report_date(date(2026, 9, 30)), "2026-09-30")
        self.assertEqual(statement.normalize_report_date(datetime(2026, 9, 30, 12, 15)), "2026-09-30")

    def test_rejects_invalid_date_with_user_friendly_message(self):
        with self.assertRaisesRegex(ValueError, "ДД.ММ.РРРР"):
            statement.normalize_report_date("30/09/2026")


class VehicleStatementRequisitesTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.executescript(
            """
            CREATE TABLE vehicles(
                id INTEGER PRIMARY KEY,
                plate TEXT,
                name TEXT,
                make_model TEXT,
                vin TEXT,
                active INTEGER DEFAULT 1
            );
            CREATE TABLE military_transport_vehicle_profile(
                vehicle_id INTEGER PRIMARY KEY,
                category TEXT DEFAULT '',
                military_type TEXT DEFAULT '',
                order_no TEXT DEFAULT '',
                order_date TEXT DEFAULT '',
                military_unit TEXT DEFAULT '',
                designated INTEGER DEFAULT 0,
                transferred INTEGER DEFAULT 0,
                returned INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                updated_at TEXT DEFAULT ''
            );
            CREATE TABLE military_transport_vehicle_workers(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                employee_id INTEGER,
                worker_name TEXT DEFAULT '',
                active INTEGER DEFAULT 1,
                notes TEXT DEFAULT ''
            );
            CREATE TABLE employees(
                id INTEGER PRIMARY KEY,
                last_name TEXT DEFAULT '',
                first_name TEXT DEFAULT '',
                middle_name TEXT DEFAULT '',
                birth_date TEXT DEFAULT '',
                actual_address TEXT DEFAULT '',
                registered_address TEXT DEFAULT ''
            );
            CREATE TABLE employee_military_profile(
                employee_id INTEGER PRIMARY KEY,
                military_specialty TEXT DEFAULT '',
                military_rank TEXT DEFAULT ''
            );
            INSERT INTO vehicles(id,plate,name,make_model,vin,active)
            VALUES(1,'BC0001AA','Богдан','А092','VIN1',1);
            """
        )
        statement.ensure_schema_on_connection(self.con)
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def test_optional_vehicle_requisites_roundtrip_and_feed_statement(self):
        statement.save_vehicle_statement_data(
            self.con, 1,
            report_scope=statement.SCOPE_OWN,
            vehicle_type="АВТОБУС",
            technical_condition="Справний",
            residual_value="123.45",
            notes="",
        )
        self.con.commit()
        stored = statement.get_vehicle_statement_data(self.con, 1)
        self.assertEqual(stored["report_scope"], statement.SCOPE_OWN)
        self.assertEqual(stored["residual_value"], "123.45")
        rows = statement.collect_statement_rows(self.con, "30.09.2026")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["plate"], "BC0001AA")
        self.assertEqual(rows[0]["vehicle_type"], "АВТОБУС")
        self.assertEqual(rows[0]["technical_condition"], "Справний")
        self.assertEqual(rows[0]["residual_value"], "123.45")

    def test_requisites_remain_optional_for_vehicle_card(self):
        stored = statement.get_vehicle_statement_data(self.con, 1)
        self.assertIsNone(stored)
        overview = statement.statement_overview(self.con, "30.09.2026")
        self.assertEqual(len(overview), 1)
        self.assertEqual(overview[0]["report_scope"], statement.SCOPE_UNKNOWN)
        self.assertEqual(statement.collect_statement_rows(self.con, "30.09.2026"), [])


class RuntimeIdentityTests(unittest.TestCase):
    def test_r3_remains_before_newer_runtime_layers(self):
        source = Path("taxo_app.py").read_text("utf-8")
        self.assertIn("from v1083_features import install as install_v1083", source)
        self.assertLess(source.index("App = install_v1082(core, App)"), source.index("App = install_v1083(core, App)"))
        if "App = install_v1084(core, App)" in source:
            self.assertLess(source.index("App = install_v1083(core, App)"), source.index("App = install_v1084(core, App)"))

    def test_r3_identity_is_historical_anchor(self):
        self.assertEqual(r3.APP_VERSION, "10.8-r3")
        feature_source = Path("v1083_features.py").read_text("utf-8")
        self.assertIn('APP_VERSION = "10.8-r3"', feature_source)
        current = Path("VERSION.txt").read_text("utf-8")
        match = re.search(r"Version:\s*(\d+)\.(\d+)-r(\d+)", current)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(tuple(map(int, match.groups())), (10, 8, 3))
        self.assertIn("v1083_features.py", Path("START.bat").read_text("utf-8"))


if __name__ == "__main__":
    unittest.main()
