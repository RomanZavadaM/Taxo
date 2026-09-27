# -*- coding: utf-8 -*-
import sqlite3
import unittest
from types import SimpleNamespace

import main
import v1043_features


class TestTaxo104R3DriverScheduleSafety(unittest.TestCase):
    def _db(self):
        con=sqlite3.connect(":memory:")
        con.row_factory=sqlite3.Row
        con.executescript("""
            CREATE TABLE drivers(
                id INTEGER PRIMARY KEY,
                employment_date TEXT DEFAULT '',
                driver_end_date TEXT DEFAULT '',
                driver_role_mode TEXT NOT NULL DEFAULT 'legacy',
                active INTEGER DEFAULT 1
            );
            CREATE TABLE worklog(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                work_date TEXT NOT NULL,
                day_type TEXT NOT NULL DEFAULT 'Робота',
                start_time TEXT DEFAULT '',
                end_time TEXT DEFAULT '',
                work_start_time TEXT DEFAULT '',
                work_end_time TEXT DEFAULT '',
                work_hours REAL DEFAULT 0,
                driving_hours REAL DEFAULT 0,
                route_name TEXT DEFAULT '',
                route_id INTEGER,
                template_id INTEGER,
                shift_type TEXT DEFAULT 'Безперервна',
                accounting_mode TEXT DEFAULT 'manual',
                UNIQUE(driver_id,work_date)
            );
            CREATE TABLE work_segments(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worklog_id INTEGER NOT NULL,
                segment_no INTEGER NOT NULL,
                start_time TEXT DEFAULT '',
                end_time TEXT DEFAULT '',
                work_start_time TEXT DEFAULT '',
                work_end_time TEXT DEFAULT ''
            );
            CREATE TABLE employees(
                id INTEGER PRIMARY KEY,
                driver_id INTEGER,
                active INTEGER DEFAULT 1
            );
            CREATE TABLE employee_time_entries(
                id INTEGER PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                work_date TEXT NOT NULL,
                day_type TEXT NOT NULL DEFAULT 'Робота'
            );
            INSERT INTO drivers(id,employment_date,driver_end_date,driver_role_mode,active)
            VALUES(1,'2026-09-21','','legacy',1);
            INSERT INTO worklog(
                driver_id,work_date,day_type,start_time,end_time,work_start_time,work_end_time,
                work_hours,driving_hours,route_name,route_id,template_id,shift_type,accounting_mode
            ) VALUES(1,'2026-09-21','Робота','06:40','08:45','06:30','08:55',
                     2.416667,2.083333,'Маршрут 1',77,88,'Розділена на частини','tacho');
            INSERT INTO work_segments(
                worklog_id,segment_no,start_time,end_time,work_start_time,work_end_time
            ) VALUES(1,1,'06:40','08:45','06:30','08:55');
        """)
        return con

    def test_bulk_8h_fill_never_rewrites_existing_schedule(self):
        con=self._db()
        driver=con.execute("SELECT * FROM drivers WHERE id=1").fetchone()
        result=v1043_features.fill_empty_no_tacho_days(main,con,1,driver,2026,9)
        con.commit()

        preserved=con.execute("SELECT * FROM worklog WHERE driver_id=1 AND work_date='2026-09-21'").fetchone()
        self.assertEqual(preserved["start_time"],"06:40")
        self.assertEqual(preserved["end_time"],"08:45")
        self.assertEqual(preserved["work_start_time"],"06:30")
        self.assertEqual(preserved["work_end_time"],"08:55")
        self.assertEqual(preserved["route_name"],"Маршрут 1")
        self.assertEqual(preserved["route_id"],77)
        self.assertEqual(preserved["template_id"],88)
        self.assertEqual(preserved["accounting_mode"],"tacho")
        self.assertEqual(
            con.execute("SELECT COUNT(*) FROM work_segments WHERE worklog_id=?",(preserved["id"],)).fetchone()[0],
            1,
        )

        eligible=[
            d for d in main.month_dates(2026,9)
            if d.weekday()<5 and main.driver_employed_on(driver,d)
        ]
        self.assertEqual(result["added"],len(eligible)-1)
        self.assertEqual(result["skipped_existing"],1)
        created=con.execute(
            "SELECT * FROM worklog WHERE driver_id=1 AND work_date='2026-09-22'"
        ).fetchone()
        self.assertEqual(created["work_hours"],8)
        self.assertEqual(created["driving_hours"],0)
        self.assertEqual(created["accounting_mode"],main.WORK_MODE_NO_TACHO)
        self.assertEqual(created["start_time"],"")
        con.close()

    def test_duration_only_plan_is_visible_without_inventing_clock_time(self):
        def original_day_view(*_args,**_kwargs):
            return {
                "explicit_worklog":True,
                "suppressed_plan":False,
                "day_type":"Робота",
                "bands":[],
                "work_minutes":480,
                "status_label":"Робота · час не задано",
            }

        fake=SimpleNamespace(
            APP_VERSION="10.4-r2",
            driver_day_view=original_day_view,
            _monthly_shift_cell=lambda row,segments:"Р",
            minutes_hhmm=lambda value:f"{int(value)//60}:{int(value)%60:02d}",
            hours_value_to_minutes=lambda value:int(round(float(value or 0)*60)),
            tk=SimpleNamespace(TclError=Exception),
            messagebox=SimpleNamespace(),
            COPYRIGHT_NOTICE="copyright",
            LICENSE_LABEL="license",
        )
        class Base:
            pass
        v1043_features.install(fake,Base)

        state=fake.driver_day_view(None,None,None)
        self.assertEqual(state["bands"],[])
        self.assertEqual(state["status_label"],"План 8:00 · час зміни не задано")
        cell=fake._monthly_shift_cell(
            {"day_type":"Робота","start_time":"","end_time":"","work_hours":8},[]
        )
        self.assertEqual(cell,"8:00\nбез часу")
        self.assertEqual(fake.APP_VERSION,"10.4-r3")


if __name__=="__main__":
    unittest.main()
