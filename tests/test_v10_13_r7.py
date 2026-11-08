# -*- coding: utf-8 -*-
"""Taxo 10.13-r7: bulk assignment orders and independent auto-numbering."""
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


class TaxoR7BulkAssignmentAndNumberingTests(unittest.TestCase):
    def setUp(self):
        self.con=make_db()

    def tearDown(self):
        self.con.close()

    def test_identity_is_10_13_r7_or_newer(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION),(10,13,7))

    def test_fresh_numbering_has_independent_work_and_personnel_series(self):
        self.assertEqual(ops.next_order_number(self.con,ops.ORDER_SERIES_WORK),"1")
        self.assertEqual(ops.next_order_number(self.con,ops.ORDER_SERIES_PERSONNEL),"1-К")
        work=ops.create_order(
            self.con,order_type=ops.TYPE_GENERIC,order_date="08.11.2026",
            order_series=ops.ORDER_SERIES_WORK,
        )
        personnel=ops.create_order(
            self.con,order_type=ops.TYPE_GENERIC,order_date="08.11.2026",
            order_series=ops.ORDER_SERIES_PERSONNEL,
        )
        self.assertEqual(ops.get_order(self.con,work)["order_no"],"1")
        self.assertEqual(ops.get_order(self.con,personnel)["order_no"],"1-К")
        self.assertEqual(ops.next_order_number(self.con,ops.ORDER_SERIES_WORK),"2")
        self.assertEqual(ops.next_order_number(self.con,ops.ORDER_SERIES_PERSONNEL),"2-К")

    def test_configurable_start_and_manual_number_advance_only_its_series(self):
        ops.save_settings(
            self.con,work_order_next_no=40,personnel_order_next_no=7
        )
        wid=ops.create_order(
            self.con,order_type=ops.TYPE_GENERIC,order_no="50",
            order_date="08.11.2026",order_series=ops.ORDER_SERIES_WORK,
        )
        pid=ops.create_order(
            self.con,order_type=ops.TYPE_GENERIC,order_no="12",
            order_date="08.11.2026",order_series=ops.ORDER_SERIES_PERSONNEL,
        )
        self.assertEqual(ops.get_order(self.con,wid)["order_no"],"50")
        self.assertEqual(ops.get_order(self.con,pid)["order_no"],"12-К")
        self.assertEqual(ops.next_order_number(self.con,ops.ORDER_SERIES_WORK),"51")
        self.assertEqual(ops.next_order_number(self.con,ops.ORDER_SERIES_PERSONNEL),"13-К")

    def test_old_database_migration_seeds_work_counter_from_existing_numbers(self):
        con=sqlite3.connect(":memory:")
        con.row_factory=sqlite3.Row
        con.executescript(
            """
            CREATE TABLE employees(id INTEGER PRIMARY KEY);
            CREATE TABLE vehicles(id INTEGER PRIMARY KEY);
            CREATE TABLE operations_settings(
                id INTEGER PRIMARY KEY CHECK(id=1),
                operations_responsible_employee_id INTEGER,
                military_transport_responsible_employee_id INTEGER,
                order_place TEXT DEFAULT '',
                updated_at TEXT NOT NULL
            );
            INSERT INTO operations_settings(id,updated_at) VALUES(1,'2026-11-08T00:00:00');
            CREATE TABLE operations_orders(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_type TEXT NOT NULL,
                order_no TEXT NOT NULL,
                order_date TEXT NOT NULL,
                place TEXT DEFAULT '',
                subject TEXT DEFAULT '',
                preamble TEXT DEFAULT '',
                body_text TEXT DEFAULT '',
                control_employee_id INTEGER,
                status TEXT NOT NULL DEFAULT 'draft',
                approved_at TEXT DEFAULT '',
                cancelled_at TEXT DEFAULT '',
                note TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(order_no,order_date)
            );
            INSERT INTO operations_orders(
                order_type,order_no,order_date,created_at,updated_at
            ) VALUES('generic','17','2026-11-01','x','x');
            """
        )
        try:
            ops.ensure_schema_on_connection(con)
            cfg=ops.settings(con)
            self.assertEqual(cfg["work_order_next_no"],18)
            self.assertEqual(cfg["personnel_order_next_no"],1)
            row=con.execute("SELECT order_series FROM operations_orders WHERE id=1").fetchone()
            self.assertEqual(row["order_series"],ops.ORDER_SERIES_WORK)
        finally:
            con.close()

    def test_pair_builder_supports_vehicle_to_many_drivers_and_equal_many_to_many(self):
        self.assertEqual(
            ops.build_assignment_pairs([10],[1,2,3]),
            [(10,1),(10,2),(10,3)],
        )
        self.assertEqual(
            ops.build_assignment_pairs([10,20,30],[1,2,3]),
            [(10,1),(20,2),(30,3)],
        )

    def test_pair_builder_blocks_ambiguous_unequal_many_to_many(self):
        with self.assertRaisesRegex(ValueError,"однакову кількість"):
            ops.build_assignment_pairs([10,20,30],[1,2])
        with self.assertRaisesRegex(ValueError,"Виберіть і"):
            ops.build_assignment_pairs([10,20],[])

    def test_assignment_order_can_create_many_pairs_at_once(self):
        oid=ops.create_vehicle_assignment_order(
            self.con,order_date="08.11.2026",
            initial_pairs=[(10,1),(20,2),(30,3)],
        )
        order=ops.get_order(self.con,oid)
        self.assertEqual(order["order_no"],"1")
        rows=ops.order_assignments(self.con,oid)
        self.assertEqual(
            [(row["vehicle_id"],row["employee_id"]) for row in rows],
            [(10,1),(20,2),(30,3)],
        )
        self.assertEqual(ops.next_order_number(self.con,ops.ORDER_SERIES_WORK),"2")

    def test_bulk_add_deduplicates_repeated_pair_in_same_call(self):
        oid=ops.create_vehicle_assignment_order(self.con,order_date="08.11.2026")
        created=ops.add_vehicle_assignments_bulk(
            self.con,oid,[(10,1),(10,1),(20,2)],valid_from="08.11.2026"
        )
        self.assertEqual(len(created),2)
        self.assertEqual(len(ops.order_assignments(self.con,oid)),2)

    def test_ui_exposes_bulk_assignment_and_numbering_controls(self):
        text=Path("src/taxo/operations_orders_ui.py").read_text(encoding="utf-8")
        for marker in (
            "Наступний № робочого / експлуатаційного наказу",
            "Наступний № кадрового наказу",
            "Серія нумерації",
            "Транспортний засіб",
            "Водій із бази водіїв",
            'text="Додати багато…"',
            'selectmode="extended"',
        ):
            self.assertIn(marker,text)


if __name__=="__main__":
    unittest.main()
