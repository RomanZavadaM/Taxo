# -*- coding: utf-8 -*-
import re
import sqlite3
import unittest
from pathlib import Path

import v1071_features as r1


class CircularRunTests(unittest.TestCase):
    def test_wraparound_run_is_preserved(self):
        mask = [True, True, False, False, False, False, False, False, True, True]
        self.assertEqual(r1.circular_runs(mask, min_len=2), [(8, 12)])

    def test_internal_runs_are_preserved(self):
        mask = [False, True, True, False, True, True, True, False]
        self.assertEqual(r1.circular_runs(mask, min_len=2), [(1, 3), (4, 7)])

    def test_empty_mask(self):
        self.assertEqual(r1.circular_runs([False, False, False], min_len=1), [])


class TimelineSegmentTests(unittest.TestCase):
    def test_cross_midnight_is_split(self):
        self.assertEqual(r1.timeline_segments(23 * 60, 60), [(1380, 1440), (0, 60)])

    def test_normal_interval_is_single_segment(self):
        self.assertEqual(r1.timeline_segments(8 * 60, 17 * 60), [(480, 1020)])

    def test_equal_endpoints_are_zero_duration(self):
        self.assertEqual(r1.timeline_segments(480, 480), [])


class ManualIntervalPreservationTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.execute(
            """CREATE TABLE intervals(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disc_id INTEGER NOT NULL,
                start_min INTEGER NOT NULL,
                end_min INTEGER NOT NULL,
                activity TEXT NOT NULL,
                confidence REAL DEFAULT 0,
                source TEXT DEFAULT 'auto',
                note TEXT DEFAULT ''
            )"""
        )
        self.con.execute(
            "INSERT INTO intervals(disc_id,start_min,end_min,activity,confidence,source) VALUES(1,60,120,'Інша робота',1.0,'manual')"
        )
        self.con.execute(
            "INSERT INTO intervals(disc_id,start_min,end_min,activity,confidence,source) VALUES(1,180,240,'Керування',0.4,'auto')"
        )
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def test_auto_refresh_keeps_manual_rows(self):
        r1.replace_auto_intervals(
            self.con,
            1,
            [(300, 360, "Керування", 0.7)],
        )
        self.con.commit()
        rows = self.con.execute(
            "SELECT start_min,end_min,activity,source FROM intervals WHERE disc_id=1 ORDER BY id"
        ).fetchall()
        self.assertEqual(
            rows,
            [
                (60, 120, "Інша робота", "manual"),
                (300, 360, "Керування", "auto"),
            ],
        )


class R1IdentityTests(unittest.TestCase):
    def test_taxo_app_keeps_r1_in_runtime_chain(self):
        text = Path("taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from v1071_features import install as install_v1071", text)
        self.assertIn("App = install_v1071(core, App)", text)

    def test_current_version_is_not_before_historical_r1(self):
        text = Path("VERSION.txt").read_text(encoding="utf-8")
        match = re.search(r"Version:\s*(\d+)\.(\d+)-r(\d+)", text)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(tuple(map(int, match.groups())), (10, 7, 1))

    def test_r1_feature_layer_keeps_historical_identity(self):
        text = Path("v1071_features.py").read_text(encoding="utf-8")
        self.assertIn('APP_VERSION = "10.7-r1"', text)


if __name__ == "__main__":
    unittest.main()
