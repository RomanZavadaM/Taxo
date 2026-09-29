# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import unittest
from pathlib import Path

import operations_orders as ops


class OperationsEditingR4Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "taxo.sqlite"
        self.con = sqlite3.connect(self.db_path)
        self.con.row_factory = sqlite3.Row
        self.con.execute("CREATE TABLE employees(id INTEGER PRIMARY KEY,last_name TEXT,first_name TEXT,middle_name TEXT,position TEXT,active INTEGER DEFAULT 1)")
        self.con.execute("CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT,active INTEGER DEFAULT 1)")
        self.con.execute("CREATE TABLE employee_military_profile(employee_id INTEGER PRIMARY KEY,military_specialty TEXT,military_rank TEXT)")
        self.con.execute("INSERT INTO employees(id,last_name,first_name,middle_name,position,active) VALUES(1,'Іваненко','Іван','Іванович','водій',1)")
        self.con.execute("INSERT INTO employees(id,last_name,first_name,middle_name,position,active) VALUES(2,'Петренко','Петро','Петрович','водій',1)")
        self.con.execute("INSERT INTO vehicles(id,name,plate,make_model,active) VALUES(1,'Bus 1','AA0001AA','MAN',1)")
        self.con.execute("INSERT INTO vehicles(id,name,plate,make_model,active) VALUES(2,'Bus 2','AA0002AA','Mercedes',1)")
        ops.ensure_schema_on_connection(self.con)

    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()

    def _order(self):
        return ops.create_order(
            self.con,
            order_type=ops.TYPE_VEHICLE_ASSIGNMENT,
            order_no="15",
            order_date="29.09.2026",
            place="Львів",
            subject="Про закріплення автотранспортних засобів",
            preamble="Підстава",
            control_employee_id=1,
        )

    def test_approved_order_can_be_corrected_and_history_is_preserved(self):
        oid = self._order()
        ops.add_vehicle_assignment(self.con, oid, 1, 1, valid_from="29.09.2026")
        ops.approve_order(self.con, oid)
        self.con.commit()
        self.assertEqual(ops.get_order(self.con, oid)["status"], ops.ORDER_APPROVED)

        updated = ops.update_order(
            self.con,
            oid,
            order_no="15-А",
            order_date="30.09.2026",
            place="Львів",
            subject="Про виправлене закріплення автотранспортних засобів",
            preamble="Уточнена підстава",
            body_text="",
            control_employee_id=1,
            history_note="Виправлення описки після друку",
        )
        self.con.commit()

        self.assertEqual(updated["status"], ops.ORDER_APPROVED)
        self.assertEqual(updated["order_no"], "15-А")
        history = ops.order_history(self.con, oid)
        actions = [row["action"] for row in history if row["entity_type"] == "order"]
        self.assertIn("create", actions)
        self.assertIn("approve", actions)
        self.assertIn("update", actions)

    def test_paper_original_marker_does_not_lock_order(self):
        oid = self._order()
        ops.set_paper_original_signed(self.con, oid, True)
        self.con.commit()
        row = ops.get_order(self.con, oid)
        self.assertEqual(row["paper_original_signed"], 1)
        self.assertTrue(row["paper_original_signed_at"])

        ops.update_order(self.con, oid, order_no="15-Б", history_note="Корекція після паперового підпису")
        self.con.commit()
        self.assertEqual(ops.get_order(self.con, oid)["order_no"], "15-Б")

    def test_assignment_can_be_corrected_and_history_is_preserved(self):
        oid = self._order()
        aid = ops.add_vehicle_assignment(self.con, oid, 1, 1, valid_from="29.09.2026")
        ops.approve_order(self.con, oid)
        self.con.commit()

        updated = ops.update_vehicle_assignment(
            self.con,
            aid,
            vehicle_id=2,
            employee_id=2,
            valid_from="30.09.2026",
            valid_until="31.12.2026",
            note="Виправлено закріплення",
            history_note="Помилка у первинному наказі",
        )
        self.con.commit()

        self.assertEqual(updated["vehicle_id"], 2)
        self.assertEqual(updated["employee_id"], 2)
        self.assertEqual(updated["valid_from"], "2026-09-30")
        history = ops.order_history(self.con, oid)
        self.assertIn("update", [row["action"] for row in history if row["entity_type"] == "assignment"])

    def test_r2_r3_schema_is_migrated_additively(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        try:
            con.execute("CREATE TABLE employees(id INTEGER PRIMARY KEY,last_name TEXT,first_name TEXT,middle_name TEXT,position TEXT,active INTEGER DEFAULT 1)")
            con.execute("CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT,active INTEGER DEFAULT 1)")
            con.execute("CREATE TABLE employee_military_profile(employee_id INTEGER PRIMARY KEY,military_specialty TEXT,military_rank TEXT)")
            con.execute("CREATE TABLE operations_orders(id INTEGER PRIMARY KEY AUTOINCREMENT,order_type TEXT NOT NULL,order_no TEXT NOT NULL,order_date TEXT NOT NULL,place TEXT DEFAULT '',subject TEXT DEFAULT '',preamble TEXT DEFAULT '',body_text TEXT DEFAULT '',control_employee_id INTEGER,status TEXT NOT NULL DEFAULT 'draft',approved_at TEXT DEFAULT '',cancelled_at TEXT DEFAULT '',note TEXT DEFAULT '',created_at TEXT NOT NULL,updated_at TEXT NOT NULL,UNIQUE(order_no,order_date))")
            con.execute("CREATE TABLE vehicle_driver_assignments(id INTEGER PRIMARY KEY AUTOINCREMENT,order_id INTEGER NOT NULL,vehicle_id INTEGER NOT NULL,employee_id INTEGER NOT NULL,valid_from TEXT NOT NULL,valid_until TEXT DEFAULT '',sequence_no INTEGER NOT NULL DEFAULT 1,note TEXT DEFAULT '',created_at TEXT NOT NULL,UNIQUE(order_id,vehicle_id,employee_id,valid_from))")
            ops.ensure_schema_on_connection(con)
            order_cols = {row[1] for row in con.execute("PRAGMA table_info(operations_orders)")}
            assignment_cols = {row[1] for row in con.execute("PRAGMA table_info(vehicle_driver_assignments)")}
            self.assertIn("paper_original_signed", order_cols)
            self.assertIn("paper_original_signed_at", order_cols)
            self.assertIn("updated_at", assignment_cols)
            self.assertIsNotNone(con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operations_change_log'").fetchone())
        finally:
            con.close()


class R4IdentityTests(unittest.TestCase):
    def test_operations_core_identifies_r4(self):
        self.assertEqual(ops.APP_VERSION, "10.7-r4")

    def test_version_file_is_r4(self):
        text = Path("VERSION.txt").read_text(encoding="utf-8")
        self.assertIn("Version: 10.7-r4", text)


if __name__ == "__main__":
    unittest.main()
