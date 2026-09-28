# -*- coding: utf-8 -*-
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

from v1046_features import classify_rest_gaps, free_gaps, rest_timeline_report


def dt(day,hour,minute=0):
    return datetime(2026,9,day,hour,minute)


def hhmm(minutes):
    value=int(round(minutes or 0)); h,m=divmod(abs(value),60)
    return ("-" if value<0 else "")+f"{h}:{m:02d}"


class TestTaxo104R6Compliance(unittest.TestCase):
    def test_internal_night_gap_is_not_hidden_by_day_envelope(self):
        intervals=[
            (dt(3,6,0),dt(3,10,0)),
            (dt(3,13,35),dt(3,20,0)),
            (dt(4,5,30),dt(4,8,0)),
        ]
        gaps=free_gaps(intervals)
        self.assertEqual([g["minutes"] for g in gaps],[215,570])

    def test_335_plus_930_is_regular_split_daily_rest(self):
        gaps=[
            {"start":dt(3,10,0),"end":dt(3,13,35),"minutes":215,"next_date":date(2026,9,3)},
            {"start":dt(3,20,0),"end":dt(4,5,30),"minutes":570,"next_date":date(2026,9,4)},
        ]
        daily,weekly=classify_rest_gaps(gaps)
        self.assertEqual(weekly,[])
        self.assertEqual(len(daily),1)
        self.assertEqual(daily[0]["kind"],"daily_regular")
        self.assertTrue(daily[0]["split"])
        self.assertEqual(daily[0]["first_minutes"],215)
        self.assertEqual(daily[0]["second_minutes"],570)
        self.assertEqual(daily[0]["minutes"],785)

    def test_short_gap_is_not_automatically_called_failed_daily_rest(self):
        gaps=[
            {"start":dt(3,10,0),"end":dt(3,13,35),"minutes":215,"next_date":date(2026,9,3)},
        ]
        daily,weekly=classify_rest_gaps(gaps)
        self.assertEqual(daily,[])
        self.assertEqual(weekly,[])

    def test_report_does_not_emit_legacy_less_than_9_for_valid_3_plus_9(self):
        intervals=[
            (dt(3,6,0),dt(3,10,0)),
            (dt(3,13,35),dt(3,20,0)),
            (dt(4,5,30),dt(4,8,0)),
        ]
        report=rest_timeline_report(intervals,date(2026,9,1),date(2026,9,30),hhmm)
        joined="\n".join(report["warnings"]+report["info"])
        self.assertNotIn("менше 9:00",joined)
        self.assertIn("3:35 + 9:30",joined)
        self.assertIn("модель 3+9",joined)

    def test_r6_source_declares_plan_not_fact(self):
        root=Path(__file__).resolve().parents[1]
        source=(root/"v1046_features.py").read_text("utf-8")
        entry=(root/"taxo_app.py").read_text("utf-8")
        self.assertIn('APP_VERSION = "10.4-r6"',source)
        self.assertIn("ПЛАНОВА ПЕРЕВІРКА",source)
        self.assertIn("не встановлюють фактичного порушення",source)
        self.assertIn("core._worklog_work_intervals",source)
        self.assertNotIn("_row_start_end_dt(row",source)
        self.assertIn("install_v1046",entry)

    def test_waybill_plan_is_not_promoted_to_digital_fact_by_r6(self):
        root=Path(__file__).resolve().parents[1]
        source=(root/"v1046_features.py").read_text("utf-8")
        self.assertIn("рукописний факт шляхівки",source)
        self.assertIn("доки його не внесено",source)
        self.assertIn("_worklog_has_fact_override",source)


if __name__=="__main__":
    unittest.main()
