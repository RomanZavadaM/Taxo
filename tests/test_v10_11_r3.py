# -*- coding: utf-8 -*-
"""Regression: Taxo 10.11-r3 data-integrity fixes."""
from __future__ import annotations

import sqlite3
import unittest
from datetime import date
from unittest.mock import patch

import main
import personnel_v91


def fact_database():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript("""
        CREATE TABLE employee_time_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            work_date TEXT NOT NULL,
            day_type TEXT NOT NULL DEFAULT 'Робота',
            planned_hours REAL,
            actual_hours REAL,
            overtime_hours REAL,
            night_hours REAL,
            evening_hours REAL,
            weekend_holiday_hours REAL,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT DEFAULT '',
            UNIQUE(employee_id, work_date)
        );
    """)
    return con


def shift_database():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript("""
        CREATE TABLE employee_shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            work_date TEXT NOT NULL,
            shift_no INTEGER NOT NULL DEFAULT 1 CHECK(shift_no IN (1,2)),
            start_time TEXT NOT NULL,
            end_day_offset INTEGER NOT NULL DEFAULT 0 CHECK(end_day_offset BETWEEN 0 AND 7),
            end_time TEXT NOT NULL,
            location TEXT DEFAULT '',
            unpaid_break_minutes INTEGER NOT NULL DEFAULT 0,
            planned_hours REAL NOT NULL DEFAULT 0,
            actual_hours REAL,
            status TEXT NOT NULL DEFAULT 'planned',
            notes TEXT DEFAULT '',
            UNIQUE(employee_id, role, work_date, shift_no)
        );
    """)
    return con


class PlanToFactR3Tests(unittest.TestCase):
    def test_existing_fact_is_never_overwritten(self):
        con = fact_database()
        con.execute(
            """INSERT INTO employee_time_entries(
                   employee_id,work_date,day_type,actual_hours,notes,created_at,updated_at
               ) VALUES(1,'2026-11-03','Робота',7.25,'Підтверджений факт','t','t')"""
        )
        employee = {"id": 1}
        with patch.object(main, "employee_employed_on", return_value=True), \
             patch.object(main, "employee_day_time", return_value={
                 "day_type": "Робота",
                 "planned_minutes": 480,
                 "actual_minutes": 435,
                 "notes": "Підтверджений факт",
             }):
            stats = main.copy_missing_plan_to_fact(
                con, employee, [date(2026, 11, 3)], now="2026-11-06T12:00:00"
            )
        row = con.execute(
            "SELECT actual_hours,notes FROM employee_time_entries WHERE employee_id=1 AND work_date='2026-11-03'"
        ).fetchone()
        self.assertEqual(row["actual_hours"], 7.25)
        self.assertEqual(row["notes"], "Підтверджений факт")
        self.assertEqual(stats["written"], 0)
        self.assertEqual(stats["protected_fact"], 1)
        con.close()

    def test_missing_fact_receives_plan_without_rewriting_other_manual_fields(self):
        con = fact_database()
        con.execute(
            """INSERT INTO employee_time_entries(
                   employee_id,work_date,day_type,planned_hours,actual_hours,notes,created_at,updated_at
               ) VALUES(1,'2026-11-04','Інший тип',6.0,NULL,'Зберегти примітку','t','t')"""
        )
        employee = {"id": 1}
        with patch.object(main, "employee_employed_on", return_value=True), \
             patch.object(main, "employee_day_time", return_value={
                 "day_type": "Робота",
                 "planned_minutes": 480,
                 "actual_minutes": None,
                 "notes": "Автоматичний план",
             }):
            stats = main.copy_missing_plan_to_fact(
                con, employee, [date(2026, 11, 4)], now="2026-11-06T12:00:00"
            )
        row = con.execute(
            """SELECT day_type,planned_hours,actual_hours,notes
                 FROM employee_time_entries
                WHERE employee_id=1 AND work_date='2026-11-04'"""
        ).fetchone()
        self.assertEqual(row["day_type"], "Інший тип")
        self.assertEqual(row["planned_hours"], 6.0)
        self.assertEqual(row["actual_hours"], 8.0)
        self.assertEqual(row["notes"], "Зберегти примітку")
        self.assertEqual(stats["written"], 1)
        self.assertEqual(stats["protected_fact"], 0)
        con.close()


class PersonnelPlannerAtomicReplaceR3Tests(unittest.TestCase):
    def _seed_old_shift(self, con):
        con.execute(
            """INSERT INTO employee_shifts(
                   employee_id,role,work_date,shift_no,start_time,end_day_offset,end_time,
                   location,unpaid_break_minutes,planned_hours,actual_hours,status,notes
               ) VALUES(1,'Механік','2026-11-05',1,'08:00',0,'17:00',
                        'База',60,8.0,NULL,'planned','Старий план')"""
        )
        return con.execute("SELECT * FROM employee_shifts").fetchall()

    def test_failed_replacement_keeps_old_shift(self):
        con = shift_database()
        old = self._seed_old_shift(con)
        with self.assertRaises(sqlite3.IntegrityError):
            personnel_v91.replace_planned_employee_shift(
                con,
                old,
                True,
                (
                    1, "Механік", "2026-11-05",
                    3,  # invalid by CHECK(shift_no IN (1,2))
                    "09:00", 0, "18:00", "База", 60, 8.0, "Новий план",
                ),
            )
        rows = con.execute("SELECT * FROM employee_shifts").fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["start_time"], "08:00")
        self.assertEqual(rows[0]["end_time"], "17:00")
        self.assertEqual(rows[0]["notes"], "Старий план")
        con.close()

    def test_successful_replacement_is_single_new_shift(self):
        con = shift_database()
        old = self._seed_old_shift(con)
        result = personnel_v91.replace_planned_employee_shift(
            con,
            old,
            True,
            (
                1, "Механік", "2026-11-05",
                1, "09:00", 0, "18:00", "База", 60, 8.0, "Новий план",
            ),
        )
        rows = con.execute("SELECT * FROM employee_shifts").fetchall()
        self.assertEqual(result, "written")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["start_time"], "09:00")
        self.assertEqual(rows[0]["end_time"], "18:00")
        self.assertEqual(rows[0]["notes"], "Новий план")
        con.close()


if __name__ == "__main__":
    unittest.main()
