# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import unittest
from pathlib import Path

import operations_orders as ops
import v1073_features as r3


class _Core:
    def __init__(self, db_path):
        self.db_path = str(db_path)

    def db(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con


class OrderAppendixR3Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "taxo.sqlite"
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        con.execute("CREATE TABLE employees(id INTEGER PRIMARY KEY,last_name TEXT,first_name TEXT,middle_name TEXT,position TEXT,active INTEGER DEFAULT 1)")
        con.execute("CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT,active INTEGER DEFAULT 1)")
        con.execute("CREATE TABLE employee_military_profile(employee_id INTEGER PRIMARY KEY,military_specialty TEXT,military_rank TEXT)")
        ops.ensure_schema_on_connection(con)
        r3.ensure_appendix_schema_on_connection(con)
        self.order_id = ops.create_order(
            con,
            order_type=ops.TYPE_GENERIC,
            order_no="12",
            order_date="29.09.2026",
            place="Львів",
            subject="Про проведення навчання",
            preamble="З метою належної організації роботи —",
            body_text="1. Провести навчання.\n2. Відповідальному забезпечити виконання.",
        )
        con.commit()
        con.close()

    def tearDown(self):
        self.tmp.cleanup()

    def _con(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def test_appendices_are_structured_and_ordered(self):
        con = self._con()
        try:
            first = r3.save_appendix(con, self.order_id, title="Тематика №1", content="Питання 1\nПитання 2")
            second = r3.save_appendix(con, self.order_id, title="Тематика №2", content="Питання 3")
            con.commit()
            rows = r3.list_appendices(con, self.order_id)
            self.assertEqual([row["id"] for row in rows], [first, second])
            self.assertEqual([row["sequence_no"] for row in rows], [1, 2])
            self.assertEqual(rows[0]["title"], "Тематика №1")
        finally:
            con.close()

    def test_approved_order_appendices_are_immutable(self):
        con = self._con()
        try:
            appendix_id = r3.save_appendix(con, self.order_id, title="Додаток", content="Зміст")
            ops.approve_order(con, self.order_id)
            con.commit()
            with self.assertRaises(ValueError):
                r3.save_appendix(con, self.order_id, title="Змінено", content="Інший зміст", appendix_id=appendix_id)
            with self.assertRaises(ValueError):
                r3.delete_appendix(con, self.order_id, appendix_id)
        finally:
            con.close()

    def test_order_pdf_with_appendix_smoke(self):
        con = self._con()
        try:
            r3.save_appendix(
                con,
                self.order_id,
                title="Тематика занять з охорони праці",
                content="1. Загальні вимоги безпеки.\n2. Дії у разі аварійної ситуації.",
            )
            con.commit()
            order = ops.get_order(con, self.order_id)
        finally:
            con.close()
        output = Path(self.tmp.name) / "order.pdf"
        r3.export_order_pdf_with_appendices(
            _Core(self.db_path),
            output,
            order,
            assignments=(),
            company={"name": "Тестове підприємство", "signer_position": "Директор", "signer_name": "Іван Іванов"},
        )
        self.assertTrue(output.exists())
        self.assertGreater(output.stat().st_size, 1500)


class R3IntegrationTests(unittest.TestCase):
    def test_feature_identity(self):
        self.assertEqual(r3.APP_VERSION, "10.7-r3")

    def test_taxo_app_installs_r3_outermost(self):
        text = Path("taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from v1073_features import install as install_v1073", text)
        self.assertIn("App = install_v1073(core, App)", text)

    def test_r2_form_provenance_rule_is_preserved(self):
        text = Path("v1072_features.py").read_text(encoding="utf-8")
        self.assertNotIn("Дані реєстру/Дія від", text)


if __name__ == "__main__":
    unittest.main()
