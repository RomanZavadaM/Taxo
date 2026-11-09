# -*- coding: utf-8 -*-
"""Taxo 10.13-r6: structured order employees/vehicles with frozen snapshots."""
import json
from pathlib import Path
import sqlite3
import unittest

import main
import operations_orders as ops


class StructuredOrderEntitiesR6Tests(unittest.TestCase):
    def setUp(self):
        self.con=sqlite3.connect(":memory:")
        self.con.row_factory=sqlite3.Row
        self.con.execute("PRAGMA foreign_keys=ON")
        self.con.executescript(
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
                (2,'Петренко','Петро','','Механік','002','2222222222',1,NULL),
                (3,'Старий','Працівник','','Слюсар','003','3333333333',0,NULL);
            INSERT INTO employee_roles VALUES(1,'Водій');
            INSERT INTO employee_roles VALUES(2,'Механік');
            INSERT INTO drivers VALUES(11,1,'');
            INSERT INTO employee_military_profile VALUES(1,'REG-001');
            INSERT INTO vehicles VALUES
                (10,'Автобус 10','BC0010AA','MAN Lion','WMA00000000000010','10',1),
                (20,'Старий автобус','BC0020AA','Mercedes','WDB00000000000020','20',0);
            """
        )
        ops.ensure_schema_on_connection(self.con)
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def _order(self, order_type=ops.TYPE_OCCUPATIONAL_SAFETY, no="1"):
        return ops.create_order(
            self.con,order_type=order_type,order_no=no,order_date="08.11.2026",
            subject="Тестовий наказ",body_text="1. Виконати вимоги."
        )

    def test_identity_is_10_13_r6_or_newer(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION),(10,13,6))

    def test_schema_contains_structured_order_entities(self):
        cols={row[1] for row in self.con.execute("PRAGMA table_info(operations_order_entities)")}
        self.assertTrue(
            {"order_id","entity_type","entity_id","role","snapshot_json","sequence_no","note"}.issubset(cols)
        )

    def test_employee_snapshot_does_not_change_with_live_card(self):
        oid=self._order()
        link=ops.add_order_entity(
            self.con,oid,ops.ORDER_ENTITY_EMPLOYEE,1,role="Працівник"
        )
        before=ops.get_order_entity(self.con,link)
        frozen=json.loads(before["snapshot_json"])
        self.assertEqual(frozen["name"],"Іваненко Іван")
        self.assertEqual(frozen["personnel_no"],"001")
        self.con.execute(
            "UPDATE employees SET last_name='Змінений',personnel_no='999',rnokpp='9999999999' WHERE id=1"
        )
        after=ops.get_order_entity(self.con,link)
        view=ops.order_entity_view(after)
        self.assertEqual(view["display"],"Іваненко Іван")
        self.assertEqual(view["identifier"],"таб. № 001")

    def test_vehicle_snapshot_keeps_vin_and_plate(self):
        oid=self._order(ops.TYPE_MAINTENANCE_REPAIR)
        link=ops.add_order_entity(
            self.con,oid,ops.ORDER_ENTITY_VEHICLE,10,role="Транспортний засіб"
        )
        self.con.execute(
            "UPDATE vehicles SET plate='НОВИЙ',vin='CHANGEDVIN',make_model='Changed' WHERE id=10"
        )
        view=ops.order_entity_view(ops.get_order_entity(self.con,link))
        self.assertIn("BC0010AA",view["display"])
        self.assertIn("MAN Lion",view["display"])
        self.assertEqual(view["identifier"],"VIN WMA00000000000010")

    def test_driver_order_uses_driver_only_employee_pool(self):
        rows=ops.order_employee_choices(self.con,ops.TYPE_DRIVER_TRAINING,active_only=True)
        self.assertEqual([row["id"] for row in rows],[1])
        all_people=ops.order_employee_choices(self.con,ops.TYPE_OCCUPATIONAL_SAFETY,active_only=True)
        self.assertEqual([row["id"] for row in all_people],[1,2])

    def test_bulk_add_deduplicates_and_preserves_sequence(self):
        oid=self._order()
        created=ops.add_order_entities(
            self.con,oid,ops.ORDER_ENTITY_EMPLOYEE,[1,2,1],role="Учасник"
        )
        self.assertEqual(len(created),2)
        again=ops.add_order_entities(
            self.con,oid,ops.ORDER_ENTITY_EMPLOYEE,[1,2],role="Учасник"
        )
        self.assertEqual(again,[])
        rows=ops.list_order_entities(self.con,oid)
        self.assertEqual([row["entity_id"] for row in rows],[1,2])
        self.assertEqual([row["sequence_no"] for row in rows],[1,2])

    def test_inactive_entities_cannot_be_added_to_new_order(self):
        oid=self._order()
        with self.assertRaisesRegex(ValueError,"активних"):
            ops.add_order_entity(
                self.con,oid,ops.ORDER_ENTITY_EMPLOYEE,3,role="Працівник"
            )
        with self.assertRaisesRegex(ValueError,"активних"):
            ops.add_order_entity(
                self.con,oid,ops.ORDER_ENTITY_VEHICLE,20,role="ТЗ"
            )

    def test_approved_order_entities_can_be_corrected(self):
        oid=self._order()
        ops.add_order_entity(self.con,oid,ops.ORDER_ENTITY_EMPLOYEE,1,role="Працівник")
        ops.approve_order(self.con,oid)
        new_id=ops.add_order_entity(self.con,oid,ops.ORDER_ENTITY_EMPLOYEE,2,role="Працівник")
        self.assertIsNotNone(new_id)
        row=ops.list_order_entities(self.con,oid)[0]
        ops.delete_order_entity(self.con,row["id"])
        self.assertEqual(len(ops.list_order_entities(self.con,oid)),1)

    def test_assignment_order_uses_specialized_assignment_model(self):
        oid=ops.create_order(
            self.con,order_type=ops.TYPE_VEHICLE_ASSIGNMENT,order_no="2",
            order_date="08.11.2026"
        )
        with self.assertRaisesRegex(ValueError,"Закріплення водіїв"):
            ops.add_order_entity(
                self.con,oid,ops.ORDER_ENTITY_EMPLOYEE,1,role="Водій"
            )

    def test_removed_entity_remains_in_order_history(self):
        oid=self._order()
        link=ops.add_order_entity(
            self.con,oid,ops.ORDER_ENTITY_EMPLOYEE,1,role="Працівник"
        )
        ops.delete_order_entity(self.con,link,history_note="Тестове видалення")
        actions=[row["action"] for row in ops.order_history(self.con,oid)]
        self.assertIn("entity_add",actions)
        self.assertIn("entity_remove",actions)

    def test_ui_has_bulk_structured_entity_workflow(self):
        text=Path("src/taxo/operations_orders_ui.py").read_text(encoding="utf-8")
        for marker in (
            'text="Учасники / ТЗ"',
            'text="Додати працівників…"',
            'text="Додати ТЗ…"',
            'selectmode="extended"',
            "Пошук працює за ПІБ/табельним №/ідентифікатором",
        ):
            self.assertIn(marker,text)

    def test_pdf_layer_prints_structured_snapshot_table(self):
        text=Path("src/taxo/v1073_features.py").read_text(encoding="utf-8")
        self.assertIn("list_order_entities",text)
        self.assertIn("Структурований перелік працівників і транспортних засобів",text)
        self.assertIn("Однозначний реквізит",text)


if __name__=="__main__":
    unittest.main()
