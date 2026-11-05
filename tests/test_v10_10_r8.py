# -*- coding: utf-8 -*-
"""Taxo 10.10-r8 — simple monthly schedule and employee-facing privacy."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

import personnel_month_schedule_r8 as schedule


def make_db():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            last_name TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            middle_name TEXT DEFAULT '',
            personnel_no TEXT DEFAULT '',
            position TEXT DEFAULT '',
            employment_date TEXT DEFAULT '',
            dismissal_date TEXT DEFAULT '',
            active INTEGER DEFAULT 1,
            driver_id INTEGER
        );
        CREATE TABLE employee_roles (
            employee_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            UNIQUE(employee_id, role)
        );
        CREATE TABLE employee_shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            work_date TEXT NOT NULL,
            shift_no INTEGER NOT NULL DEFAULT 1,
            start_time TEXT NOT NULL,
            end_day_offset INTEGER NOT NULL DEFAULT 0,
            end_time TEXT NOT NULL,
            location TEXT DEFAULT '',
            unpaid_break_minutes INTEGER NOT NULL DEFAULT 0,
            planned_hours REAL NOT NULL DEFAULT 0,
            actual_hours REAL,
            status TEXT NOT NULL DEFAULT 'planned',
            notes TEXT DEFAULT '',
            UNIQUE(employee_id, role, work_date, shift_no)
        );
        CREATE TABLE employee_time_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            work_date TEXT NOT NULL,
            day_type TEXT NOT NULL DEFAULT 'Робота',
            planned_hours REAL,
            actual_hours REAL,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT DEFAULT '',
            UNIQUE(employee_id, work_date)
        );
        """
    )
    con.execute(
        """INSERT INTO employees(id,last_name,first_name,personnel_no,position,active,driver_id)
           VALUES(1,'Контролер','Олена','001','Контролер',1,NULL)"""
    )
    con.execute("INSERT INTO employee_roles(employee_id,role) VALUES(1,'Контролер')")
    con.execute(
        """INSERT INTO employees(id,last_name,first_name,personnel_no,position,active,driver_id)
           VALUES(2,'Механік','Ігор','002','Механік',1,NULL)"""
    )
    con.execute("INSERT INTO employee_roles(employee_id,role) VALUES(2,'Механік')")
    con.execute(
        """INSERT INTO employees(id,last_name,first_name,personnel_no,position,active,driver_id)
           VALUES(3,'Водій','Петро','003','Водій',1,33)"""
    )
    con.execute("INSERT INTO employee_roles(employee_id,role) VALUES(3,'Водій')")
    con.commit()
    return con


class CoreStub:
    @staticmethod
    def employee_employed_on(_employee, _day):
        return True

    @staticmethod
    def employee_day_time(con, employee_id, target_date):
        absence = con.execute(
            "SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",
            (employee_id, target_date.isoformat()),
        ).fetchone()
        if absence and absence["day_type"] != "Робота":
            return {
                "day_type": absence["day_type"],
                "planned_minutes": 0,
                "actual_minutes": absence["actual_hours"],
                "source": "manual",
                "notes": absence["notes"],
                "manual": True,
            }
        rows = con.execute(
            "SELECT * FROM employee_shifts WHERE employee_id=? AND work_date=?",
            (employee_id, target_date.isoformat()),
        ).fetchall()
        planned = int(round(sum(float(r["planned_hours"] or 0) for r in rows) * 60))
        return {
            "day_type": "Робота" if planned else "Вихідний",
            "planned_minutes": planned,
            "actual_minutes": None,
            "source": "shift" if planned else "—",
            "notes": "",
            "manual": False,
        }


class SimpleScheduleR8Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()

    def tearDown(self):
        self.con.close()

    def test_three_on_three_pattern(self):
        dates = schedule.selected_pattern_dates(2026, 11, schedule.PATTERN_3_3)
        self.assertEqual(
            [d.day for d in dates[:8]],
            [1, 2, 3, 7, 8, 9, 13, 14],
        )

    def test_plan_applies_only_to_selected_employee(self):
        result = schedule.apply_simple_month_plan(
            CoreStub,
            self.con,
            [1],
            2026,
            11,
            pattern=schedule.PATTERN_2_2,
            start_time="08:00",
            end_time="17:00",
            unpaid_break_minutes=60,
        )
        self.con.commit()
        self.assertGreater(result["added"], 0)
        self.assertEqual(
            self.con.execute("SELECT COUNT(*) FROM employee_shifts WHERE employee_id=2").fetchone()[0],
            0,
        )
        first = self.con.execute(
            "SELECT * FROM employee_shifts WHERE employee_id=1 ORDER BY work_date LIMIT 1"
        ).fetchone()
        self.assertEqual(first["role"], "Контролер")
        self.assertEqual(first["planned_hours"], 8.0)

    def test_driver_only_employee_is_not_duplicated_into_personnel_shifts(self):
        result = schedule.apply_simple_month_plan(
            CoreStub,
            self.con,
            [3],
            2026,
            11,
            pattern=schedule.PATTERN_WEEKDAYS,
        )
        self.con.commit()
        self.assertEqual(result["added"], 0)
        self.assertGreater(result["skipped_driver"], 0)
        self.assertEqual(
            self.con.execute("SELECT COUNT(*) FROM employee_shifts WHERE employee_id=3").fetchone()[0],
            0,
        )

    def test_existing_fact_is_never_overwritten(self):
        self.con.execute(
            """INSERT INTO employee_shifts(
                   employee_id,role,work_date,shift_no,start_time,end_day_offset,end_time,
                   unpaid_break_minutes,planned_hours,actual_hours,status,notes
               ) VALUES(1,'Контролер','2026-11-02',1,'08:00',0,'17:00',60,8.0,9.0,'done','fact')"""
        )
        self.con.commit()
        schedule.apply_simple_month_plan(
            CoreStub,
            self.con,
            [1],
            2026,
            11,
            pattern=schedule.PATTERN_WEEKDAYS,
            replace=True,
        )
        self.con.commit()
        row = self.con.execute(
            "SELECT * FROM employee_shifts WHERE employee_id=1 AND work_date='2026-11-02'"
        ).fetchone()
        self.assertEqual(row["actual_hours"], 9.0)
        self.assertEqual(row["notes"], "fact")

    def test_employee_view_contains_only_selected_people_and_no_internal_notes(self):
        # Create an internal duplicate-role warning involving other employees.
        self.con.execute(
            """INSERT INTO employee_shifts(
                   employee_id,role,work_date,shift_no,start_time,end_day_offset,end_time,
                   planned_hours,status,notes
               ) VALUES(1,'Контролер','2026-11-05',1,'08:00',0,'16:00',8,'planned','')"""
        )
        self.con.execute(
            """INSERT INTO employee_shifts(
                   employee_id,role,work_date,shift_no,start_time,end_day_offset,end_time,
                   planned_hours,status,notes
               ) VALUES(2,'Контролер','2026-11-05',1,'08:00',0,'16:00',8,'planned','')"""
        )
        self.con.commit()
        data = schedule.collect_month_schedule(
            CoreStub,
            self.con,
            2026,
            11,
            employee_ids=[3],
            view=schedule.VIEW_EMPLOYEE,
        )
        self.assertEqual([row["employee_id"] for row in data["employees"]], [3])
        self.assertEqual(data["internal_notes"], [])

    def test_employee_xlsx_does_not_leak_unselected_staff(self):
        data = schedule.collect_month_schedule(
            CoreStub,
            self.con,
            2026,
            11,
            employee_ids=[1],
            view=schedule.VIEW_EMPLOYEE,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "schedule.xlsx"
            schedule.export_employee_schedule_xlsx(data, path)
            wb = load_workbook(path, read_only=True, data_only=True)
            try:
                values = " ".join(
                    str(cell or "")
                    for row in wb.active.iter_rows(values_only=True)
                    for cell in row
                )
            finally:
                wb.close()
        self.assertIn("Контролер Олена", values)
        self.assertNotIn("Механік Ігор", values)
        self.assertNotIn("немає контролера", values.casefold())


if __name__ == "__main__":
    unittest.main()
