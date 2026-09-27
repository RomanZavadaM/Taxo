# -*- coding: utf-8 -*-
import inspect
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import main
import personnel_v91
import v1043_features
from release_naming import start_archive_stem, version_from_file

ROOT=Path(__file__).resolve().parents[1]


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

    def test_candidate_identity(self):
        # r3 is an immutable historical checkpoint, while the current runtime may
        # legitimately advance to r4/r5/etc.  Guard the r3 marker itself instead
        # of forcing every later revision to keep main.APP_VERSION at r3.
        self.assertEqual(v1043_features.APP_VERSION,"10.4-r3")
        self.assertEqual(main.APP_VERSION,version_from_file(ROOT/"VERSION.txt"))
        self.assertEqual(start_archive_stem("10.4-r3"),"Taxo_v10_4_candidate_r3_START")

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

    def test_old_p5_edrpou_setting_migrates_to_company_requisites(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path=Path(tmp)/"test.sqlite3"
            con=sqlite3.connect(db_path)
            con.executescript("""
                CREATE TABLE company(id INTEGER PRIMARY KEY, name TEXT DEFAULT '');
                INSERT INTO company(id,name) VALUES(1,'АТП');
                CREATE TABLE app_settings(key TEXT PRIMARY KEY,value TEXT DEFAULT '');
                INSERT INTO app_settings(key,value) VALUES('company_edrpou','12345678');
            """)
            con.commit(); con.close()

            def open_db():
                db=sqlite3.connect(db_path)
                db.row_factory=sqlite3.Row
                return db

            fake=SimpleNamespace(db=open_db)
            v1043_features._ensure_company_edrpou_schema(fake)

            con=open_db()
            columns={row[1] for row in con.execute("PRAGMA table_info(company)").fetchall()}
            value=con.execute("SELECT edrpou FROM company WHERE id=1").fetchone()["edrpou"]
            con.close()
            self.assertIn("edrpou",columns)
            self.assertEqual(value,"12345678")

    def test_duration_only_plan_and_edrpou_rendering_are_wired(self):
        source=inspect.getsource(v1043_features)
        p5_source=inspect.getsource(personnel_v91)
        self.assertIn("План {core.minutes_hhmm(state['work_minutes'])} · час зміни не задано",source)
        self.assertIn('return f"{core.minutes_hhmm(minutes)}\\nбез часу"',source)
        self.assertIn('text="ЄДРПОУ"',source)
        self.assertIn('line = f"ЄДРПОУ: {edrpou}"',source)
        self.assertIn('"Ідентифікаційний код ЄДРПОУ: {edrpou or \'\'}"',p5_source)
        self.assertIn('core.get_setting("company_edrpou","")',p5_source)


if __name__=="__main__":
    unittest.main()
