# -*- coding: utf-8 -*-
import unittest
from datetime import date

from main import (
    driver_day_view,
    gaps_minutes,
    normalized_segment_intervals,
    segment_overlap_details,
    segment_overlap_message,
    segments_overlap_minutes,
    segments_union_minutes,
)


SCREENSHOT_SEGMENTS = [
    {
        "work_start_time": "06:30", "work_end_time": "08:55",
        "start_time": "06:40", "end_time": "08:45",
    },
    {
        "work_start_time": "12:30", "work_end_time": "13:50",
        "start_time": "12:35", "end_time": "13:50",
    },
    {
        "work_start_time": "14:10", "work_end_time": "15:45",
        "start_time": "14:15", "end_time": "15:30",
    },
    {
        "work_start_time": "15:30", "work_end_time": "17:00",
        "start_time": "15:45", "end_time": "17:00",
    },
    {
        "work_start_time": "18:00", "work_end_time": "20:10",
        "start_time": "18:10", "end_time": "20:00",
    },
]


class TestDriverIntervalCanonicalR9(unittest.TestCase):
    def test_screenshot_overlap_is_same_day_not_fake_next_day(self):
        intervals = normalized_segment_intervals(SCREENSHOT_SEGMENTS, "work")
        self.assertEqual(intervals[2]["start"], 14 * 60 + 10)
        self.assertEqual(intervals[3]["start"], 15 * 60 + 30)
        self.assertLess(intervals[3]["start"], intervals[2]["end"])

    def test_screenshot_work_union_is_8h45_not_9h(self):
        self.assertEqual(segments_union_minutes(SCREENSHOT_SEGMENTS, "work"), 8 * 60 + 45)
        self.assertEqual(segments_overlap_minutes(SCREENSHOT_SEGMENTS, "work"), 15)
        self.assertEqual(segments_union_minutes(SCREENSHOT_SEGMENTS, "drive"), 7 * 60 + 40)

    def test_overlap_does_not_create_2345_gap(self):
        self.assertEqual(
            gaps_minutes(SCREENSHOT_SEGMENTS, "work"),
            [3 * 60 + 35, 20, 60],
        )
        self.assertNotIn(23 * 60 + 45, gaps_minutes(SCREENSHOT_SEGMENTS, "work"))

    def test_overlap_message_identifies_adjacent_parts(self):
        details = segment_overlap_details(SCREENSHOT_SEGMENTS, "work")
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0]["left_index"], 2)
        self.assertEqual(details[0]["right_index"], 3)
        self.assertEqual(details[0]["minutes"], 15)
        message = segment_overlap_message(SCREENSHOT_SEGMENTS, "work")
        self.assertIn("№3", message)
        self.assertIn("№4", message)
        self.assertIn("0:15", message)

    def test_driver_day_view_uses_exact_union_for_tab_and_schedule(self):
        row = {
            "day_type": "Робота",
            "work_hours": 9.0,  # legacy stored sum double-counts the overlap
            "driving_hours": 7 + 40 / 60,
            "overtime_hours": 0,
            "work_start_time": "06:30",
            "work_end_time": "20:10",
            "start_time": "06:40",
            "end_time": "20:00",
        }
        state = driver_day_view(date(2026, 9, 19), row, SCREENSHOT_SEGMENTS)
        self.assertEqual(state["work_minutes"], 8 * 60 + 45)
        self.assertEqual(state["driving_minutes"], 7 * 60 + 40)
        self.assertEqual(state["work_overlap_minutes"], 15)
        self.assertIn("перекриття 0:15", state["breaks"])

    def test_real_overnight_rollover_still_works(self):
        segments = [
            {
                "work_start_time": "22:00", "work_end_time": "23:30",
                "start_time": "22:10", "end_time": "23:20",
            },
            {
                "work_start_time": "00:30", "work_end_time": "02:00",
                "start_time": "00:40", "end_time": "01:50",
            },
        ]
        intervals = normalized_segment_intervals(segments, "work")
        self.assertEqual(intervals[1]["start"], 24 * 60 + 30)
        self.assertEqual(gaps_minutes(segments, "work"), [60])
        self.assertFalse(segment_overlap_details(segments, "work"))


if __name__ == "__main__":
    unittest.main()
