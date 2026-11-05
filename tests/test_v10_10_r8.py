# -*- coding: utf-8 -*-
"""Taxo 10.10-r8 — simple monthly schedule and privacy of filtered views."""
import sqlite3
import unittest

import personnel_month_schedule_r8 as schedule


def make_db():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY,
            personnel_no TEXT DEFAULT '',
            last_name TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            middle_name TEXT DEFAULT '',
            position TEXT DEFAULT '',
            driver_id INTEGER,
            active INTEGER DEFAULT 1
        );
        CREATE TABLE employee_roles(
            employee_id INTEGER,
            role TEXT
        );
        CREATE TABLE employee_shifts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            role TEXT,
            work_date TEXT,
            shift_no INTEGER,
            start_time TEXT,
            end_day_offset INTEGER DEFAULT 0,
            end_time TEXT,
            location TEXT DEFAULT '',
            unpaid_break_minutes INTEGER DEFAULT 0,
            planned_hours REAL,
            actual_hours REAL,
            status TEXT,
            notes TEXT
        );
        CREATE TABLE employee_time_entries(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            work_date TEXT,
            day_type TEXT,
            notes TEXT
        );
        CREATE TABLE worklog(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER,
            work_date TEXT,
            start_time TEXT,
            end_time TEXT,
            route_name TEXT,
            work_hours REAL
        );
        """
    )
    con.execute(
        "INSERT INTO employees VALUES(1,'001','Іваненко','Іван','','Водій',10,1)"
    )
    con.execute(
        "INSERT INTO employees VALUES(2,'002','Петренко','Петро','','Контролер',NULL,1)"
    )
    con.execute("INSERT INTO employee_roles VALUES(1,'Водій')")
    con.execute("INSERT INTO employee_roles VALUES(2,'Контролер')")
    con.execute(
        """INSERT INTO worklog(driver_id,work_date,start_time,end_time,route_name,work_hours)
           VALUES(10,'2026-11-05','06:00','15:00','Маршрут 10',8.0)"""
    )
    con.execute(
        """INSERT INTO employee_shifts(
            employee_id,role,work_date,shift_no,start_time,end_time,planned_hours,actual_hours,status,notes
        ) VALUES(2,'Контролер','2026-11-05',1,'08:00','17:00',8.0,NULL,'planned','')"""
    )
    con.commit()
    return con


class MonthScheduleViewsR8Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()

    def tearDown(self):
        self.con.close()

    def test_internal_view_contains_both_employees(self):
        rows = schedule.month_schedule_rows(
            self.con, 2026, 11, mode=schedule.VIEW_INTERNAL
        )
        self.assertEqual({row["employee_id"] for row in rows}, {1, 2})
        driver = next(row for row in rows if row["employee_id"] == 1)
        self.assertEqual(driver["cells"][5]["code"], "Р")
        self.assertIn("Маршрут 10", driver["cells"][5]["detail"])

    def test_personal_driver_view_does_not_leak_other_staff(self):
        rows = schedule.month_schedule_rows(
            self.con, 2026, 11,
            mode=schedule.VIEW_PERSONAL,
            personal_id=1,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["employee_name"], "Іваненко Іван")
        rendered = repr(rows)
        self.assertNotIn("Петренко", rendered)
        self.assertNotIn("Контролер", rendered)

    def test_selected_view_contains_only_selected_people(self):
        rows = schedule.month_schedule_rows(
            self.con, 2026, 11,
            mode=schedule.VIEW_SELECTED,
            selected_ids=[2],
        )
        self.assertEqual([row["employee_id"] for row in rows], [2])
        self.assertEqual(rows[0]["cells"][5]["code"], "Р")

    def test_role_view_contains_only_that_role(self):
        rows = schedule.month_schedule_rows(
            self.con, 2026, 11,
            mode=schedule.VIEW_ROLE,
            role="Контролер",
        )
        self.assertEqual([row["employee_id"] for row in rows], [2])


class SimplePlannerR8Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()

    def tearDown(self):
        self.con.close()

    def test_simple_planner_never_duplicates_driver_plan(self):
        result = schedule.apply_simple_plan(
            self.con, [1, 2], 2026, 11,
            pattern=schedule.PATTERN_5_2,
            start_time="08:00", end_time="17:00",
            unpaid_break_minutes=60,
        )
        self.con.commit()
        self.assertEqual(result["skipped_drivers"], 1)
        driver_generic = self.con.execute(
            "SELECT COUNT(*) FROM employee_shifts WHERE employee_id=1"
        ).fetchone()[0]
        self.assertEqual(driver_generic, 0)
        controller_count = self.con.execute(
            "SELECT COUNT(*) FROM employee_shifts WHERE employee_id=2"
        ).fetchone()[0]
        self.assertGreater(controller_count, 1)

    def test_absence_and_actual_fact_are_not_overwritten(self):
        self.con.execute(
            "INSERT INTO employee_time_entries(employee_id,work_date,day_type,notes) VALUES(2,'2026-11-02','Лікарняний','')"
        )
        self.con.execute(
            """INSERT INTO employee_shifts(
                employee_id,role,work_date,shift_no,start_time,end_time,planned_hours,actual_hours,status,notes
            ) VALUES(2,'Контролер','2026-11-03',1,'09:00','18:00',8.0,8.0,'actual','fact')"""
        )
        self.con.commit()

        schedule.apply_simple_plan(
            self.con, [2], 2026, 11,
            pattern=schedule.PATTERN_5_2,
            replace=True,
        )
        self.con.commit()

        nov2 = self.con.execute(
            "SELECT COUNT(*) FROM employee_shifts WHERE employee_id=2 AND work_date='2026-11-02'"
        ).fetchone()[0]
        self.assertEqual(nov2, 0)
        actual = self.con.execute(
            "SELECT start_time,end_time,actual_hours FROM employee_shifts WHERE employee_id=2 AND work_date='2026-11-03'"
        ).fetchone()
        self.assertEqual((actual["start_time"], actual["end_time"], actual["actual_hours"]), ("09:00", "18:00", 8.0))


if __name__ == "__main__":
    unittest.main()
