# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main
from release_naming import version_from_file


def make_audit_db(path):
    con=sqlite3.connect(path)
    con.executescript("""
    CREATE TABLE drivers(
        id INTEGER PRIMARY KEY,
        last_name TEXT, first_name TEXT, middle_name TEXT
    );
    CREATE TABLE routes(
        id INTEGER PRIMARY KEY,
        name TEXT,
        code TEXT,
        active INTEGER DEFAULT 1
    );
    CREATE TABLE worklog(
        id INTEGER PRIMARY KEY,
        driver_id INTEGER,
        work_date TEXT,
        start_time TEXT DEFAULT '',
        end_time TEXT DEFAULT '',
        work_start_time TEXT DEFAULT '',
        work_end_time TEXT DEFAULT '',
        route_name TEXT DEFAULT '',
        route_id INTEGER
    );
    CREATE TABLE work_segments(
        id INTEGER PRIMARY KEY,
        worklog_id INTEGER,
        segment_no INTEGER,
        start_time TEXT DEFAULT '',
        end_time TEXT DEFAULT '',
        work_start_time TEXT DEFAULT '',
        work_end_time TEXT DEFAULT ''
    );
    CREATE TABLE route_segments(
        id INTEGER PRIMARY KEY,
        route_id INTEGER,
        segment_no INTEGER,
        start_time TEXT DEFAULT '',
        end_time TEXT DEFAULT '',
        work_start_time TEXT DEFAULT '',
        work_end_time TEXT DEFAULT ''
    );

    INSERT INTO drivers VALUES(1,'Дробот','Олег','Богданович');
    INSERT INTO routes VALUES(10,'Львів АС-2 - Бібрка','674',1);
    INSERT INTO routes VALUES(11,'Порожній активний маршрут','999',1);

    INSERT INTO worklog(
        id,driver_id,work_date,start_time,end_time,
        work_start_time,work_end_time,route_name,route_id
    ) VALUES
        (100,1,'2026-09-11','','','','','',10),
        (101,1,'2026-09-12','08:10','','08:00','10:00','',10);

    INSERT INTO work_segments VALUES
        (1,100,1,'06:40','08:45','06:30','08:55'),
        (2,100,2,'12:35','13:50','12:30','13:50'),
        (3,100,3,'14:15','15:30','14:10','15:30'),
        (4,100,4,'15:45','17:00','15:45','17:00'),
        (5,100,5,'18:10','20:00','18:00','20:10');

    INSERT INTO route_segments VALUES
        (1,10,1,'08:00','10:00','07:50','10:10'),
        (2,10,2,'09:50','12:00','10:00','12:10');
    """)
    con.commit()
    con.close()


class TestScheduleAuditR94(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"audit.sqlite3"
        make_audit_db(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def db(self):
        con=sqlite3.connect(self.path)
        con.row_factory=sqlite3.Row
        return con

    def test_current_day_scope_does_not_scan_routes(self):
        with patch.object(main,"db",self.db):
            data=main.collect_schedule_integrity_audit(
                2026,9,work_date="2026-09-11",
                include_days=True,include_routes=False
            )
        self.assertEqual(data["inspected_day_records"],1)
        self.assertEqual(data["inspected_route_records"],0)
        self.assertEqual(data["findings"],[])

    def test_legacy_exact_row_without_segments_is_still_checked(self):
        with patch.object(main,"db",self.db):
            data=main.collect_schedule_integrity_audit(
                2026,9,work_date="2026-09-12",
                include_days=True,include_routes=False
            )
        self.assertEqual(data["legacy_exact_day_records"],1)
        self.assertTrue(any(x["kind"]=="incomplete_drive" for x in data["findings"]))
        finding=next(x for x in data["findings"] if x["kind"]=="incomplete_drive")
        self.assertEqual(finding["route"],"674 / Львів АС-2 - Бібрка")

    def test_route_only_scope_finds_template_overlap(self):
        with patch.object(main,"db",self.db):
            data=main.collect_schedule_integrity_audit(
                2026,9,include_days=False,include_routes=True
            )
        self.assertEqual(data["inspected_day_records"],0)
        self.assertEqual(data["inspected_route_records"],2)
        overlaps=[x for x in data["findings"] if x["kind"]=="drive_overlap"]
        self.assertEqual(len(overlaps),1)
        self.assertEqual(overlaps[0]["source"],"Шаблон маршруту")
        self.assertEqual(overlaps[0]["route"],"674 / Львів АС-2 - Бібрка")
        missing=[x for x in data["findings"] if x["kind"]=="route_no_segments"]
        self.assertEqual(len(missing),1)
        self.assertEqual(missing[0]["route"],"999 / Порожній активний маршрут")

    def test_empty_segment_is_flagged(self):
        issues=main.segment_integrity_issues([{
            "start_time":"","end_time":"",
            "work_start_time":"","work_end_time":"",
        }])
        self.assertTrue(any(x["kind"]=="empty_segment" for x in issues))

    def test_daily_status_distinguishes_no_records_from_clean_exact_data(self):
        self.assertEqual(
            main.schedule_audit_day_status_text({
                "findings":[], "inspected_day_records":0, "exact_day_records":0
            }),
            "○ день: записів для аудиту немає",
        )
        self.assertEqual(
            main.schedule_audit_day_status_text({
                "findings":[], "inspected_day_records":1, "exact_day_records":0
            }),
            "○ день: є запис, але точний час не задано",
        )
        self.assertEqual(
            main.schedule_audit_day_status_text({
                "findings":[], "inspected_day_records":1, "exact_day_records":1
            }),
            "✓ день: помилок введення немає",
        )

    def test_daily_status_reports_problem_count(self):
        self.assertEqual(
            main.schedule_audit_day_status_text({
                "findings":[{"kind":"x"},{"kind":"y"}],
                "inspected_day_records":1,
                "exact_day_records":1,
            }),
            "⚠ день: 2 помилк.",
        )


    def test_release_safety_and_version_markers(self):
        root=Path(__file__).resolve().parents[1]
        for ver in ("r7","r8"):
            workflow=(root/f".github/workflows/publish-v9.1-{ver}-source.yml").read_text("utf-8")
            self.assertIn("workflow_dispatch:",workflow)
            self.assertNotIn("gh release upload",workflow)
            self.assertIn(f"ref: v9.1-{ver}",workflow)
            self.assertIn("refusing to overwrite",workflow)

        gitignore=(root/".gitignore").read_text("utf-8")
        self.assertIn("Taxo_v9_1_candidate_r*_Windows_x64_Portable.zip",gitignore)
        self.assertIn("SHA256SUMS_v9_1_candidate_r*.txt",gitignore)

        current = version_from_file(root / "VERSION.txt")
        self.assertRegex(
            current,
            r"^(?:9\.1 candidate r\d+(?:\.\d+)*|10\.\d+(?:\.\d+)?(?:-r\d+(?:\.\d+)*)?)$",
        )
        version=(root/"VERSION.txt").read_text("utf-8")
        self.assertIn(f"Version: {current}",version)
        self.assertIn(current,(root/"v91_features.py").read_text("utf-8"))
        self.assertIn(current,(root/"personnel_v91.py").read_text("utf-8"))
        self.assertIn(current,(root/"taxo_app.py").read_text("utf-8"))

if __name__=="__main__":
    unittest.main()
