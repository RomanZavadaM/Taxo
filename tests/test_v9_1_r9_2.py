# -*- coding: utf-8 -*-
import unittest

from main import segment_integrity_issues


class TestScheduleIntegrityAuditR92(unittest.TestCase):
    def test_corrected_split_day_has_no_integrity_issue(self):
        segments = [
            {
                "work_start_time": "06:30", "work_end_time": "08:55",
                "start_time": "06:40", "end_time": "08:45",
            },
            {
                "work_start_time": "12:30", "work_end_time": "13:50",
                "start_time": "12:35", "end_time": "13:50",
            },
            {
                "work_start_time": "14:10", "work_end_time": "15:30",
                "start_time": "14:15", "end_time": "15:30",
            },
            {
                "work_start_time": "15:45", "work_end_time": "17:00",
                "start_time": "15:45", "end_time": "17:00",
            },
        ]
        self.assertEqual(segment_integrity_issues(segments), [])

    def test_existing_work_overlap_is_found(self):
        segments = [
            {
                "work_start_time": "14:10", "work_end_time": "15:45",
                "start_time": "14:15", "end_time": "15:30",
            },
            {
                "work_start_time": "15:30", "work_end_time": "17:00",
                "start_time": "15:45", "end_time": "17:00",
            },
        ]
        issues = segment_integrity_issues(segments)
        overlaps = [x for x in issues if x["kind"] == "work_overlap"]
        self.assertEqual(len(overlaps), 1)
        self.assertEqual(overlaps[0]["minutes"], 15)
        self.assertIn("перекриваються", overlaps[0]["message"])

    def test_driving_overlap_is_checked_separately(self):
        segments = [
            {
                "work_start_time": "08:00", "work_end_time": "11:00",
                "start_time": "08:10", "end_time": "10:00",
            },
            {
                "work_start_time": "11:00", "work_end_time": "13:00",
                "start_time": "09:50", "end_time": "12:30",
            },
        ]
        issues = segment_integrity_issues(segments)
        self.assertTrue(any(x["kind"] == "drive_overlap" for x in issues))

    def test_driving_outside_work_is_found(self):
        segments = [
            {
                "work_start_time": "08:00", "work_end_time": "10:00",
                "start_time": "07:50", "end_time": "09:30",
            }
        ]
        issues = segment_integrity_issues(segments)
        self.assertTrue(any(x["kind"] == "drive_outside_work" for x in issues))

    def test_incomplete_clock_pair_is_found(self):
        segments = [
            {
                "work_start_time": "08:00", "work_end_time": "10:00",
                "start_time": "08:10", "end_time": "",
            }
        ]
        issues = segment_integrity_issues(segments)
        self.assertTrue(any(x["kind"] == "incomplete_drive" for x in issues))


if __name__ == "__main__":
    unittest.main()
