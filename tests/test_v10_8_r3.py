# -*- coding: utf-8 -*-
from datetime import date, datetime
from pathlib import Path
import re
import sqlite3
import unittest

import military_transport_statement as statement
import v1083_features as r3
import version_compat  # 10.10 stable-aware version parsing


class StatementDateNormalizationTests(unittest.TestCase):
    def test_accepts_taxo_display_date(self):
        self.assertEqual(r3.normalize_statement_day("30.09.2026"), "2026-09-30")

    def test_accepts_iso_date(self):
        self.assertEqual(r3.normalize_statement_day("2026-09-30"), "2026-09-30")

    def test_accepts_date_objects(self):
        self.assertEqual(r3.normalize_statement_day(date(2026, 9, 30)), "2026-09-30")
        self.assertEqual(r3.normalize_statement_day(datetime(2026, 9, 30, 12, 0)), "2026-09-30")

    def test_rejects_invalid_date_with_user_friendly_message(self):
        with self.assertRaisesRegex(ValueError, "ДД.ММ.РРРР"):
            r3.normalize_statement_day("31.02.2026")


class VehicleStatementRequisitesTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.executescript(
            """
            PRAGMA foreign_keys=ON;
            CREATE TABLE vehicles(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                plate TEXT DEFAULT '',
                make_model TEXT DEFAULT '',
                year INTEGER,
                active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            );
            CREATE TABLE employees(
                id INTEGER PRIMARY KEY,
                last_name TEXT NOT NULL,
                first_name TEXT NOT NULL,
                middle_name TEXT DEFAULT '',
                active INTEGER DEFAULT 1
            );
            INSERT INTO vehicles(id,name,plate,make_model,year,active,created_at)
            VALUES(1,'БАЗ А079','BC0001AA','БАЗ А079',2010,1,'2026-09-30T00:00:00');
            """
        )
        statement.ensure_schema_on_connection(self.con)
        statement._iso_day = r3.normalize_statement_day

    def tearDown(self):
        self.con.close()

    def test_optional_vehicle_requisites_roundtrip_and_feed_statement(self):
        statement.set_vehicle_statement_data(
            self.con,
            1,
            report_scope=statement.SCOPE_OWN,
            vehicle_type="АВТОБУС",
            technical_condition="Справний",
            residual_book_value_thousand_uah="123,45",
            note="Реквізити картки ТЗ",
        )
        self.con.commit()
        stored = statement.get_vehicle_statement_data(self.con, 1)
        self.assertEqual(stored["vehicle_type"], "АВТОБУС")
        self.assertEqual(stored["technical_condition"], "Справний")
        self.assertEqual(stored["residual_book_value_thousand_uah"], "123.45")
        self.assertEqual(stored["note"], "Реквізити картки ТЗ")

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
        self.assertIn('APP_VERSION = "10.8-r3"', Path("v1083_features.py").read_text("utf-8"))
        current = Path("VERSION.txt").read_text("utf-8")
        match = version_compat.search_version_line(current)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(tuple(map(int, match.groups())), (10, 8, 3))
        self.assertIn("v1083_features.py", Path("START.bat").read_text("utf-8"))


if __name__ == "__main__":
    unittest.main()
