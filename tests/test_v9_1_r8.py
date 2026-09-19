# -*- coding: utf-8 -*-
import unittest
from datetime import date

from main import driver_day_view


class TestDriverDayViewR8(unittest.TestCase):
    def test_explicit_weekend_is_not_blank_on_schedule(self):
        row = {
            "day_type": "Вихідний",
            "work_hours": 0,
            "driving_hours": 0,
            "overtime_hours": 0,
            "work_start_time": "",
            "work_end_time": "",
            "start_time": "",
            "end_time": "",
        }
        state = driver_day_view(date(2026, 9, 19), row, [])
        self.assertEqual(state["day_type"], "Вихідний")
        self.assertEqual(state["status_label"], "Вихідний")
        self.assertEqual(state["bands"], [])
        self.assertEqual(state["work_minutes"], 0)
        self.assertEqual(state["driving_minutes"], 0)

    def test_empty_weekend_has_same_effective_state(self):
        state = driver_day_view(date(2026, 9, 19), None, [])
        self.assertEqual(state["day_type"], "Вихідний")
        self.assertEqual(state["status_label"], "Вихідний")
        self.assertEqual(state["bands"], [])

    def test_work_segments_feed_both_work_and_driving_bands(self):
        row = {
            "day_type": "Робота",
            "work_hours": 2.5,
            "driving_hours": 2.0,
            "overtime_hours": 0,
            "work_start_time": "06:30",
            "work_end_time": "09:00",
            "start_time": "06:40",
            "end_time": "08:40",
        }
        segments = [{
            "work_start_time": "06:30",
            "work_end_time": "09:00",
            "start_time": "06:40",
            "end_time": "08:40",
        }]
        state = driver_day_view(date(2026, 9, 18), row, segments)
        self.assertEqual(state["status_label"], "")
        self.assertIn(("Робота", "06:30", "09:00"), state["bands"])
        self.assertIn(("Керування", "06:40", "08:40"), state["bands"])
        self.assertEqual(state["work_minutes"], 150)
        self.assertEqual(state["driving_minutes"], 120)

    def test_personnel_absence_suppresses_historical_plan_without_deleting_it(self):
        row = {
            "day_type": "Робота",
            "work_hours": 8,
            "driving_hours": 7,
            "overtime_hours": 0,
            "work_start_time": "06:00",
            "work_end_time": "14:00",
            "start_time": "06:15",
            "end_time": "13:15",
        }
        segments = [{
            "work_start_time": "06:00",
            "work_end_time": "14:00",
            "start_time": "06:15",
            "end_time": "13:15",
        }]
        state = driver_day_view(
            date(2026, 9, 18),
            row,
            segments,
            day_type_override="Основна щорічна відпустка",
            suppress_plan=True,
        )
        self.assertEqual(state["day_type"], "Основна щорічна відпустка")
        self.assertEqual(state["status_label"], "Основна щорічна відпустка")
        self.assertEqual(state["bands"], [])
        self.assertEqual(state["work_minutes"], 0)
        self.assertEqual(state["driving_minutes"], 0)
        self.assertTrue(state["suppressed_plan"])


if __name__ == "__main__":
    unittest.main()
