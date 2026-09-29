# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import unittest
from pathlib import Path

import operations_orders as ops


class OperationsSchemaTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.executescript(
            """
            CREATE TABLE employees(
                id INTEGER PRIMARY KEY,
                last_name TEXT,first_name TEXT,middle_name TEXT,
                position TEXT,active INTEGER DEFAULT 1,birth_date TEXT,
                actual_address TEXT,registered_address TEXT
            );
            CREATE TABLE employee_military_profile(
                employee_id INTEGER PRIMARY KEY,
                military_specialty TEXT DEFAULT '',military_rank TEXT DEFAULT ''
            );
            CREATE TABLE vehicles(
                id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT,active INTEGER DEFAULT 1
            );
            CREATE TABLE company(
                id INTEGER PRIMARY KEY,name TEXT,address TEXT,phone TEXT,email TEXT,
                signer_name TEXT,signer_position TEXT
            );
            INSERT INTO employees VALUES(1,'Дробот','Олег','Васильович','водій',1,'1980-01-01','Львів','Львів');
            INSERT INTO employees VALUES(2,'Мелих','Юрій','Васильович','інженер',1,'1975-01-01','','');
            INSERT INTO employee_military_profile VALUES(1,'837037','солдат');
            INSERT INTO vehicles VALUES(10,'БАЗ А079','BC 3687 OH','БАЗ А079',1);
            INSERT INTO company VALUES(1,'ПП АТП Завада','с. Муроване','','','Завада Р.М.','Директор');
            """
        )
        ops.ensure_schema_on_connection(self.con)
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def _order(self):
        return ops.create_order(
            self.con,
            order_type=ops.TYPE_VEHICLE_ASSIGNMENT,
            order_no='9',
            order_date='17.05.2023',
            place='с. Муроване',
            control_employee_id=2,
        )

    def test_assignment_becomes_operational_only_after_order_approval(self):
        order_id = self._order()
        ops.add_vehicle_assignment(
            self.con, order_id, 10, 1, valid_from='18.05.2023'
        )
        self.assertEqual(ops.active_driver_assignments(self.con, 10, '2023-05-18'), [])
        ops.approve_order(self.con, order_id)
        rows = ops.active_driver_assignments(self.con, 10, '2023-05-18')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['last_name'], 'Дробот')
        self.assertEqual(rows[0]['order_no'], '9')

    def test_assignment_honours_validity_window(self):
        order_id = self._order()
        ops.add_vehicle_assignment(
            self.con, order_id, 10, 1, valid_from='18.05.2023', valid_until='31.05.2023'
        )
        ops.approve_order(self.con, order_id)
        self.assertEqual(len(ops.active_driver_assignments(self.con, 10, '2023-05-31')), 1)
        self.assertEqual(len(ops.active_driver_assignments(self.con, 10, '2023-06-01')), 0)

    def test_statement_approval_is_invalidated_when_rows_change(self):
        company = {'name':'ПП АТП Завада','address':'с. Муроване','phone':'','email':'','signer_name':'Завада Р.М.','signer_position':'Директор'}
        rows = [{'plate':'BC 3687 OH','worker_name':'Дробот О.В.'}]
        ops.approve_military_statement(self.con, '20.12.2026', company, rows, 2)
        ok, approval = ops.military_statement_is_approved(self.con, '20.12.2026', company, rows)
        self.assertTrue(ok)
        self.assertIsNotNone(approval)
        changed = [{'plate':'BC 3687 OH','worker_name':'Інший водій'}]
        ok, approval = ops.military_statement_is_approved(self.con, '20.12.2026', company, changed)
        self.assertFalse(ok)
        self.assertIsNotNone(approval)

    def test_operations_settings_store_both_responsible_roles(self):
        ops.save_settings(
            self.con,
            operations_responsible_employee_id=2,
            military_transport_responsible_employee_id=2,
            order_place='с. Муроване',
        )
        row = ops.settings(self.con)
        self.assertEqual(row['operations_responsible_employee_id'], 2)
        self.assertEqual(row['military_transport_responsible_employee_id'], 2)
        self.assertEqual(row['order_place'], 'с. Муроване')

    def test_order_pdf_smoke_matches_enterprise_order_structure(self):
        order_id = self._order()
        ops.add_vehicle_assignment(self.con, order_id, 10, 1, valid_from='18.05.2023')
        order = ops.get_order(self.con, order_id)
        assignments = ops.order_assignments(self.con, order_id)
        company = dict(self.con.execute('SELECT * FROM company WHERE id=1').fetchone())
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'order.pdf'
            ops.export_order_pdf(path, order, assignments, company, control_name='Мелих Ю.В.')
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 500)


class R2IntegrationTests(unittest.TestCase):
    def test_version_file_is_r2(self):
        text = Path('VERSION.txt').read_text(encoding='utf-8')
        self.assertIn('Version: 10.7-r2', text)

    def test_taxo_app_installs_r2_outermost(self):
        text = Path('taxo_app.py').read_text(encoding='utf-8')
        self.assertIn('from v1072_features import install as install_v1072', text)
        self.assertIn('App = install_v1072(core, App)', text)
        self.assertLess(text.index('App = install_v1071(core, App)'), text.index('App = install_v1072(core, App)'))

    def test_start_package_requires_operations_runtime(self):
        text = Path('.github/workflows/source-test-archive.yml').read_text(encoding='utf-8')
        for name in ('operations_orders.py','operations_orders_ui.py','v1072_features.py'):
            self.assertIn(name, text)

    def test_r2_layer_does_not_put_registry_source_label_into_official_form(self):
        text = Path('v1072_features.py').read_text(encoding='utf-8')
        self.assertNotIn('Дані реєстру/Дія від', text)
        self.assertIn('Затвердити дані відомості', text)


if __name__ == '__main__':
    unittest.main()
