# -*- coding: utf-8 -*-
"""10.13-r5: shared identity-aware entity choices."""
import csv
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import entity_choices
import main
import operations_orders as ops
import safety_instructions_ui as brief


class SharedEntityChoicesR5Tests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.executescript(
            """
            CREATE TABLE employees(
                id INTEGER PRIMARY KEY,
                last_name TEXT, first_name TEXT, middle_name TEXT,
                position TEXT, personnel_no TEXT, rnokpp TEXT,
                active INTEGER DEFAULT 1, driver_id INTEGER
            );
            CREATE TABLE employee_roles(employee_id INTEGER, role TEXT);
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
                name TEXT, plate TEXT, make_model TEXT, vin TEXT,
                garage_no TEXT, active INTEGER DEFAULT 1
            );

            INSERT INTO employees VALUES
                (1,'Іваненко','Іван','','Водій','001','1111111111',1,11),
                (2,'Іваненко','Іван','','Механік','002','2222222222',1,NULL),
                (3,'Петренко','Петро','','Водій','','3333333333',1,33),
                (4,'Старий','Водій','','Водій','004','4444444444',0,44);
            INSERT INTO employee_roles VALUES(1,'Водій');
            INSERT INTO employee_roles VALUES(2,'Механік');
            INSERT INTO drivers VALUES(11,1,'');
            INSERT INTO drivers VALUES(33,1,'');
            INSERT INTO drivers VALUES(44,0,'2026-10-31');
            INSERT INTO employee_military_profile VALUES(1,'REG-001');

            INSERT INTO vehicles VALUES
                (10,'Автобус 10','BC0010AA','MAN Lion','WMA00000000000010','10',1),
                (20,'Автобус 20','BC0020AA','MAN Lion','WMA00000000000020','20',1),
                (30,'Старий автобус','BC0030AA','Mercedes','WDB00000000000030','30',0);
            """
        )

    def tearDown(self):
        self.con.close()

    def test_identity_is_10_13_r5_or_newer(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION), (10, 13, 5))

    def test_employee_choices_are_stable_and_identity_aware(self):
        rows = entity_choices.list_employee_choices(self.con, active_only=True)
        self.assertEqual([row["id"] for row in rows], [1, 2, 3])
        first = next(row for row in rows if row["id"] == 1)
        second = next(row for row in rows if row["id"] == 2)
        self.assertIn("таб. № 001", first["label"])
        self.assertIn("таб. № 002", second["label"])
        self.assertIn("1111111111", first["search_text"])
        self.assertEqual(first["registry_person_id"], "REG-001")
        self.assertEqual(first["snapshot"]["id"], 1)
        self.assertEqual(first["snapshot"]["rnokpp"], "1111111111")
        self.assertNotEqual(first["label"], second["label"])

    def test_employee_without_personnel_number_remains_identifiable(self):
        row = next(
            item for item in entity_choices.list_employee_choices(self.con)
            if item["id"] == 3
        )
        self.assertIn("РНОКПП", row["label"])
        self.assertIn("3333", row["label"])
        self.assertIn("3333333333", row["search_text"])

    def test_driver_choices_do_not_include_mechanic_or_inactive_driver(self):
        current = ops.list_driver_choices(self.con, active_only=True)
        self.assertEqual([row["id"] for row in current], [1, 3])
        historical = ops.list_driver_choices(self.con, active_only=False)
        self.assertEqual({row["id"] for row in historical}, {1, 3, 4})

    def test_vehicle_choices_carry_vin_plate_and_stable_snapshot(self):
        rows = ops.list_vehicle_choices(self.con, active_only=True)
        self.assertEqual([row["id"] for row in rows], [10, 20])
        first = rows[0]
        self.assertIn("BC0010AA", first["label"])
        self.assertIn("VIN WMA00000000000010", first["label"])
        self.assertEqual(first["snapshot"]["vin"], "WMA00000000000010")
        self.assertIn("wma00000000000010", first["search_text"])
        historical = ops.list_vehicle_choices(self.con, active_only=False)
        self.assertEqual({row["id"] for row in historical}, {10, 20, 30})

    def test_operations_wrappers_use_shared_contract(self):
        direct = entity_choices.list_employee_choices(self.con, active_only=True)
        through_operations = ops.list_employee_choices(self.con, active_only=True)
        self.assertEqual(through_operations, direct)

    def test_instruction_csv_keeps_database_identity_without_printing_rnokpp(self):
        employee = next(
            row for row in ops.list_employee_choices(self.con)
            if row["id"] == 1
        )
        prepared = brief.prepare_list(
            "Охорона праці",
            "Повторний",
            "08.11.2026",
            "Інструкція з охорони праці",
            [employee["name"]],
            people_records=[employee],
        )
        with TemporaryDirectory() as directory:
            target = Path(directory) / "briefing.csv"
            brief.write_preparation_csv(target, prepared)
            with target.open("r", encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.reader(stream, delimiter=";"))
        self.assertEqual(rows[-2], ["№", "Працівник", "Табельний №", "Код Taxo"])
        self.assertEqual(rows[-1], ["1", "Іваненко Іван", "001", "1"])
        self.assertNotIn("1111111111", "\n".join(";".join(row) for row in rows))


if __name__ == "__main__":
    unittest.main()
