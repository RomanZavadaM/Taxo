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


class TestTaxo103R3AttestationTailFix(unittest.TestCase):
    def test_version_is_r3(self):
        self.assertEqual(main.APP_VERSION,"10.3-r3")
        self.assertEqual(version_from_file(ROOT/"VERSION.txt"),"10.3-r3")
        self.assertEqual(
            start_archive_stem("10.3-r3"),
            "Taxo_v10_3_candidate_r3_START",
        )

    def test_ten_minute_tail_extends_one_touching_form(self):
        ma=datetime(2026,9,24,7,35)
        mb=datetime(2026,9,24,7,45)
        old_start=datetime(2026,9,21,19,45)
        other_start=datetime(2026,9,22,12,0)
        other_end=datetime(2026,9,22,18,0)
        missing=[(ma,mb)]
        overlapping=[
            (1200,old_start,ma,74,16),
            (360,other_start,other_end,91,18),
        ]
        result=main._attestation_tail_adjustment(missing,overlapping)
        self.assertIsNotNone(result)
        target_from,target_to,ast,aen,att_id,activity=result
        self.assertEqual(att_id,74)
        self.assertEqual(activity,16)
        self.assertEqual((target_from,target_to),(old_start,mb))
        self.assertEqual((ast,aen),(old_start,ma))

    def test_gap_between_two_forms_is_not_auto_absorbed(self):
        ma=datetime(2026,9,24,7,35)
        mb=datetime(2026,9,24,7,45)
        missing=[(ma,mb)]
        overlapping=[
            (100,datetime(2026,9,23,20,0),ma,74,16),
            (100,mb,datetime(2026,9,24,10,0),75,16),
        ]
        self.assertIsNone(main._attestation_tail_adjustment(missing,overlapping))

    def test_no_duration_threshold_is_used(self):
        src=(ROOT/"main.py").read_text("utf-8")
        self.assertNotIn("ATTESTATION_TAIL_MINUTES",src)
        self.assertIn("однозначна суміжність",src)

    def test_missing_adjacent_worklog_does_not_block_form_edit(self):
        con=make_db()
        app=object.__new__(main.App)
        changes=main.App._sync_attestation_boundaries_to_worklog(
            app,con,7,
            "19:45 18.09.2026","07:45 21.09.2026",
            "19:40 18.09.2026","07:45 21.09.2026",
        )
        self.assertEqual(changes,[])
        con.close()


if __name__=="__main__":
    unittest.main()
