# -*- coding: utf-8 -*-
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

from work_rest_compliance import (
    bounded_free_gaps,
    detect_overlaps,
    fortnight_weekly_rest_warnings,
    rest_compliance_report,
)


def dt(day, hour=0, minute=0):
    return datetime(2026, 9, day, hour, minute)


def hhmm(minutes):
    value = int(round(minutes or 0))
    h, m = divmod(abs(value), 60)
    return ("-" if value < 0 else "") + f"{h}:{m:02d}"


class WorkRestComplianceR4Tests(unittest.TestCase):
    def test_boundary_gaps_are_not_discarded(self):
        gaps = bounded_free_gaps([(dt(2, 8), dt(2, 18))], dt(1), dt(4))
        self.assertEqual(gaps[0]["boundary"], "start")
        self.assertEqual(gaps[-1]["boundary"], "end")
        self.assertEqual(gaps[0]["minutes"], 32 * 60)
        self.assertEqual(gaps[-1]["minutes"], 30 * 60)

    def test_no_qualified_rest_is_visible(self):
        intervals = []
        cursor = dt(1, 6)
        for _ in range(7):
            intervals.append((cursor, cursor + timedelta(hours=18)))
            cursor += timedelta(hours=24)
        report = rest_compliance_report(
            intervals, dt(1, 6), dt(8, 6), date(2026, 9, 1), date(2026, 9, 8), hhmm
        )
        joined = "\n".join(report["warnings"])
        self.assertIn("немає жодного кваліфікованого", joined)
        self.assertIn("немає кваліфікованого щотижневого", joined)

    def test_overlap_is_error_not_silently_merged(self):
        overlaps = detect_overlaps([(dt(3, 8), dt(3, 14)), (dt(3, 13), dt(3, 18))])
        self.assertEqual(len(overlaps), 1)
        self.assertEqual(overlaps[0]["minutes"], 60)
        report = rest_compliance_report(
            [(dt(3, 8), dt(3, 14)), (dt(3, 13), dt(3, 18))],
            dt(2), dt(5), date(2026, 9, 1), date(2026, 9, 30), hhmm,
        )
        self.assertTrue(any("помилка даних" in item for item in report["warnings"]))

    def test_valid_split_3_plus_9_remains_accepted(self):
        intervals = [
            (dt(3, 6), dt(3, 10)),
            (dt(3, 13, 35), dt(3, 20)),
            (dt(4, 5, 30), dt(4, 8)),
        ]
        report = rest_compliance_report(
            intervals, dt(2), dt(6), date(2026, 9, 1), date(2026, 9, 30), hhmm
        )
        self.assertTrue(any("3+9" in item for item in report["info"]))
        self.assertFalse(any("менше 9:00" in item for item in report["warnings"]))

    def test_two_reduced_weekly_rests_trigger_fortnight_warning(self):
        weekly = [
            {"start": dt(1), "end": dt(2), "minutes": 24 * 60, "kind": "weekly_reduced"},
            {"start": dt(8), "end": dt(9), "minutes": 24 * 60, "kind": "weekly_reduced"},
        ]
        warnings = fortnight_weekly_rest_warnings(
            weekly, date(2026, 9, 1), date(2026, 9, 14), hhmm
        )
        self.assertTrue(any("жоден не досягає 45:00" in item for item in warnings))

    def test_plan_fact_boundary_is_explicit(self):
        root = Path(__file__).resolve().parents[1]
        source = (root / "work_rest_compliance.py").read_text("utf-8")
        self.assertIn('"control_basis": "plan"', source)
        self.assertIn("_worklog_work_intervals", source)
        self.assertNotIn("fact_work_start", source)
        self.assertNotIn("fact_work_end", source)

    def test_r4_runtime_layer_is_preserved_before_later_revisions(self):
        root = Path(__file__).resolve().parents[1]
        feature = (root / "feature_layers.py").read_text("utf-8")
        main = (root / "main.py").read_text("utf-8")
        version = (root / "VERSION.txt").read_text("utf-8").strip()
        self.assertIn("v1094-work-rest-compliance", feature)
        self.assertRegex(version, r"^Version: 10\.(?:9-r(?:[4-9]|10)|1\d(?:-r\d+)?)$")
        current = version.removeprefix("Version: ")
        self.assertIn(f'APP_VERSION = "{current}"', main)


if __name__ == "__main__":
    unittest.main()
