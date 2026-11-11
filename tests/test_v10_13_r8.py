# -*- coding: utf-8 -*-
"""Taxo 10.13-r8: bulk assignment selection matches approval invariants."""
from pathlib import Path
import sqlite3
import unittest

import main
import operations_orders as ops
from v1098_orders_immutability import approve_order as approve_immutable


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
            (2,'Петренко','Петро','','Водій','002','2222222222',1,22),
            (3,'Сидоренко','Сидір','','Водій','003','3333333333',1,33);
        INSERT INTO employee_roles VALUES(1,'Водій'),(2,'Водій'),(3,'Водій');
        INSERT INTO drivers VALUES(11,1,''),(22,1,''),(33,1,'');
        INSERT INTO vehicles VALUES
            (10,'Автобус 10','BC0010AA','MAN Lion','VIN00000000000010','10',1),
            (20,'Автобус 20','BC0020AA','MAN Lion','VIN00000000000020','20',1),
            (30,'Автобус 30','BC0030AA','Mercedes','VIN00000000000030','30',1);
        """
    )
    ops.ensure_schema_on_connection(con)
    con.commit()
    return con


class TaxoR8BulkAssignmentSafetyTests(unittest.TestCase):
    def setUp(self):
        self.con=make_db()

    def tearDown(self):
        self.con.close()

    def test_identity_is_10_13_r8_or_newer(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION),(10,13,8))

    def test_one_driver_many_vehicles_is_rejected_before_draft_pairs(self):
        with self.assertRaisesRegex(ValueError,"Один водій не може"):
            ops.build_assignment_pairs([10,20,30],[1])

    def test_one_vehicle_many_drivers_can_be_approved(self):
        pairs=ops.build_assignment_pairs([10],[1,2,3])
        oid=ops.create_vehicle_assignment_order(
            self.con,order_date="08.11.2026",initial_pairs=pairs
        )
        approved=approve_immutable(self.con,oid)
        self.assertEqual(approved["status"],ops.ORDER_APPROVED)
        rows=ops.order_assignments(self.con,oid)
        self.assertEqual(
            [(row["vehicle_id"],row["employee_id"]) for row in rows],
            [(10,1),(10,2),(10,3)],
        )

    def test_equal_multiple_distinct_pairs_can_be_approved(self):
        pairs=ops.build_assignment_pairs([10,20,30],[1,2,3])
        oid=ops.create_vehicle_assignment_order(
            self.con,order_date="08.11.2026",initial_pairs=pairs
        )
        approved=approve_immutable(self.con,oid)
        self.assertEqual(approved["status"],ops.ORDER_APPROVED)
        self.assertEqual(
            [(row["vehicle_id"],row["employee_id"]) for row in ops.order_assignments(self.con,oid)],
            [(10,1),(20,2),(30,3)],
        )

    def test_approval_guard_still_rejects_conflicting_manual_rows(self):
        oid=ops.create_vehicle_assignment_order(self.con,order_date="08.11.2026")
        ops.add_vehicle_assignment(self.con,oid,10,1,valid_from="08.11.2026")
        ops.add_vehicle_assignment(self.con,oid,20,1,valid_from="08.11.2026")
        with self.assertRaisesRegex(ValueError,"одночасно"):
            approve_immutable(self.con,oid)
        self.assertEqual(ops.get_order(self.con,oid)["status"],ops.ORDER_DRAFT)

    def test_ui_no_longer_advertises_one_driver_many_vehicles(self):
        text=Path("src/taxo/operations_orders_ui.py").read_text(encoding="utf-8")
        text+=Path("src/taxo/order_assignments_ui.py").read_text(encoding="utf-8")
        self.assertIn("Один водій не закріплюється одночасно за кількома ТЗ",text)
        self.assertNotIn("1 водій + кілька ТЗ",text)


if __name__=="__main__":
    unittest.main()
