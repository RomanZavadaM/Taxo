# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import v1044_features


class TestTaxo104R4WaybillAndAudit(unittest.TestCase):
    def test_route_boundary_prefers_first_departure_and_final_arrival(self):
        stops=[
            {"direction":"outbound","stop_no":1,"stop_name":"Муроване","point_type":"АТП",
             "arrival_time":"","departure_time":"07:30","day_offset":0,
             "arrival_day_offset":0,"departure_day_offset":0},
            {"direction":"outbound","stop_no":2,"stop_name":"Львів",
             "arrival_time":"08:15","departure_time":"","day_offset":0,
             "arrival_day_offset":0,"departure_day_offset":0},
            {"direction":"return","stop_no":1,"stop_name":"Золочів АС",
             "arrival_time":"09:35","departure_time":"10:15","day_offset":0,
             "arrival_day_offset":0,"departure_day_offset":0},
            {"direction":"return","stop_no":4,"stop_name":"Муроване","point_type":"АТП",
             "arrival_time":"19:50","departure_time":"","day_offset":0,
             "arrival_day_offset":0,"departure_day_offset":0},
        ]
        boundary=v1044_features._route_boundary_times(stops,"outbound")
        self.assertEqual(boundary["start_time"],"07:30")
        self.assertEqual(boundary["start_stop"],"Муроване")
        self.assertEqual(boundary["end_time"],"19:50")
        self.assertEqual(boundary["end_stop"],"Муроване")

    def test_uploaded_waybill_example_is_reported_as_boundary_mismatch(self):
        segment={
            "start_time":"07:55","start_day_offset":0,
            "end_time":"19:40","end_day_offset":0,
        }
        stops={
            "start_time":"07:30","start_day_offset":0,"start_stop":"Муроване",
            "end_time":"19:50","end_day_offset":0,"end_stop":"Муроване",
        }
        base={
            "source_kind":"route","source":"Шаблон маршруту","worklog_id":None,
            "driver_id":None,"route_id":751,"date":"",
            "subject":"751 / Львів - Золочів АС - Поморяни",
            "route":"751 / Львів - Золочів АС - Поморяни",
        }
        findings=v1044_features._boundary_mismatch_findings(segment,stops,base)
        self.assertEqual([x["kind"] for x in findings],[
            "route_start_boundary_mismatch","route_end_boundary_mismatch"
        ])
        self.assertEqual(findings[0]["minutes"],25)
        self.assertEqual(findings[1]["minutes"],10)
        self.assertIn("07:55",findings[0]["message"])
        self.assertIn("07:30",findings[0]["message"])
        self.assertIn("19:40",findings[1]["message"])
        self.assertIn("19:50",findings[1]["message"])

    def test_audit_augmentation_finds_boundary_conflict_in_day_and_route(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"audit.sqlite3"
            con=sqlite3.connect(path)
            con.executescript("""
                CREATE TABLE drivers(id INTEGER PRIMARY KEY,last_name TEXT,first_name TEXT,middle_name TEXT);
                CREATE TABLE routes(
                    id INTEGER PRIMARY KEY,name TEXT,code TEXT,active INTEGER DEFAULT 1,
                    start_direction TEXT DEFAULT 'outbound',start_day_offset INTEGER DEFAULT 0,
                    end_day_offset INTEGER DEFAULT 0
                );
                CREATE TABLE worklog(
                    id INTEGER PRIMARY KEY,driver_id INTEGER,work_date TEXT,route_id INTEGER,
                    route_name TEXT,start_time TEXT,end_time TEXT
                );
                CREATE TABLE work_segments(
                    id INTEGER PRIMARY KEY,worklog_id INTEGER,segment_no INTEGER,
                    start_time TEXT,end_time TEXT,work_start_time TEXT,work_end_time TEXT
                );
                CREATE TABLE route_segments(
                    id INTEGER PRIMARY KEY,route_id INTEGER,segment_no INTEGER,
                    start_time TEXT,end_time TEXT,work_start_time TEXT,work_end_time TEXT
                );
                CREATE TABLE route_stops(
                    id INTEGER PRIMARY KEY,route_id INTEGER,direction TEXT,stop_no INTEGER,
                    stop_name TEXT,arrival_time TEXT,departure_time TEXT,note TEXT,
                    day_offset INTEGER DEFAULT 0,arrival_day_offset INTEGER DEFAULT 0,
                    departure_day_offset INTEGER DEFAULT 0,point_type TEXT DEFAULT 'Зупинка'
                );
                INSERT INTO drivers VALUES(1,'Цінкало','Дмитро','Петрович');
                INSERT INTO routes VALUES(751,'Львів - Золочів АС - Поморяни','751',1,'outbound',0,0);
                INSERT INTO worklog VALUES(9,1,'2026-09-22',751,'','07:55','19:40');
                INSERT INTO work_segments VALUES(1,9,1,'07:55','19:40','07:45','19:50');
                INSERT INTO route_segments VALUES(1,751,1,'07:55','19:40','07:45','19:50');
                INSERT INTO route_stops VALUES(1,751,'outbound',1,'Муроване','','07:30','',0,0,0,'АТП');
                INSERT INTO route_stops VALUES(2,751,'return',4,'Муроване','19:50','','',0,0,0,'АТП');
            """)
            con.commit(); con.close()

            def db():
                cx=sqlite3.connect(path)
                cx.row_factory=sqlite3.Row
                return cx

            core=SimpleNamespace(db=db)
            original=lambda *a,**k:{
                "findings":[],"day_findings":0,"route_findings":0,
                "inspected_day_records":1,"exact_day_records":1,
                "legacy_exact_day_records":0,"inspected_route_records":1,
            }
            data=v1044_features.augment_schedule_audit(
                core,original,2026,9,True,"2026-09-22",True,True
            )
            day=[x for x in data["findings"] if x["source_kind"]=="worklog"]
            route=[x for x in data["findings"] if x["source_kind"]=="route"]
            self.assertEqual({x["kind"] for x in day},{
                "route_start_boundary_mismatch","route_end_boundary_mismatch"
            })
            self.assertEqual({x["kind"] for x in route},{
                "route_start_boundary_mismatch","route_end_boundary_mismatch"
            })

    def test_candidate_identity_is_r4(self):
        root=Path(__file__).resolve().parents[1]
        version=(root/"VERSION.txt").read_text("utf-8")
        entry=(root/"taxo_app.py").read_text("utf-8")
        self.assertIn("Version: 10.4-r4",version)
        self.assertIn("install_v1044",entry)
        self.assertIn("APP_VERSION = \"10.4-r4\"",(root/"v1044_features.py").read_text("utf-8"))


if __name__=="__main__":
    unittest.main()
