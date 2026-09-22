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
    def test_r3_checkpoint_stays_immutable_under_later_10_3_revisions(self):
        self.assertEqual(main.APP_VERSION,version_from_file(ROOT/"VERSION.txt"))
        self.assertEqual(
            start_archive_stem("10.3-r3"),
            "Taxo_v10_3_candidate_r3_START",
        )

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
