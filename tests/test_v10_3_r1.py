# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path
import sqlite3
import unittest

import main
from release_naming import start_archive_stem, version_from_file


ROOT=Path(__file__).resolve().parents[1]


class TestTaxo103R1DutyBoundaries(unittest.TestCase):
    def test_r1_checkpoint_remains_immutable(self):
        self.assertEqual(version_from_file(ROOT/"VERSION.txt"),main.APP_VERSION)
        self.assertEqual(
            start_archive_stem("10.3-r1"),
            "Taxo_v10_3_candidate_r1_START",
        )

    def test_route_plan_provides_individual_pre_post_work_margin(self):
        plan=[{
            "start_time":"08:15",
            "end_time":"19:25",
            "work_start_time":"07:55",
            "work_end_time":"19:40",
        }]
        self.assertEqual(main._planned_route_work_margins(plan),(20,15))

    def test_actual_route_shift_preserves_route_work_margin(self):
        row={
            "work_date":"2026-09-21",
            "start_time":"07:25",
            "end_time":"20:40",
            "work_start_time":"07:55",
            "work_end_time":"19:40",
        }
        plan=[{
            "start_time":"08:15",
            "end_time":"19:25",
            "work_start_time":"07:55",
            "work_end_time":"19:40",
        }]
        start,end,pre,post=main._effective_attestation_duty_interval(row,[],plan)
        self.assertEqual(start,datetime(2026,9,21,7,5))
        self.assertEqual(end,datetime(2026,9,21,20,55))
        self.assertEqual((pre,post),(20,15))

    def test_explicit_longer_work_interval_wins_over_route_margin(self):
        row={
            "work_date":"2026-09-21",
            "start_time":"07:25",
            "end_time":"20:40",
            "work_start_time":"06:50",
            "work_end_time":"21:10",
        }
        plan=[{
            "start_time":"08:15",
            "end_time":"19:25",
            "work_start_time":"07:55",
            "work_end_time":"19:40",
        }]
        start,end,pre,post=main._effective_attestation_duty_interval(row,[],plan)
        self.assertEqual(start,datetime(2026,9,21,6,50))
        self.assertEqual(end,datetime(2026,9,21,21,10))
        self.assertEqual((pre,post),(20,15))

    def test_attestation_control_uses_duty_not_route_boundaries(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn("_effective_attestation_duty_interval(",source)
        self.assertIn("route_plan_by_id",source)
        self.assertIn("до початку наступної робочої зміни",source)
        self.assertNotIn(
            "block_start=min(a for a,b in route_parts)\n        block_end=max(b for a,b in route_parts)",
            source,
        )

    def test_attestation_edit_updates_adjacent_work_not_driving(self):
        con=sqlite3.connect(":memory:")
        con.row_factory=sqlite3.Row
        con.executescript("""
            CREATE TABLE worklog(
                id INTEGER PRIMARY KEY,
                driver_id INTEGER NOT NULL,
                work_date TEXT NOT NULL,
                start_time TEXT DEFAULT '',
                end_time TEXT DEFAULT '',
                work_start_time TEXT DEFAULT '',
                work_end_time TEXT DEFAULT '',
                work_hours REAL DEFAULT 0
            );
            CREATE TABLE work_segments(
                id INTEGER PRIMARY KEY,
                worklog_id INTEGER NOT NULL,
                segment_no INTEGER NOT NULL,
                start_time TEXT DEFAULT '',
                end_time TEXT DEFAULT '',
                work_start_time TEXT DEFAULT '',
                work_end_time TEXT DEFAULT '',
                work_hours REAL DEFAULT 0
            );
        """)
        con.execute(
            "INSERT INTO worklog VALUES(1,7,'2026-09-18','08:15','20:40','07:55','19:40',11.75)"
        )
        con.execute(
            "INSERT INTO work_segments VALUES(11,1,1,'08:15','20:40','07:55','19:40',11.75)"
        )
        con.execute(
            "INSERT INTO worklog VALUES(2,7,'2026-09-21','07:25','19:25','07:55','19:40',11.75)"
        )
        con.execute(
            "INSERT INTO work_segments VALUES(21,2,1,'07:25','19:25','07:55','19:40',11.75)"
        )
        app=object.__new__(main.App)
        changes=main.App._sync_attestation_boundaries_to_worklog(
            app,con,7,
            "19:40 18.09.2026","07:55 21.09.2026",
            "20:55 18.09.2026","07:05 21.09.2026",
        )
        self.assertEqual(len(changes),2)

        prev=con.execute("SELECT * FROM worklog WHERE id=1").fetchone()
        nxt=con.execute("SELECT * FROM worklog WHERE id=2").fetchone()
        self.assertEqual(prev["work_end_time"],"20:55")
        self.assertEqual(nxt["work_start_time"],"07:05")
        # Маршрут/керування не переписується бланком.
        self.assertEqual((prev["start_time"],prev["end_time"]),("08:15","20:40"))
        self.assertEqual((nxt["start_time"],nxt["end_time"]),("07:25","19:25"))

        prev_seg=con.execute("SELECT * FROM work_segments WHERE id=11").fetchone()
        nxt_seg=con.execute("SELECT * FROM work_segments WHERE id=21").fetchone()
        self.assertEqual(prev_seg["work_end_time"],"20:55")
        self.assertEqual(nxt_seg["work_start_time"],"07:05")
        con.close()

    def test_attestation_cannot_cut_into_driving_time(self):
        con=sqlite3.connect(":memory:")
        con.row_factory=sqlite3.Row
        con.executescript("""
            CREATE TABLE worklog(
                id INTEGER PRIMARY KEY, driver_id INTEGER, work_date TEXT,
                start_time TEXT, end_time TEXT, work_start_time TEXT,
                work_end_time TEXT, work_hours REAL
            );
            CREATE TABLE work_segments(
                id INTEGER PRIMARY KEY, worklog_id INTEGER, segment_no INTEGER,
                start_time TEXT, end_time TEXT, work_start_time TEXT,
                work_end_time TEXT, work_hours REAL
            );
        """)
        con.execute(
            "INSERT INTO worklog VALUES(1,7,'2026-09-18','08:15','20:40','07:55','20:55',13.0)"
        )
        con.execute(
            "INSERT INTO work_segments VALUES(11,1,1,'08:15','20:40','07:55','20:55',13.0)"
        )
        item={
            "row":con.execute("SELECT * FROM worklog WHERE id=1").fetchone(),
            "segments":con.execute("SELECT * FROM work_segments WHERE worklog_id=1").fetchall(),
        }
        with self.assertRaises(ValueError):
            main.App._set_worklog_boundary(
                con,item,"end",datetime(2026,9,18,20,30)
            )
        row=con.execute("SELECT * FROM worklog WHERE id=1").fetchone()
        self.assertEqual(row["end_time"],"20:40")
        self.assertEqual(row["work_end_time"],"20:55")
        con.close()

    def test_no_global_fixed_rest_buffer_is_introduced(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertNotIn("ATTESTATION_PRE_BUFFER",source)
        self.assertNotIn("ATTESTATION_POST_BUFFER",source)
        self.assertIn("_planned_route_work_margins",source)


if __name__=="__main__":
    unittest.main()
