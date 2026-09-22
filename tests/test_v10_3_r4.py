# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path
import sqlite3
import unittest

import main
from release_naming import start_archive_stem, version_from_file

ROOT=Path(__file__).resolve().parents[1]


def make_db():
    con=sqlite3.connect(":memory:")
    con.row_factory=sqlite3.Row
    con.executescript("""
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
            fact_work_start_time TEXT DEFAULT '',
            fact_work_end_time TEXT DEFAULT '',
            fact_work_hours REAL,
            fact_source TEXT DEFAULT '',
            fact_updated_at TEXT DEFAULT ''
        );
        CREATE TABLE work_segments(
            id INTEGER PRIMARY KEY,
            worklog_id INTEGER NOT NULL,
            segment_no INTEGER NOT NULL,
            start_time TEXT DEFAULT '',
            end_time TEXT DEFAULT '',
            work_start_time TEXT DEFAULT '',
            work_end_time TEXT DEFAULT '',
            work_hours REAL DEFAULT 0,
            activity_type TEXT DEFAULT 'Робота',
            note TEXT DEFAULT ''
        );
    """)
    return con


class TestTaxo103R4FactualBoundary(unittest.TestCase):
    def test_version_is_r4(self):
        self.assertEqual(main.APP_VERSION,"10.3-r4")
        self.assertEqual(version_from_file(ROOT/"VERSION.txt"),"10.3-r4")
        self.assertEqual(
            start_archive_stem("10.3-r4"),
            "Taxo_v10_3_candidate_r4_START",
        )

    def test_tail_is_never_auto_absorbed(self):
        missing=[(
            datetime(2026,9,21,20,25),
            datetime(2026,9,21,20,40),
        )]
        overlapping=[(
            100,
            datetime(2026,9,18,19,40),
            datetime(2026,9,21,20,25),
            74,
            16,
        )]
        self.assertIsNone(main._attestation_tail_adjustment(missing,overlapping))

    def test_factual_boundary_can_shorten_or_extend_work_without_touching_plan(self):
        con=make_db()
        con.execute(
            """INSERT INTO worklog(
                id,driver_id,work_date,start_time,end_time,
                work_start_time,work_end_time,work_hours
            ) VALUES(1,7,'2026-09-21','07:45','20:25','07:35','20:40',13.083333)"""
        )
        item={"row":con.execute("SELECT * FROM worklog WHERE id=1").fetchone(),"segments":[]}
        main.App._set_worklog_boundary(
            con,item,"end",datetime(2026,9,21,20,55)
        )
        row=con.execute("SELECT * FROM worklog WHERE id=1").fetchone()
        self.assertEqual(row["work_end_time"],"20:40")
        self.assertEqual(row["end_time"],"20:25")
        self.assertEqual(row["fact_work_end_time"],"20:55")
        con.close()

    def test_missing_adjacent_worklog_does_not_invent_one(self):
        con=make_db()
        app=object.__new__(main.App)
        changes=main.App._sync_attestation_boundaries_to_worklog(
            app,con,7,
            "20:25 21.09.2026","07:45 24.09.2026",
            "20:40 21.09.2026","07:35 24.09.2026",
        )
        self.assertEqual(changes,[])
        count=con.execute("SELECT COUNT(*) FROM worklog").fetchone()[0]
        self.assertEqual(count,0)
        con.close()

    def test_source_text_states_manual_fact_not_auto_tail(self):
        src=(ROOT/"main.py").read_text("utf-8")
        self.assertIn("не є окремим бланком",src)
        self.assertIn("не додається до нього автоматично",src)
        self.assertIn("уточніть межу цього ж бланка вручну",src)
        self.assertIn("Фактичне закінчення попередньої роботи",src)
        self.assertIn("Фактичний початок наступної роботи",src)
        self.assertIn("Змінюйте тільки ту межу, яка вже відома по факту",src)


if __name__=="__main__":
    unittest.main()
