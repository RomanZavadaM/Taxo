# -*- coding: utf-8 -*-
import inspect
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import main
import personnel_v91
import work_regime


def make_time_db():
    con=sqlite3.connect(":memory:")
    con.row_factory=sqlite3.Row
    con.executescript(
        """
        CREATE TABLE drivers(
            id INTEGER PRIMARY KEY,
            personnel_no TEXT DEFAULT '',
            last_name TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            middle_name TEXT DEFAULT '',
            employment_date TEXT DEFAULT '',
            driver_end_date TEXT DEFAULT '',
            driver_role_mode TEXT NOT NULL DEFAULT 'legacy',
            notes TEXT DEFAULT '',
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT ''
        );
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY,
            personnel_no TEXT DEFAULT '',
            last_name TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            middle_name TEXT DEFAULT '',
            position TEXT DEFAULT '',
            employment_date TEXT DEFAULT '',
            dismissal_date TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            active INTEGER DEFAULT 1,
            driver_id INTEGER
        );
        CREATE TABLE employee_roles(
            employee_id INTEGER,
            role TEXT,
            PRIMARY KEY(employee_id,role)
        );
        CREATE TABLE driver_role_periods(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            driver_id INTEGER NOT NULL,
            start_date TEXT DEFAULT '',
            end_date TEXT DEFAULT '',
            source TEXT NOT NULL DEFAULT 'manual',
            voided INTEGER NOT NULL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE worklog(
            id INTEGER PRIMARY KEY,
            driver_id INTEGER NOT NULL,
            work_date TEXT NOT NULL,
            day_type TEXT DEFAULT 'Робота',
            start_time TEXT DEFAULT '',
            end_time TEXT DEFAULT '',
            work_start_time TEXT DEFAULT '',
            work_end_time TEXT DEFAULT '',
            work_hours REAL DEFAULT 0,
            driving_hours REAL DEFAULT 0,
            overtime_hours REAL DEFAULT 0,
            route_id INTEGER,
            route_name TEXT DEFAULT ''
        );
        CREATE TABLE work_segments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worklog_id INTEGER NOT NULL,
            segment_no INTEGER NOT NULL,
            start_time TEXT DEFAULT '',
            end_time TEXT DEFAULT '',
            work_start_time TEXT DEFAULT '',
            work_end_time TEXT DEFAULT '',
            work_hours REAL DEFAULT 0,
            driving_hours REAL DEFAULT 0,
            activity_type TEXT DEFAULT 'Робота',
            note TEXT DEFAULT ''
        );
        CREATE TABLE employee_shifts(
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
            notes TEXT DEFAULT ''
        );
        CREATE TABLE employee_time_entries(
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
            created_at TEXT DEFAULT '',
            updated_at TEXT DEFAULT '',
            UNIQUE(employee_id,work_date)
        );
        CREATE TABLE employee_work_regimes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            effective_from TEXT NOT NULL,
            effective_to TEXT DEFAULT '',
            regime_type TEXT NOT NULL DEFAULT 'five_day',
            accounting_period TEXT NOT NULL DEFAULT 'week',
            weekly_norm_minutes INTEGER NOT NULL DEFAULT 2400,
            mon_minutes INTEGER NOT NULL DEFAULT 480,
            tue_minutes INTEGER NOT NULL DEFAULT 480,
            wed_minutes INTEGER NOT NULL DEFAULT 480,
            thu_minutes INTEGER NOT NULL DEFAULT 480,
            fri_minutes INTEGER NOT NULL DEFAULT 480,
            sat_minutes INTEGER NOT NULL DEFAULT 0,
            sun_minutes INTEGER NOT NULL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT '',
            updated_at TEXT DEFAULT ''
        );
        CREATE TABLE route_segments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_id INTEGER NOT NULL,
            segment_no INTEGER NOT NULL,
            start_time TEXT DEFAULT '',
            end_time TEXT DEFAULT '',
            work_start_time TEXT DEFAULT '',
            work_end_time TEXT DEFAULT '',
            work_hours REAL DEFAULT 0,
            driving_hours REAL DEFAULT 0
        );
        """
    )
    return con


def add_driver_employee(con, *, mode="legacy", active=1, end_date="", employment="2020-01-01"):
    con.execute(
        """INSERT INTO drivers(
             id,personnel_no,last_name,first_name,employment_date,driver_end_date,
             driver_role_mode,active,created_at
           ) VALUES(1,'001','Тест','Працівник',?,?,?,?,?)""",
        (employment,end_date,mode,int(active),"2020-01-01T00:00:00"),
    )
    con.execute(
        """INSERT INTO employees(
             id,personnel_no,last_name,first_name,position,employment_date,
             active,driver_id
           ) VALUES(10,'001','Тест','Працівник','Працівник',?,1,1)""",
        (employment,),
    )
    if active:
        con.execute("INSERT INTO employee_roles(employee_id,role) VALUES(10,'Водій')")
    con.commit()


class TestTaxo102R3TimesheetAndDriverRole(unittest.TestCase):
    def test_version_is_r3(self):
        self.assertEqual(main.APP_VERSION,"10.2-r3")

    def test_version_file_matches_app_version(self):
        root=Path(__file__).resolve().parents[1]
        version_text=(root/"VERSION.txt").read_text(encoding="utf-8")
        self.assertIn("Version: 10.2-r3",version_text)
        from release_naming import start_archive_stem, version_from_file
        self.assertEqual(version_from_file(root/"VERSION.txt"),main.APP_VERSION)
        self.assertEqual(
            start_archive_stem(main.APP_VERSION),
            "Taxo_v10_2_candidate_r3_START",
        )

    def test_shift_uses_paid_plan_not_raw_clock_span(self):
        con=make_time_db()
        con.execute(
            """INSERT INTO employee_shifts(
                 employee_id,role,work_date,shift_no,start_time,end_day_offset,end_time,
                 unpaid_break_minutes,planned_hours,notes
               ) VALUES(10,'Інше','2026-09-01',1,'08:00',0,'17:00',60,8.0,'Місячний план персоналу')"""
        )
        con.commit()
        planned,actual,found=main._employee_shift_minutes_for_day(
            con,10,date(2026,9,1)
        )
        self.assertTrue(found)
        self.assertEqual(planned,480)
        self.assertIsNone(actual)
        con.close()

    def test_legacy_bulk_08_17_is_normalized_to_5_40_paid_day(self):
        con=make_time_db()
        con.execute(
            """INSERT INTO employee_work_regimes(
                 employee_id,effective_from,regime_type,accounting_period,
                 weekly_norm_minutes,mon_minutes,tue_minutes,wed_minutes,thu_minutes,
                 fri_minutes,sat_minutes,sun_minutes
               ) VALUES(10,'2026-01-01','five_day','week',2400,480,480,480,480,480,0,0)"""
        )
        con.execute(
            """INSERT INTO employee_shifts(
                 employee_id,role,work_date,shift_no,start_time,end_day_offset,end_time,
                 unpaid_break_minutes,planned_hours,notes
               ) VALUES(10,'Інше','2026-09-01',1,'08:00',0,'17:00',0,9.0,'Місячний план персоналу')"""
        )
        con.commit()
        planned,_actual,_found=main._employee_shift_minutes_for_day(
            con,10,date(2026,9,1)
        )
        self.assertEqual(planned,480)
        con.close()

    def test_driver_plan_stops_after_real_role_end(self):
        con=make_time_db()
        add_driver_employee(con,mode="legacy",active=0,end_date="2026-09-10")
        for day in ("2026-09-10","2026-09-15"):
            con.execute(
                """INSERT INTO worklog(
                     id,driver_id,work_date,work_start_time,work_end_time,work_hours
                   ) VALUES(?,?,?,?,?,8.0)""",
                (1 if day.endswith("10") else 2,1,day,"09:00","17:00"),
            )
        con.commit()
        self.assertEqual(
            main._driver_plan_minutes_for_day(con,1,date(2026,9,10)),480
        )
        self.assertEqual(
            main._driver_plan_minutes_for_day(con,1,date(2026,9,15)),0
        )
        con.close()

    def test_invalid_legacy_driver_never_feeds_timesheet(self):
        con=make_time_db()
        add_driver_employee(con,mode="invalid",active=0,end_date="")
        con.execute(
            """INSERT INTO worklog(
                 id,driver_id,work_date,work_start_time,work_end_time,work_hours
               ) VALUES(1,1,'2026-09-01','09:00','17:00',8.0)"""
        )
        con.commit()
        self.assertFalse(main.driver_role_active_on(con,1,date(2026,9,1)))
        self.assertEqual(
            main._driver_plan_minutes_for_day(con,1,date(2026,9,1)),0
        )
        con.close()

    def test_explicit_role_period_is_historical_source_of_truth(self):
        con=make_time_db()
        add_driver_employee(con,mode="explicit",active=0,end_date="2026-09-10")
        con.execute(
            """INSERT INTO driver_role_periods(
                 employee_id,driver_id,start_date,end_date,source,created_at
               ) VALUES(10,1,'2026-09-01','2026-09-10','manual','2026-09-10T00:00:00')"""
        )
        con.commit()
        self.assertFalse(main.driver_role_active_on(con,1,date(2026,8,31)))
        self.assertTrue(main.driver_role_active_on(con,1,date(2026,9,5)))
        self.assertTrue(main.driver_role_active_on(con,1,date(2026,9,10)))
        self.assertFalse(main.driver_role_active_on(con,1,date(2026,9,11)))
        con.close()

    def test_void_legacy_role_keeps_old_worklog_for_audit(self):
        con=make_time_db()
        add_driver_employee(con,mode="legacy",active=1)
        con.execute(
            """INSERT INTO worklog(
                 id,driver_id,work_date,work_start_time,work_end_time,work_hours
               ) VALUES(1,1,'2026-09-01','09:00','17:00',8.0)"""
        )
        con.commit()
        main.void_legacy_driver_role(con,10,1)
        con.commit()
        driver=con.execute("SELECT * FROM drivers WHERE id=1").fetchone()
        self.assertEqual(driver["driver_role_mode"],"invalid")
        self.assertEqual(driver["active"],0)
        self.assertEqual(con.execute("SELECT COUNT(*) FROM worklog").fetchone()[0],1)
        self.assertIsNone(
            con.execute(
                "SELECT 1 FROM employee_roles WHERE employee_id=10 AND role='Водій'"
            ).fetchone()
        )
        con.close()

    def test_finish_role_keeps_employee_and_creates_closed_period(self):
        con=make_time_db()
        add_driver_employee(con,mode="legacy",active=1)
        main.finish_driver_role(con,10,1,"2026-09-20")
        con.commit()
        employee=con.execute("SELECT * FROM employees WHERE id=10").fetchone()
        period=con.execute(
            "SELECT * FROM driver_role_periods WHERE driver_id=1"
        ).fetchone()
        self.assertEqual(employee["active"],1)
        self.assertEqual(period["end_date"],"2026-09-20")
        self.assertEqual(
            con.execute("SELECT driver_role_mode FROM drivers WHERE id=1").fetchone()[0],
            "explicit",
        )
        con.close()

    def test_linked_route_fallback_ignores_invalid_driver_role(self):
        con=make_time_db()
        add_driver_employee(con,mode="invalid",active=0)
        con.execute(
            """INSERT INTO worklog(
                 id,driver_id,work_date,work_hours,route_id
               ) VALUES(1,1,'2026-09-01',8.0,7)"""
        )
        con.execute(
            """INSERT INTO route_segments(
                 route_id,segment_no,work_start_time,work_end_time,work_hours
               ) VALUES(7,1,'09:00','17:00',8.0)"""
        )
        con.commit()
        self.assertEqual(
            personnel_v91.linked_route_plan_minutes(
                main,con,1,date(2026,9,1)
            ),
            0,
        )
        con.close()

    def test_general_planner_records_unpaid_breaks(self):
        source=inspect.getsource(personnel_v91.install)
        self.assertIn("unpaid_break_minutes",source)
        self.assertIn("Перерва, хв",source)
        self.assertIn("0<gap<=120",source)
        self.assertIn("paid_minutes/60.0",source)

    def test_general_planner_exposes_safe_replanning_control(self):
        source=inspect.getsource(personnel_v91.install)
        self.assertIn("Перепланувати: замінити існуючий ПЛАН",source)
        self.assertIn("actual_hours IS NULL",source)
        self.assertIn("command=lambda: preview()",source)
        self.assertIn("body.rowconfigure(12, weight=1)",source)
        self.assertIn("buttons.grid(row=11",source)
        self.assertIn("tree.grid(row=12",source)

    def test_audit_flags_13_hour_day_against_5_40_norm(self):
        with tempfile.TemporaryDirectory() as folder:
            db_path=Path(folder)/"audit.sqlite3"
            con=sqlite3.connect(db_path)
            con.executescript(
                """
                CREATE TABLE employees(
                    id INTEGER PRIMARY KEY,personnel_no TEXT,last_name TEXT,first_name TEXT,
                    middle_name TEXT,position TEXT,employment_date TEXT,dismissal_date TEXT,
                    active INTEGER,driver_id INTEGER
                );
                CREATE TABLE employee_roles(employee_id INTEGER,role TEXT);
                CREATE TABLE employee_time_entries(
                    id INTEGER PRIMARY KEY,employee_id INTEGER,work_date TEXT,day_type TEXT,
                    planned_hours REAL,actual_hours REAL,notes TEXT
                );
                CREATE TABLE employee_shifts(
                    id INTEGER PRIMARY KEY,employee_id INTEGER,role TEXT,work_date TEXT,
                    shift_no INTEGER,start_time TEXT,end_day_offset INTEGER,end_time TEXT,
                    planned_hours REAL,actual_hours REAL,notes TEXT
                );
                CREATE TABLE employee_work_regimes(
                    id INTEGER PRIMARY KEY,employee_id INTEGER,effective_from TEXT,effective_to TEXT,
                    regime_type TEXT,accounting_period TEXT,weekly_norm_minutes INTEGER,
                    mon_minutes INTEGER,tue_minutes INTEGER,wed_minutes INTEGER,thu_minutes INTEGER,
                    fri_minutes INTEGER,sat_minutes INTEGER,sun_minutes INTEGER,notes TEXT
                );
                """
            )
            con.execute(
                "INSERT INTO employees VALUES(1,'001','Тест','13 год','','Економіст','2020-01-01','',1,NULL)"
            )
            con.execute(
                """INSERT INTO employee_work_regimes VALUES(
                   1,1,'2026-01-01','','five_day','week',2400,
                   480,480,480,480,480,0,0,'')"""
            )
            con.execute(
                "INSERT INTO employee_time_entries VALUES(1,1,'2026-09-01','Робота',13.0,NULL,'ручний тест')"
            )
            con.commit(); con.close()

            def db():
                conn=sqlite3.connect(db_path)
                conn.row_factory=sqlite3.Row
                return conn

            def employee_day_time(con,employee_id,target_date):
                row=con.execute(
                    "SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                    (employee_id,target_date.isoformat()),
                ).fetchone()
                return {
                    "day_type":row["day_type"] if row else "Вихідний",
                    "planned_minutes":main.hours_value_to_minutes(row["planned_hours"]) if row else 0,
                    "actual_minutes":None,
                    "source":"test","notes":row["notes"] if row else "",
                }

            fake=SimpleNamespace(
                db=db,
                month_dates=main.month_dates,
                employee_employed_on=lambda _e,_d: True,
                employee_day_time=employee_day_time,
                employee_name=lambda e:f"{e['last_name']} {e['first_name']}",
                hours_value_to_minutes=main.hours_value_to_minutes,
            )
            audit=personnel_v91.collect_personnel_timesheet_audit(
                fake,2026,9,active_only=True
            )
            codes={x["code"] for x in audit["issues"]}
            self.assertIn("plan_vs_norm",codes)
            self.assertIn("long_plan",codes)

    def test_p5_runs_audit_before_plan_substitution(self):
        source=inspect.getsource(personnel_v91.install)
        pos_audit=source.index("collect_personnel_timesheet_audit")
        pos_preview=source.index("preview=collect_p5_data",pos_audit)
        self.assertLess(pos_audit,pos_preview)


if __name__=="__main__":
    unittest.main()
