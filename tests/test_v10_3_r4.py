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
    def test_r4_checkpoint_stays_immutable_under_later_10_3_revisions(self):
        self.assertEqual(main.APP_VERSION,version_from_file(ROOT/"VERSION.txt"))
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
        self.assertIn("не є окремим бланком",src)
        self.assertIn("додається до нього автоматично",src)
        self.assertIn("уточнюється саме межа відпочинку/відсутності",src)
        self.assertIn("Фактичний початок відпочинку / відсутності",src)
        self.assertIn("Фактичне закінчення відпочинку / відсутності",src)
        self.assertIn("не додається автоматично в роботу",src)
        self.assertIn("sync_worklog=False",src)
        self.assertIn("This function is not called automatically by form creation/editing.",src)


    def test_confirmed_edge_gap_is_not_rest_and_not_missing_blank(self):
        ga=datetime(2026,9,21,20,40)
        gb=datetime(2026,9,24,7,35)
        ast=datetime(2026,9,21,20,50)
        aen=datetime(2026,9,24,7,25)
        missing=[(ga,ast),(aen,gb)]
        att_intervals=[(ast,aen,74,16)]
        kept,excluded=main._exclude_confirmed_attestation_edge_gaps(
            ga,gb,missing,att_intervals,{74:(True,True)}
        )
        self.assertEqual(kept,[])
        self.assertEqual(excluded,[(ga,ast),(aen,gb)])

    def test_unconfirmed_edge_gap_stays_for_manual_review(self):
        ga=datetime(2026,9,21,20,40)
        gb=datetime(2026,9,24,7,35)
        ast=datetime(2026,9,21,20,50)
        aen=datetime(2026,9,24,7,25)
        missing=[(ga,ast),(aen,gb)]
        att_intervals=[(ast,aen,74,16)]
        kept,excluded=main._exclude_confirmed_attestation_edge_gaps(
            ga,gb,missing,att_intervals,{74:(False,False)}
        )
        self.assertEqual(kept,missing)
        self.assertEqual(excluded,[])


if __name__=="__main__":
    unittest.main()
