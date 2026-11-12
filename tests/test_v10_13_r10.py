# -*- coding: utf-8 -*-
"""Taxo 10.13-r10: visible order preview and print workflow."""
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
            (3,'Завада','Тарас','Йосипович','Інженер','010','3333333333',1,NULL);
        INSERT INTO employee_roles VALUES(1,'Водій'),(2,'Водій');
        INSERT INTO drivers VALUES(11,1,''),(22,1,'');
        INSERT INTO vehicles VALUES
            (10,'Автобус 10','BC0010AA','MAN Lion','VIN00000000000010','10',1);
        """
    )
    ops.ensure_schema_on_connection(con)
    con.commit()
    return con


class TaxoR10OrderPreviewTests(unittest.TestCase):
    def setUp(self):
        self.con=make_db()

    def tearDown(self):
        self.con.close()

    def test_identity_is_10_13_r10_or_newer(self):
        self.assertIn(main.APP_VERSION, ("10.13-r10", "10.14-r1", "10.14-r2", "10.14-r3", "10.14-r4", "10.14-r5", "10.14-r6", "10.14-r7", "10.14-r8", "10.14-r9", "10.14-r10", "10.15-r1", "10.15-r2", "10.15-r3", "10.15-r4", "10.15-r5", "10.15-r7", "10.15-r8", "10.15-r9", "10.15-r10", "10.16-r1", "10.16-r2", "10.16-r3", "10.16-r4", "10.16-r5", "10.16-r6", "10.16-r7", "10.16-r8", "10.16-r9", "10.16-r10", "10.17-r1", "10.17-r2", "10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6", "10.17-r7", "10.17-r8", "10.17-r9", "10.17-r10", "10.18-r1"))
        self.assertIn(main.APP_VERSION,Path("VERSION.txt").read_text(encoding="utf-8"))
        self.assertIn("Taxo " + main.APP_VERSION,Path("START.bat").read_text(encoding="utf-8"))

    def test_assignment_order_preview_contains_printable_content_and_all_pairs(self):
        oid=ops.create_vehicle_assignment_order(
            self.con,
            order_date="08.11.2026",
            place="с. Муроване",
            subject="Про закріплення автотранспортних засобів",
            preamble="Для виконання виробничих завдань —",
            control_employee_id=3,
            initial_pairs=[(10,1),(10,2)],
        )
        order=ops.get_order(self.con,oid)
        assignments=ops.order_assignments(self.con,oid)
        preview=ops.order_preview_text(
            order,
            assignments=assignments,
            company={"name":"Тестове підприємство","signer_position":"Директор","signer_name":"Керівник"},
            control_name="Завада Тарас Йосипович",
        )
        for marker in (
            "Н А К А З",
            "по Тестове підприємство",
            "08.11.2026",
            "№ 1",
            "с. Муроване",
            "Про закріплення автотранспортних засобів",
            "Н А К А З У Ю:",
            "MAN Lion; BC0010AA — Іваненко Іван",
            "MAN Lion; BC0010AA — Петренко Петро",
            "Контроль за виконанням даного наказу покласти на Завада Тарас Йосипович",
            "Директор    ________________    Керівник",
        ):
            self.assertIn(marker,preview)

    def test_preview_handles_assignment_without_pairs(self):
        oid=ops.create_vehicle_assignment_order(self.con,order_date="08.11.2026")
        preview=ops.order_preview_text(
            ops.get_order(self.con,oid),
            assignments=[],
            company={"name":"Підприємство"},
        )
        self.assertIn("(закріплення ще не додані)",preview)

    def test_orders_ui_exposes_preview_print_and_auto_opens_created_order(self):
        text=Path("src/taxo/operations_orders_ui.py").read_text(encoding="utf-8")
        text += Path("src/taxo/order_register_ui.py").read_text(encoding="utf-8")
        text += Path("src/taxo/order_editor_ui.py").read_text(encoding="utf-8")
        text+=Path("src/taxo/order_preview_ui.py").read_text(encoding="utf-8")
        for marker in (
            "Переглянути / друк",
            "Сформувати PDF / друк",
            'dlg.title("Перегляд наказу №%s"',
            "preview_order(created_order)",
            "book.select(orders_tab)",
            'order_tree.bind("<Double-1>",lambda _e:preview_order()',
            "Перевірте зміст наказу.",
        ):
            self.assertIn(marker,text)


if __name__=="__main__":
    unittest.main()
