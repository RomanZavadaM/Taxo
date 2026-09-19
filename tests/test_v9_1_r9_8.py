# -*- coding: utf-8 -*-
import inspect
import sqlite3
import unittest
from datetime import date

import main


def make_staff_db():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY,
            last_name TEXT,
            first_name TEXT,
            middle_name TEXT,
            active INTEGER
        );
        CREATE TABLE employee_shifts(
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            role TEXT,
            work_date TEXT,
            shift_no INTEGER,
            start_time TEXT,
            end_day_offset INTEGER,
            end_time TEXT,
            location TEXT,
            actual_hours REAL
        );
        CREATE TABLE employee_time_entries(
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            work_date TEXT,
            day_type TEXT
        );
        """
    )
    return con


def add_employee(con, employee_id, last_name, first_name):
    con.execute(
        "INSERT INTO employees(id,last_name,first_name,middle_name,active) VALUES(?,?,?,?,1)",
        (employee_id, last_name, first_name, ""),
    )


def add_shift(
    con, shift_id, employee_id, role, work_date, shift_no,
    start_time="06:00", end_time="18:00", end_day_offset=0, location=""
):
    con.execute(
        """INSERT INTO employee_shifts(
               id,employee_id,role,work_date,shift_no,start_time,
               end_day_offset,end_time,location,actual_hours
           ) VALUES(?,?,?,?,?,?,?,?,?,NULL)""",
        (
            shift_id, employee_id, role, work_date, shift_no, start_time,
            end_day_offset, end_time, location,
        ),
    )


class TestR98WaybillDutyStaff(unittest.TestCase):
    def test_waybill_staff_is_bound_to_schedule_date_not_next_day(self):
        con = make_staff_db()
        add_employee(con, 1, "Лікар", "Двадцятого")
        add_employee(con, 2, "Механік", "Двадцятого")
        add_employee(con, 3, "Лікар", "ДвадцятьПершого")
        add_employee(con, 4, "Механік", "ДвадцятьПершого")

        add_shift(con, 1, 1, "Лікар", "2026-09-20", 1, "06:00", "18:00")
        add_shift(con, 2, 2, "Механік", "2026-09-20", 1, "06:00", "18:00")
        add_shift(con, 3, 3, "Лікар", "2026-09-21", 1, "06:00", "18:00")
        add_shift(con, 4, 4, "Механік", "2026-09-21", 1, "06:00", "18:00")
        con.commit()

        app = object.__new__(main.App)
        duty = main.App._duty_staff_for_work_date(
            app, date(2026, 9, 20), con
        )
        con.close()

        self.assertEqual(duty["doctor_1"], "Лікар Двадцятого")
        self.assertEqual(duty["mechanic_1"], "Механік Двадцятого")
        self.assertNotIn("ДвадцятьПершого", duty["doctor_1"])
        self.assertNotIn("ДвадцятьПершого", duty["mechanic_1"])
        self.assertEqual(duty["staff_conflicts"], [])

    def test_legacy_duplicate_same_role_date_shift_is_explicit_conflict(self):
        con = make_staff_db()
        add_employee(con, 1, "Лікар", "Перший")
        add_employee(con, 2, "Лікар", "Другий")
        add_shift(
            con, 1, 1, "Лікар", "2026-09-20", 1,
            "06:00", "18:00", location="Гараж А"
        )
        add_shift(
            con, 2, 2, "Лікар", "2026-09-20", 1,
            "06:00", "18:00", location="Гараж Б"
        )
        con.commit()

        app = object.__new__(main.App)
        duty = main.App._duty_staff_for_work_date(
            app, date(2026, 9, 20), con
        )
        con.close()

        self.assertEqual(duty["doctor_1"], "")
        self.assertEqual(len(duty["staff_conflicts"]), 1)
        self.assertIn("Лікар I: 2 призначення", duty["staff_conflicts"][0])
        self.assertIn("Лікар Перший", duty["staff_conflicts"][0])
        self.assertIn("Лікар Другий", duty["staff_conflicts"][0])

    def test_waybill_rows_compute_one_day_duty_before_row_loop(self):
        source = inspect.getsource(main.App._waybill_schedule_rows)
        self.assertIn(
            "day_duty=self._duty_staff_for_work_date(work_date,con)",
            source,
        )
        self.assertIn("duty=day_duty", source)
        self.assertNotIn(
            "_duty_staff_for_interval(start_dt,end_dt,start_location,con)",
            source,
        )

    def test_manual_shift_slot_no_longer_depends_on_location(self):
        source = inspect.getsource(main.App.dispatch_shift_form)
        normalized = " ".join(source.split())
        self.assertIn(
            "SELECT id FROM employee_shifts WHERE role=? AND shift_no=? AND work_date=? AND id<>?",
            normalized,
        )
        self.assertNotIn(
            "role=? AND shift_no=? AND work_date=? AND lower(COALESCE(location",
            normalized,
        )


if __name__ == "__main__":
    unittest.main()
