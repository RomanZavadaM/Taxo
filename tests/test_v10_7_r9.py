# -*- coding: utf-8 -*-
import sqlite3
import unittest

import operations_orders as ops
import v1079_features as r9


class DummyCore:
    APP_VERSION = "old"


class Taxo107R9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = DummyCore()
        r9.install(cls.core, object)

    def test_version_identity(self):
        self.assertEqual(r9.APP_VERSION, "10.7-r9")
        self.assertEqual(self.core.APP_VERSION, "10.7-r9")

    def test_new_real_world_order_types_registered(self):
        self.assertIn(r9.TYPE_RESPONSIBLE_PERSONS, ops.ORDER_TYPE_LABELS)
        self.assertIn(r9.TYPE_VEHICLE_RELEASE_RETURN, ops.ORDER_TYPE_LABELS)
        self.assertIn(r9.TYPE_SEASONAL_OPERATION, ops.ORDER_TYPE_LABELS)
        self.assertEqual(ops.ORDER_TYPE_GROUP[r9.TYPE_VEHICLE_RELEASE_RETURN], ops.ORDER_GROUP_VEHICLES)
        self.assertEqual(ops.ORDER_TYPE_GROUP[r9.TYPE_SEASONAL_OPERATION], ops.ORDER_GROUP_VEHICLES)

    def test_existing_operational_types_have_editable_templates(self):
        expected = (
            ops.TYPE_STORAGE, ops.TYPE_WORKTIME, ops.TYPE_REST_PLACES,
            ops.TYPE_DRIVER_TRAINING, ops.TYPE_SAFETY_TRAINING,
            ops.TYPE_ROAD_SAFETY, ops.TYPE_TECHNICAL_CONTROL,
            ops.TYPE_MAINTENANCE_REPAIR, ops.TYPE_ACCIDENT_COMMISSION,
            ops.TYPE_OCCUPATIONAL_SAFETY, ops.TYPE_FIRE_SAFETY,
        )
        for order_type in expected:
            self.assertTrue(ops.DEFAULT_BODY_TEMPLATES.get(order_type, "").strip(), order_type)

    def test_create_order_prefills_template_only_when_body_is_blank(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute("CREATE TABLE employees(id INTEGER PRIMARY KEY, last_name TEXT, first_name TEXT, middle_name TEXT, position TEXT, active INTEGER)")
        con.execute("CREATE TABLE vehicles(id INTEGER PRIMARY KEY, name TEXT, plate TEXT, make_model TEXT, active INTEGER)")
        ops.ensure_schema_on_connection(con)

        oid = ops.create_order(
            con, order_type=ops.TYPE_MAINTENANCE_REPAIR,
            order_no="1", order_date="30.09.2026",
        )
        row = ops.get_order(con, oid)
        self.assertEqual(row["body_text"], ops.DEFAULT_BODY_TEMPLATES[ops.TYPE_MAINTENANCE_REPAIR])

        oid2 = ops.create_order(
            con, order_type=ops.TYPE_MAINTENANCE_REPAIR,
            order_no="2", order_date="30.09.2026", body_text="Власний текст користувача",
        )
        row2 = ops.get_order(con, oid2)
        self.assertEqual(row2["body_text"], "Власний текст користувача")
        con.close()

    def test_templates_do_not_hardcode_legal_article_numbers(self):
        text = "\n".join(ops.DEFAULT_BODY_TEMPLATES.values())
        self.assertNotIn("статті ", text.lower())
        self.assertNotIn("пункту ", text.lower())


if __name__ == "__main__":
    unittest.main()
