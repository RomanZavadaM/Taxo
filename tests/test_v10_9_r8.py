# -*- coding: utf-8 -*-
import sqlite3
import unittest

import operations_orders as ops
from v1098_orders_immutability import (
    FEATURE_VERSION,
    active_driver_assignments,
    add_vehicle_assignment,
    approve_order,
    cancel_order,
    delete_vehicle_assignment,
    ensure_schema_on_connection,
    set_paper_original_signed,
    update_order,
    update_vehicle_assignment,
)


class OrdersImmutabilityR8Tests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys=ON")
        self.con.executescript(
            """
            CREATE TABLE employees(
                id INTEGER PRIMARY KEY,
                last_name TEXT, first_name TEXT, middle_name TEXT,
                position TEXT, birth_date TEXT,
                actual_address TEXT, registered_address TEXT
            );
            CREATE TABLE vehicles(
                id INTEGER PRIMARY KEY,
                name TEXT, plate TEXT, make_model TEXT
            );
            CREATE TABLE employee_military_profile(
                employee_id INTEGER PRIMARY KEY,
                military_specialty TEXT, military_rank TEXT
            );
            INSERT INTO employees VALUES(1,'Іваненко','Іван','Іванович','водій','','','');
            INSERT INTO employees VALUES(2,'Петренко','Петро','Петрович','диспетчер','','','');
            INSERT INTO vehicles VALUES(10,'Автобус 10','BC0010AA','Model A');
            INSERT INTO vehicles VALUES(20,'Автобус 20','BC0020AA','Model B');
            """
        )
        ensure_schema_on_connection(self.con)

    def tearDown(self):
        self.con.close()

    def order(self, number, *, kind=ops.TYPE_GENERIC, controller=2):
        # Do not use ops.create_order() here: historical feature-layer tests
        # intentionally monkey-patch that public name during full-suite import.
        # The fixture is inserted directly, while every r8 behaviour below is
        # exercised through the real r8 domain functions.
        cur = self.con.execute(
            """INSERT INTO operations_orders(
                   order_type,order_no,order_date,place,subject,preamble,body_text,
                   control_employee_id,status,approved_at,cancelled_at,note,
                   paper_original_signed,paper_original_signed_at,created_at,updated_at
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                kind, str(number), "2026-10-01", "", "Тест", "", "",
                controller, ops.ORDER_DRAFT, "", "", "", 0, "",
                "2026-10-01T09:00:00", "2026-10-01T09:00:00",
            ),
        )
        return int(cur.lastrowid)

    def assignment_order(self, number):
        return self.order(number, kind=ops.TYPE_VEHICLE_ASSIGNMENT)

    def test_identity(self):
        self.assertEqual(FEATURE_VERSION, "10.9-r8")

    def test_omitted_control_employee_is_preserved(self):
        oid = self.order("1")
        updated = update_order(self.con, oid, subject="Нова тема")
        self.assertEqual(updated["control_employee_id"], 2)
        cleared = update_order(self.con, oid, control_employee_id=None)
        self.assertIsNone(cleared["control_employee_id"])

    def test_approved_order_is_immutable(self):
        oid = self.order("2")
        approve_order(self.con, oid)
        with self.assertRaisesRegex(ValueError, "незмінний"):
            update_order(self.con, oid, subject="Не можна")

    def test_signed_order_is_immutable_and_signature_cannot_be_removed(self):
        oid = self.order("3")
        set_paper_original_signed(self.con, oid, True, signed_at="2026-10-01T10:00:00")
        with self.assertRaisesRegex(ValueError, "незмінний"):
            update_order(self.con, oid, body_text="Не можна")
        with self.assertRaisesRegex(ValueError, "не можна знімати"):
            set_paper_original_signed(self.con, oid, False)

    def test_cancelled_order_cannot_be_reapproved(self):
        oid = self.order("4")
        cancel_order(self.con, oid)
        with self.assertRaisesRegex(ValueError, "не можна повторно затвердити"):
            approve_order(self.con, oid)

    def test_assignments_under_approved_order_cannot_be_changed(self):
        oid = self.assignment_order("5")
        aid = add_vehicle_assignment(self.con, oid, 10, 1, valid_from="2026-10-01")
        approve_order(self.con, oid)
        with self.assertRaisesRegex(ValueError, "незмінний"):
            update_vehicle_assignment(self.con, aid, vehicle_id=20)
        with self.assertRaisesRegex(ValueError, "незмінний"):
            delete_vehicle_assignment(self.con, aid)
        with self.assertRaisesRegex(ValueError, "незмінний"):
            add_vehicle_assignment(self.con, oid, 20, 1, valid_from="2026-10-10")

    def test_new_approved_assignment_ends_prior_without_rewriting_old_order(self):
        first = self.assignment_order("6")
        old_aid = add_vehicle_assignment(self.con, first, 10, 1, valid_from="2026-10-01")
        approve_order(self.con, first)
        old_before = dict(ops.get_vehicle_assignment(self.con, old_aid))

        second = self.assignment_order("7")
        add_vehicle_assignment(self.con, second, 20, 1, valid_from="2026-10-15")
        approve_order(self.con, second)

        old_after = dict(ops.get_vehicle_assignment(self.con, old_aid))
        self.assertEqual(old_before, old_after)
        ending = self.con.execute(
            "SELECT * FROM vehicle_driver_assignment_endings WHERE assignment_id=?", (old_aid,)
        ).fetchone()
        self.assertEqual(ending["effective_until"], "2026-10-14")
        self.assertEqual(ending["ended_by_order_id"], second)
        self.assertEqual(len(active_driver_assignments(self.con, 10, "2026-10-14")), 1)
        self.assertEqual(len(active_driver_assignments(self.con, 10, "2026-10-15")), 0)
        rows = active_driver_assignments(self.con, 20, "2026-10-15")
        self.assertEqual([row["employee_id"] for row in rows], [1])

    def test_conflicting_assignments_inside_new_order_block_approval(self):
        oid = self.assignment_order("8")
        add_vehicle_assignment(self.con, oid, 10, 1, valid_from="2026-10-01")
        add_vehicle_assignment(self.con, oid, 20, 1, valid_from="2026-10-10")
        with self.assertRaisesRegex(ValueError, "одночасно"):
            approve_order(self.con, oid)
        self.assertEqual(ops.get_order(self.con, oid)["status"], ops.ORDER_DRAFT)


if __name__ == "__main__":
    unittest.main()
