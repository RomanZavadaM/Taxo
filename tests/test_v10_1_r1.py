# -*- coding: utf-8 -*-
import inspect
import sqlite3
import unittest

import branding
import main


def make_role_db():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE drivers(
            id INTEGER PRIMARY KEY,
            personnel_no TEXT,
            last_name TEXT,
            first_name TEXT,
            middle_name TEXT,
            employment_date TEXT,
            driver_end_date TEXT,
            notes TEXT,
            active INTEGER,
            created_at TEXT
        );
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY,
            personnel_no TEXT,
            last_name TEXT,
            first_name TEXT,
            middle_name TEXT,
            position TEXT,
            employment_date TEXT,
            dismissal_date TEXT,
            notes TEXT,
            active INTEGER,
            driver_id INTEGER,
            created_at TEXT
        );
        CREATE TABLE employee_roles(
            employee_id INTEGER,
            role TEXT,
            PRIMARY KEY(employee_id, role)
        );
        """
    )
    return con


def add_driver(con, *, active, end_date=""):
    con.execute(
        """INSERT INTO drivers(
               id,personnel_no,last_name,first_name,middle_name,employment_date,
               driver_end_date,notes,active,created_at
           ) VALUES(1,'001','Тест','Водій','','2020-01-01',?,'',?,'2020-01-01T00:00:00')""",
        (end_date, int(active)),
    )


def add_employee(con, *, active, dismissal="", with_role=False):
    con.execute(
        """INSERT INTO employees(
               id,personnel_no,last_name,first_name,middle_name,position,
               employment_date,dismissal_date,notes,active,driver_id,created_at
           ) VALUES(10,'001','Тест','Водій','','Працівник',
                    '2020-01-01',?,'',?,1,'2020-01-01T00:00:00')""",
        (dismissal, int(active)),
    )
    if with_role:
        con.execute(
            "INSERT INTO employee_roles(employee_id,role) VALUES(10,'Водій')"
        )


class TestDriverRoleSeparation(unittest.TestCase):
    def test_finished_driver_role_does_not_dismiss_employee_or_return_role(self):
        con = make_role_db()
        add_driver(con, active=False, end_date="2026-09-20")
        add_employee(con, active=True, with_role=False)
        dr = con.execute("SELECT * FROM drivers WHERE id=1").fetchone()

        main.sync_legacy_driver_employee(con, dr)

        employee = con.execute("SELECT * FROM employees WHERE id=10").fetchone()
        role = con.execute(
            "SELECT 1 FROM employee_roles WHERE employee_id=10 AND role='Водій'"
        ).fetchone()
        self.assertEqual(employee["active"], 1)
        self.assertIsNone(role)
        self.assertEqual(
            con.execute("SELECT driver_end_date FROM drivers WHERE id=1").fetchone()[0],
            "2026-09-20",
        )
        con.close()

    def test_old_startup_corruption_is_repaired_when_role_end_date_exists(self):
        con = make_role_db()
        add_driver(con, active=False, end_date="2026-09-20")
        add_employee(con, active=False, dismissal="", with_role=True)
        dr = con.execute("SELECT * FROM drivers WHERE id=1").fetchone()

        main.sync_legacy_driver_employee(con, dr)

        employee = con.execute("SELECT * FROM employees WHERE id=10").fetchone()
        roles = con.execute(
            "SELECT role FROM employee_roles WHERE employee_id=10"
        ).fetchall()
        self.assertEqual(employee["active"], 1)
        self.assertEqual(roles, [])
        con.close()

    def test_real_dismissal_is_not_undone_by_legacy_sync(self):
        con = make_role_db()
        add_driver(con, active=False, end_date="2026-09-20")
        add_employee(
            con, active=False, dismissal="2026-09-20", with_role=True
        )
        dr = con.execute("SELECT * FROM drivers WHERE id=1").fetchone()

        main.sync_legacy_driver_employee(con, dr)

        employee = con.execute("SELECT * FROM employees WHERE id=10").fetchone()
        self.assertEqual(employee["active"], 0)
        self.assertEqual(employee["dismissal_date"], "2026-09-20")
        self.assertIsNone(
            con.execute(
                "SELECT 1 FROM employee_roles WHERE employee_id=10 AND role='Водій'"
            ).fetchone()
        )
        con.close()

    def test_active_driver_role_is_backfilled_without_overwriting_employment(self):
        con = make_role_db()
        add_driver(con, active=True)
        add_employee(con, active=True, with_role=False)
        dr = con.execute("SELECT * FROM drivers WHERE id=1").fetchone()

        main.sync_legacy_driver_employee(con, dr)

        self.assertEqual(
            con.execute("SELECT active FROM employees WHERE id=10").fetchone()[0],
            1,
        )
        self.assertIsNotNone(
            con.execute(
                "SELECT 1 FROM employee_roles WHERE employee_id=10 AND role='Водій'"
            ).fetchone()
        )
        con.close()

    def test_employee_card_preserves_historical_driver_end_date(self):
        source = inspect.getsource(main.App.employee_form)
        self.assertIn("stored_driver_end", source)
        self.assertIn("next_driver_end=stored_driver_end", source)
        self.assertNotIn(
            'vals["employment_date"],"",vals["notes"],driver_active,driver_id',
            source,
        )

    def test_reemployment_does_not_reactivate_driver_role(self):
        source = inspect.getsource(main.App.toggle_employee_active)
        normalized = " ".join(source.split())
        self.assertIn("if row[\"driver_id\"] and new_state==0", normalized)
        self.assertNotIn(
            'UPDATE drivers SET active=? WHERE id=?',
            normalized,
        )


class TestBrandRefresh(unittest.TestCase):
    def test_brand_asset_has_no_fixed_company_name(self):
        source = inspect.getsource(branding)
        self.assertNotIn("АТП Завада", source)
        self.assertIn("Назва підприємства", source)

    def test_company_name_field_drives_header(self):
        source = inspect.getsource(main.App.build_company)
        self.assertIn('("name", "Назва підприємства")', source)
        self.assertIn('v.trace_add("write"', source)

    def test_icon_generator_creates_text_free_brand_image(self):
        image = branding.create_brand_image(128)
        self.assertEqual(image.size, (128, 128))
        self.assertEqual(image.mode, "RGBA")


if __name__ == "__main__":
    unittest.main()
