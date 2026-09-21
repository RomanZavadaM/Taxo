# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file


ROOT=Path(__file__).resolve().parents[1]


class TestTaxo103R1DutyBoundaries(unittest.TestCase):
    def test_version_is_10_3_r1_everywhere(self):
        self.assertEqual(main.APP_VERSION,"10.3-r1")
        self.assertEqual(version_from_file(ROOT/"VERSION.txt"),"10.3-r1")
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

    def test_no_global_fixed_rest_buffer_is_introduced(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertNotIn("ATTESTATION_PRE_BUFFER",source)
        self.assertNotIn("ATTESTATION_POST_BUFFER",source)
        self.assertIn("_planned_route_work_margins",source)


if __name__=="__main__":
    unittest.main()
