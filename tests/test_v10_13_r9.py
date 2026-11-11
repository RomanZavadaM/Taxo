# -*- coding: utf-8 -*-
"""Taxo 10.13-r9: owner manual-test fixes."""
from pathlib import Path
import sqlite3
import unittest

import main
import operations_orders as ops


def make_db():
    con=sqlite3.connect(":memory:")
    con.row_factory=sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(
        """
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY,
            last_name TEXT,first_name TEXT,middle_name TEXT,
            position TEXT,personnel_no TEXT,rnokpp TEXT,
            active INTEGER DEFAULT 1,driver_id INTEGER
        );
        CREATE TABLE employee_roles(employee_id INTEGER,role TEXT);
        CREATE TABLE drivers(
            id INTEGER PRIMARY KEY,
            active INTEGER DEFAULT 1,
            driver_end_date TEXT DEFAULT ''
        );
        CREATE TABLE employee_military_profile(
            employee_id INTEGER PRIMARY KEY,
            registry_person_id TEXT DEFAULT ''
        );
        CREATE TABLE vehicles(
            id INTEGER PRIMARY KEY,
            name TEXT,plate TEXT,make_model TEXT,vin TEXT,
            garage_no TEXT,active INTEGER DEFAULT 1
        );
        INSERT INTO employees VALUES
            (1,'Іваненко','Іван','','Водій','001','1111111111',1,11),
            (2,'Петренко','Петро','','Водій','002','2222222222',1,22);
        INSERT INTO employee_roles VALUES(1,'Водій'),(2,'Водій');
        INSERT INTO drivers VALUES(11,1,''),(22,1,'');
        INSERT INTO vehicles VALUES
            (10,'Автобус 10','BC0010AA','MAN Lion','VIN00000000000010','10',1),
            (20,'Автобус 20','BC0020AA','MAN Lion','VIN00000000000020','20',1);
        """
    )
    ops.ensure_schema_on_connection(con)
    con.commit()
    return con


class TaxoR9OwnerTestFixes(unittest.TestCase):
    def setUp(self):
        self.con=make_db()

    def tearDown(self):
        self.con.close()

    def test_identity_is_10_13_r9_or_newer(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION),(10,13,9))

    def test_legacy_template_wrapper_accepts_order_series(self):
        text=Path("src/taxo/v1079_features.py").read_text(encoding="utf-8")
        self.assertIn("order_series=None",text)
        self.assertIn('kwargs["order_series"] = order_series',text)
        self.assertIn("return original_create_order(con, **kwargs)",text)

    def test_duplicate_single_assignment_has_human_message(self):
        oid=ops.create_vehicle_assignment_order(self.con,order_date="08.11.2026")
        ops.add_vehicle_assignment(self.con,oid,10,1,valid_from="08.11.2026")
        with self.assertRaisesRegex(ValueError,"Таке закріплення вже є"):
            ops.add_vehicle_assignment(self.con,oid,10,1,valid_from="08.11.2026")

    def test_bulk_assignment_skips_existing_pair_and_keeps_new_pair(self):
        oid=ops.create_vehicle_assignment_order(self.con,order_date="08.11.2026")
        ops.add_vehicle_assignment(self.con,oid,10,1,valid_from="08.11.2026")
        created=ops.add_vehicle_assignments_bulk(
            self.con,oid,[(10,1),(20,2)],valid_from="08.11.2026"
        )
        self.assertEqual(len(created),1)
        rows=ops.order_assignments(self.con,oid)
        self.assertEqual(
            [(row["vehicle_id"],row["employee_id"]) for row in rows],
            [(10,1),(20,2)],
        )

    def test_numbering_has_direct_visible_entry_from_orders(self):
        text=Path("src/taxo/operations_orders_ui.py").read_text(encoding="utf-8")
        text+=Path("src/taxo/operations_settings_ui.py").read_text(encoding="utf-8")
        text+=Path("src/taxo/order_register_ui.py").read_text(encoding="utf-8")
        for marker in (
            "Нумерація наказів…",
            'text="Нумерація наказів"',
            "Наступний № робочого / експлуатаційного наказу",
            "Наступний № кадрового наказу",
            "Якщо паперовий журнал уже ведеться",
        ):
            self.assertIn(marker,text)

    def test_startup_schedules_one_time_foreground_focus(self):
        text=Path("taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("def _bring_main_window_to_front(app):",text)
        self.assertIn('app.attributes("-topmost", True)',text)
        self.assertIn('app.after(250, lambda: app.attributes("-topmost", False))',text)
        self.assertIn("app.focus_force()",text)
        self.assertIn("app.after(120, lambda: _bring_main_window_to_front(app))",text)


if __name__=="__main__":
    unittest.main()
