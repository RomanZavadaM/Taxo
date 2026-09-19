# -*- coding: utf-8 -*-
import sqlite3
import unittest
from pathlib import Path

import main
from release_naming import start_archive_stem


def make_conn():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE drivers(
            id INTEGER PRIMARY KEY,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT DEFAULT '',
            personnel_no TEXT DEFAULT '',
            employment_date TEXT DEFAULT '',
            driver_end_date TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT ''
        );
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_no TEXT DEFAULT '',
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT DEFAULT '',
            position TEXT DEFAULT '',
            employment_date TEXT DEFAULT '',
            dismissal_date TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            active INTEGER NOT NULL DEFAULT 1,
            driver_id INTEGER UNIQUE,
            created_at TEXT NOT NULL
        );
        CREATE TABLE employee_roles(
            employee_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            PRIMARY KEY(employee_id, role)
        );
        """
    )
    return con


class TestDriverRoleLifecycle1001R1(unittest.TestCase):
    def test_startup_bridge_does_not_resurrect_removed_driver_role(self):
        con = make_conn()
        con.execute(
            """INSERT INTO drivers(
                   id,last_name,first_name,middle_name,personnel_no,
                   employment_date,driver_end_date,notes,active,created_at
               ) VALUES(1,'Завада','Тарас','Йосипович','2678111477',
                        '2025-07-19','2026-09-20','',0,'2025-07-19T00:00:00')"""
        )
        con.execute(
            """INSERT INTO employees(
                   id,personnel_no,last_name,first_name,middle_name,position,
                   employment_date,dismissal_date,notes,active,driver_id,created_at
               ) VALUES(10,'2678111477','Завада','Тарас','Йосипович',
                        'Інженер з транспорту','2025-07-19','','',1,1,'2025-07-19T00:00:00')"""
        )
        con.execute("INSERT INTO employee_roles(employee_id,role) VALUES(10,'Механік')")
        dr = con.execute("SELECT * FROM drivers WHERE id=1").fetchone()

        employee_id, created = main.ensure_legacy_driver_employee(con, dr)

        self.assertEqual(employee_id, 10)
        self.assertFalse(created)
        employee = con.execute("SELECT * FROM employees WHERE id=10").fetchone()
        self.assertEqual(employee["active"], 1)
        roles = {
            row["role"]
            for row in con.execute(
                "SELECT role FROM employee_roles WHERE employee_id=10"
            ).fetchall()
        }
        self.assertEqual(roles, {"Механік"})
        self.assertNotIn("Водій", roles)

    def test_first_legacy_migration_still_creates_driver_employee(self):
        con = make_conn()
        con.execute(
            """INSERT INTO drivers(
                   id,last_name,first_name,middle_name,personnel_no,
                   employment_date,driver_end_date,notes,active,created_at
               ) VALUES(2,'Тестовий','Водій','','D2',
                        '2026-01-01','','',1,'2026-01-01T00:00:00')"""
        )
        dr = con.execute("SELECT * FROM drivers WHERE id=2").fetchone()

        employee_id, created = main.ensure_legacy_driver_employee(con, dr)

        self.assertTrue(created)
        employee = con.execute(
            "SELECT * FROM employees WHERE id=?", (employee_id,)
        ).fetchone()
        self.assertEqual(employee["active"], 1)
        self.assertEqual(employee["driver_id"], 2)
        self.assertTrue(
            con.execute(
                "SELECT 1 FROM employee_roles WHERE employee_id=? AND role='Водій'",
                (employee_id,),
            ).fetchone()
        )

    def test_finishing_driver_role_does_not_fire_employee(self):
        con = make_conn()
        con.execute(
            """INSERT INTO drivers(
                   id,last_name,first_name,middle_name,personnel_no,
                   employment_date,driver_end_date,notes,active,created_at
               ) VALUES(3,'Працівник','Один','','E3',
                        '2020-01-01','','',1,'2020-01-01T00:00:00')"""
        )
        con.execute(
            """INSERT INTO employees(
                   id,personnel_no,last_name,first_name,middle_name,position,
                   employment_date,dismissal_date,notes,active,driver_id,created_at
               ) VALUES(30,'E3','Працівник','Один','','Інженер',
                        '2020-01-01','','',1,3,'2020-01-01T00:00:00')"""
        )
        con.execute("INSERT INTO employee_roles(employee_id,role) VALUES(30,'Водій')")
        con.execute("INSERT INTO employee_roles(employee_id,role) VALUES(30,'Механік')")

        main.finish_driver_role(con, 30, 3, "2026-09-20")

        employee = con.execute("SELECT * FROM employees WHERE id=30").fetchone()
        driver = con.execute("SELECT * FROM drivers WHERE id=3").fetchone()
        self.assertEqual(employee["active"], 1)
        self.assertEqual(employee["dismissal_date"], "")
        self.assertEqual(driver["active"], 0)
        self.assertEqual(driver["driver_end_date"], "2026-09-20")
        roles = {
            row["role"]
            for row in con.execute(
                "SELECT role FROM employee_roles WHERE employee_id=30"
            ).fetchall()
        }
        self.assertEqual(roles, {"Механік"})

    def test_subsequent_employee_save_preserves_driver_role_end_date(self):
        con = make_conn()
        con.execute(
            """INSERT INTO drivers(
                   id,last_name,first_name,middle_name,personnel_no,
                   employment_date,driver_end_date,notes,active,created_at
               ) VALUES(4,'Працівник','Два','','E4',
                        '2020-01-01','2026-09-20','old',0,'2020-01-01T00:00:00')"""
        )
        con.execute(
            """INSERT INTO employees(
                   id,personnel_no,last_name,first_name,middle_name,position,
                   employment_date,dismissal_date,notes,active,driver_id,created_at
               ) VALUES(40,'E4','Працівник','Два','','Інженер',
                        '2020-01-01','','',1,4,'2020-01-01T00:00:00')"""
        )

        main.sync_employee_driver_role(
            con,
            40,
            4,
            last_name="Працівник",
            first_name="Два",
            middle_name="",
            personnel_no="E4",
            employment_date="2020-01-01",
            notes="updated",
            employee_active=True,
            has_driver_role=False,
            closing_driver=False,
            driver_end_date="",
        )

        driver = con.execute("SELECT * FROM drivers WHERE id=4").fetchone()
        self.assertEqual(driver["active"], 0)
        self.assertEqual(driver["driver_end_date"], "2026-09-20")
        self.assertEqual(driver["notes"], "updated")

    def test_rehire_does_not_restore_driver_role_if_role_was_removed(self):
        con = make_conn()
        con.execute(
            """INSERT INTO drivers(
                   id,last_name,first_name,middle_name,personnel_no,
                   employment_date,driver_end_date,notes,active,created_at
               ) VALUES(5,'Працівник','Три','','E5',
                        '2020-01-01','2026-09-20','',0,'2020-01-01T00:00:00')"""
        )
        con.execute(
            """INSERT INTO employees(
                   id,personnel_no,last_name,first_name,middle_name,position,
                   employment_date,dismissal_date,notes,active,driver_id,created_at
               ) VALUES(50,'E5','Працівник','Три','','Юрисконсульт',
                        '2020-01-01','2026-09-19','',0,5,'2020-01-01T00:00:00')"""
        )
        con.execute("INSERT INTO employee_roles(employee_id,role) VALUES(50,'Інше')")

        main.set_employee_active_state(con, 50, 1, "2026-09-20")

        employee = con.execute("SELECT * FROM employees WHERE id=50").fetchone()
        driver = con.execute("SELECT * FROM drivers WHERE id=5").fetchone()
        self.assertEqual(employee["active"], 1)
        self.assertEqual(employee["dismissal_date"], "")
        self.assertEqual(driver["active"], 0)
        self.assertEqual(driver["driver_end_date"], "2026-09-20")
        self.assertFalse(
            con.execute(
                "SELECT 1 FROM employee_roles WHERE employee_id=50 AND role='Водій'"
            ).fetchone()
        )

    def test_patch_candidate_archive_name_keeps_patch_number(self):
        self.assertEqual(
            start_archive_stem("10.0.1 candidate r1"),
            "Taxo_v10_0_1_candidate_r1_START",
        )


if __name__ == "__main__":
    unittest.main()
