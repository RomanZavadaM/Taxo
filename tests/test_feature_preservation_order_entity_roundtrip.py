# -*- coding: utf-8 -*-
"""Feature preservation: structured order members survive a real DB reopen.

Checks the result of a save, not just the existence of a button. Uses only
synthetic personnel and vehicle data; never accesses a user's workspace.
"""
import sqlite3
import tempfile
import unittest
from pathlib import Path

import operations_orders as ops


class OrderEntitiesPersistentRoundtripTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "taxo_test.sqlite3"
        self.con = self.connect()
        self.con.executescript("""
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY, last_name TEXT, first_name TEXT,
                middle_name TEXT, position TEXT, personnel_no TEXT,
                rnokpp TEXT, active INTEGER DEFAULT 1, driver_id INTEGER
            );
            CREATE TABLE employee_roles (employee_id INTEGER, role TEXT);
            CREATE TABLE drivers (
                id INTEGER PRIMARY KEY, active INTEGER DEFAULT 1,
                driver_end_date TEXT DEFAULT ''
            );
            CREATE TABLE employee_military_profile (
                employee_id INTEGER PRIMARY KEY,
                registry_person_id TEXT DEFAULT ''
            );
            CREATE TABLE vehicles (
                id INTEGER PRIMARY KEY, name TEXT, plate TEXT, make_model TEXT,
                vin TEXT, garage_no TEXT, active INTEGER DEFAULT 1
            );
            INSERT INTO employees VALUES
                (1,'Іваненко','Іван','','Водій','001','1111111111',1,11),
                (2,'Петренко','Петро','','Механік','002','2222222222',1,NULL);
            INSERT INTO employee_roles VALUES (1,'Водій');
            INSERT INTO drivers VALUES (11,1,'');
            INSERT INTO vehicles VALUES
                (10,'Автобус 10','BC0010AA','MAN Lion',
                 'WMA00000000000010','10',1);
        """)
        ops.ensure_schema_on_connection(self.con)
        self.con.commit()
        self.addCleanup(self.close_current)

    def close_current(self):
        # The connection changes after each reopen: close the final handle.
        self.con.close()

    def connect(self):
        con = sqlite3.connect(str(self.path))
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def test_saved_members_survive_reopen_card_changes_and_targeted_delete(self):
        oid = ops.create_order(
            self.con, order_type=ops.TYPE_OCCUPATIONAL_SAFETY,
            order_no="TEST-101", order_date="19.11.2026",
            subject="Пробний наказ", body_text="Тільки тестові дані."
        )
        people = ops.add_order_entities(
            self.con, oid, ops.ORDER_ENTITY_EMPLOYEE, [1, 2, 1],
            role="Учасник", note="Тестове збереження"
        )
        vehicle = ops.add_order_entity(
            self.con, oid, ops.ORDER_ENTITY_VEHICLE, 10,
            role="Транспортний засіб"
        )
        self.assertEqual(len(people), 2)
        self.assertIsNotNone(vehicle)
        self.con.commit()
        self.con.close()
        self.con = self.connect()

        rows = ops.list_order_entities(self.con, oid)
        self.assertEqual(
            [(row["entity_type"], row["entity_id"]) for row in rows],
            [(ops.ORDER_ENTITY_EMPLOYEE, 1),
             (ops.ORDER_ENTITY_EMPLOYEE, 2),
             (ops.ORDER_ENTITY_VEHICLE, 10)]
        )
        self.assertEqual([row["sequence_no"] for row in rows], [1, 2, 3])
        self.assertEqual(rows[0]["note"], "Тестове збереження")
        self.assertEqual(ops.order_entity_view(rows[0])["display"], "Іваненко Іван")
        self.assertIn("BC0010AA", ops.order_entity_view(rows[2])["display"])
        print_view = ops.order_preview_text(
            ops.get_order(self.con, oid), entities=rows
        )
        self.assertIn("Іваненко Іван", print_view)
        self.assertIn("Петренко Петро", print_view)
        self.assertIn("BC0010AA", print_view)

        self.con.execute(
            "UPDATE employees SET last_name='Змінене' WHERE id=1"
        )
        self.con.execute(
            "UPDATE vehicles SET plate='CHANGED' WHERE id=10"
        )
        self.con.commit()
        self.con.close()
        self.con = self.connect()
        rows = ops.list_order_entities(self.con, oid)
        self.assertEqual(ops.order_entity_view(rows[0])["display"], "Іваненко Іван")
        self.assertIn("BC0010AA", ops.order_entity_view(rows[2])["display"])

        ops.delete_order_entity(
            self.con, rows[1]["id"], history_note="Контрольне видалення"
        )
        self.con.commit()
        self.con.close()
        self.con = self.connect()
        after = ops.list_order_entities(self.con, oid)
        self.assertEqual(
            [(row["entity_type"], row["entity_id"]) for row in after],
            [(ops.ORDER_ENTITY_EMPLOYEE, 1), (ops.ORDER_ENTITY_VEHICLE, 10)]
        )
        final_view = ops.order_preview_text(
            ops.get_order(self.con, oid), entities=after
        )
        self.assertIn("Іваненко Іван", final_view)
        self.assertNotIn("Петренко Петро", final_view)
        self.assertIn("BC0010AA", final_view)
        actions = [row["action"] for row in ops.order_history(self.con, oid)]
        self.assertIn("entity_add", actions)
        self.assertIn("entity_remove", actions)

    def test_duplicate_add_after_reopen_is_idempotent(self):
        oid = ops.create_order(
            self.con, order_type=ops.TYPE_OCCUPATIONAL_SAFETY,
            order_no="TEST-102", order_date="19.11.2026",
            subject="Тест на дублікати"
        )
        ops.add_order_entities(
            self.con, oid, ops.ORDER_ENTITY_EMPLOYEE, [1, 2]
        )
        self.con.commit()
        self.con.close()
        self.con = self.connect()
        created = ops.add_order_entities(
            self.con, oid, ops.ORDER_ENTITY_EMPLOYEE, [2, 1, 2]
        )
        self.assertEqual(created, [])
        self.assertEqual(len(ops.list_order_entities(self.con, oid)), 2)


if __name__ == "__main__":
    unittest.main()
