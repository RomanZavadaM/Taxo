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


class TestTaxo103R2FactualOverrides(unittest.TestCase):
    def test_version_is_r2(self):
        self.assertEqual(main.APP_VERSION,"10.3-r2")
        self.assertEqual(version_from_file(ROOT/"VERSION.txt"),"10.3-r2")
        self.assertEqual(
            start_archive_stem("10.3-r2"),
            "Taxo_v10_3_candidate_r2_START",
        )

    def test_ordinary_day_plan_is_default_fact(self):
        row={
            "work_date":"2026-09-21",
            "work_start_time":"07:55",
            "work_end_time":"19:40",
            "start_time":"08:15",
            "end_time":"19:25",
            "fact_work_start_time":"",
            "fact_work_end_time":"",
            "fact_work_hours":None,
        }
        parts=main._worklog_effective_work_intervals(row,[])
        self.assertEqual(parts,[
            (datetime(2026,9,21,7,55),datetime(2026,9,21,19,40))
        ])
        self.assertFalse(main._worklog_has_fact_override(row))

    def test_breakdown_can_finish_work_before_planned_route_end(self):
        row={
            "work_date":"2026-09-21",
            "work_start_time":"07:55",
            "work_end_time":"20:55",
            "start_time":"08:15",
            "end_time":"20:40",
            "fact_work_start_time":"",
            "fact_work_end_time":"13:20",
            "fact_work_hours":None,
        }
        plan=[{
            "work_start_time":"07:55","work_end_time":"20:55",
            "start_time":"08:15","end_time":"20:40",
        }]
        start,end,_pre,_post=main._effective_attestation_duty_interval(row,[],plan)
        self.assertEqual(start,datetime(2026,9,21,7,55))
        self.assertEqual(end,datetime(2026,9,21,13,20))

    def test_attestation_correction_keeps_original_plan(self):
        con=make_db()
        con.execute(
            """INSERT INTO worklog(
                id,driver_id,work_date,start_time,end_time,
                work_start_time,work_end_time,work_hours
            ) VALUES(1,7,'2026-09-21','08:15','20:40','07:55','20:55',13.0)"""
        )
        item={"row":con.execute("SELECT * FROM worklog WHERE id=1").fetchone(),"segments":[]}
        main.App._set_worklog_boundary(
            con,item,"end",datetime(2026,9,21,13,20)
        )
        row=con.execute("SELECT * FROM worklog WHERE id=1").fetchone()
        self.assertEqual((row["work_start_time"],row["work_end_time"]),("07:55","20:55"))
        self.assertEqual((row["start_time"],row["end_time"]),("08:15","20:40"))
        self.assertEqual(row["fact_work_end_time"],"13:20")
        self.assertEqual(row["fact_source"],"attestation")
        self.assertAlmostEqual(float(row["fact_work_hours"]),5+25/60,places=4)
        con.close()

    def test_sickness_after_lunch_shortens_fact_not_plan(self):
        con=make_db()
        con.execute(
            """INSERT INTO worklog(
                id,driver_id,work_date,start_time,end_time,
                work_start_time,work_end_time,work_hours
            ) VALUES(1,7,'2026-09-21','08:15','17:30','07:55','18:00',9.0)"""
        )
        app=object.__new__(main.App)
        changes=main.App._sync_new_nonwork_attestation_to_worklog(
            app,con,7,
            "13:20 21.09.2026","07:00 24.09.2026",14
        )
        self.assertEqual(len(changes),1)
        row=con.execute("SELECT * FROM worklog WHERE id=1").fetchone()
        self.assertEqual(row["work_end_time"],"18:00")
        self.assertEqual(row["fact_work_end_time"],"13:20")
        self.assertEqual(row["day_type"],"Робота")
        con.close()

    def test_work_activity_form_does_not_trim_work(self):
        con=make_db()
        con.execute(
            """INSERT INTO worklog(
                id,driver_id,work_date,start_time,end_time,
                work_start_time,work_end_time,work_hours
            ) VALUES(1,7,'2026-09-21','08:15','17:30','07:55','18:00',9.0)"""
        )
        app=object.__new__(main.App)
        changes=main.App._sync_new_nonwork_attestation_to_worklog(
            app,con,7,
            "13:20 21.09.2026","17:00 21.09.2026",18
        )
        self.assertEqual(changes,[])
        row=con.execute("SELECT * FROM worklog WHERE id=1").fetchone()
        self.assertEqual(row["fact_work_end_time"],"")
        con.close()

    def test_driver_day_view_uses_fact_only_when_requested(self):
        row={
            "work_date":"2026-09-21",
            "day_type":"Робота",
            "work_start_time":"07:55",
            "work_end_time":"18:00",
            "work_hours":10.083333,
            "start_time":"08:15",
            "end_time":"17:30",
            "driving_hours":9.25,
            "overtime_hours":0,
            "fact_work_start_time":"",
            "fact_work_end_time":"13:20",
            "fact_work_hours":5+25/60,
            "fact_source":"attestation",
        }
        plan=main.driver_day_view(datetime(2026,9,21).date(),row,[],use_fact=False)
        fact=main.driver_day_view(datetime(2026,9,21).date(),row,[],use_fact=True)
        self.assertEqual(plan["work_minutes"],605)
        self.assertEqual(fact["work_minutes"],325)
        self.assertFalse(plan["fact_applied"])
        self.assertTrue(fact["fact_applied"])

    def test_current_prepare_workflow_is_preserved(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn('status="ПОТОЧНИЙ — ПІДГОТУВАТИ"',source)
        self.assertIn("create_selected_gap_attestation",source)
        self.assertIn("factual_completed=(en <= datetime.now())",source)
        self.assertIn('basis="фактичний" if factual_completed else "підготовлено за планом до виїзду"',source)

    def test_schema_contains_sparse_fact_fields(self):
        source=(ROOT/"main.py").read_text("utf-8")
        for field in (
            "fact_work_start_time","fact_work_end_time","fact_work_hours",
            "fact_source","fact_updated_at",
        ):
            self.assertIn(field,source)


if __name__=="__main__":
    unittest.main()
