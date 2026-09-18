# -*- coding: utf-8 -*-
import tempfile
import unittest
from datetime import date
from pathlib import Path

import fitz

from v91_features import (
    PATTERN_2_2,
    PATTERN_SELECTED,
    PATTERN_WEEKDAYS,
    pattern_dates,
    shift_span_minutes,
    widget_alive,
)
from waybill import build_waybill_pdf


class TestV91MonthlyPlanning(unittest.TestCase):
    def test_weekdays_for_full_month_fragment(self):
        rows = pattern_dates(
            date(2026, 9, 1),
            date(2026, 9, 7),
            PATTERN_WEEKDAYS,
        )
        self.assertEqual(
            rows,
            [
                date(2026, 9, 1),
                date(2026, 9, 2),
                date(2026, 9, 3),
                date(2026, 9, 4),
                date(2026, 9, 7),
            ],
        )

    def test_selected_weekdays(self):
        rows = pattern_dates(
            date(2026, 9, 1),
            date(2026, 9, 14),
            PATTERN_SELECTED,
            weekdays={0, 2},  # Monday + Wednesday
        )
        self.assertEqual([d.weekday() for d in rows], [2, 0, 2, 0])

    def test_two_on_two_off_is_anchored_at_start(self):
        rows = pattern_dates(
            date(2026, 9, 1),
            date(2026, 9, 10),
            PATTERN_2_2,
        )
        self.assertEqual(
            rows,
            [
                date(2026, 9, 1),
                date(2026, 9, 2),
                date(2026, 9, 5),
                date(2026, 9, 6),
                date(2026, 9, 9),
                date(2026, 9, 10),
            ],
        )

    def test_overnight_shift_minutes(self):
        self.assertEqual(shift_span_minutes("18:00", "06:00", 1), 12 * 60)
        with self.assertRaises(ValueError):
            shift_span_minutes("18:00", "06:00", 0)

    def test_dead_widget_is_safe(self):
        class DeadWidget:
            def winfo_exists(self):
                raise RuntimeError("destroyed")

        self.assertFalse(widget_alive(DeadWidget()))
        self.assertFalse(widget_alive(None))


class TestV91WaybillRendering(unittest.TestCase):
    def _make_pdf(self, company_name):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        output = Path(tmp.name) / "waybill.pdf"
        data = {
            "company_name": company_name,
            "waybill_no": "001234",
            "waybill_series": "АААТ",
            "date": "18.09.2026",
            "route": "Львів — Винники",
            "vehicle": "Еталон А081 / ВС1234АА",
            "driver": "Тестовий Водій",
            "driver_personnel_no": "17",
            "planned_departure": "06:30",
            "planned_return": "18:15",
            "doctor_1": "Тестовий Лікар",
            "mechanic_1": "Тестовий Механік",
            "outbound_stops": [],
            "return_stops": [],
        }
        build_waybill_pdf(None, output, data)
        return output

    def test_filled_company_replaces_stamp_hint(self):
        output = self._make_pdf("ТОВ АВТОТРАНСПОРТНЕ ПІДПРИЄМСТВО")
        with fitz.open(output) as doc:
            text = "\n".join(page.get_text() for page in doc)
        normalized = " ".join(text.split())
        self.assertIn("ТОВ АВТОТРАНСПОРТНЕ", normalized)
        self.assertNotIn("Місце для штампа", normalized)
        self.assertIn("Тестовий Лікар", normalized)
        self.assertIn("Тестовий Механік", normalized)

    def test_empty_company_keeps_stamp_hint(self):
        output = self._make_pdf("")
        with fitz.open(output) as doc:
            text = doc[0].get_text()
        self.assertIn("Місце для штампа", text)


if __name__ == "__main__":
    unittest.main()
