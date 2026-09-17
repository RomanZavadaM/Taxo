# -*- coding: utf-8 -*-
import tempfile
import unittest
from datetime import date, datetime, time
from pathlib import Path

from activity_register_60 import (
    RAW_REST,
    assign_span,
    classify_and_fill,
    compress_day,
    export_activity_register_pdf,
    new_grid,
    span_datetimes,
    summarize_day,
)


class ActivityRegister60Tests(unittest.TestCase):
    def test_midnight_wrapped_span(self):
        base = date(2026, 9, 17)
        start, end = span_datetimes(base, "22:30", "02:15")
        self.assertEqual(start, datetime(2026, 9, 17, 22, 30))
        self.assertEqual(end, datetime(2026, 9, 18, 2, 15))

    def test_split_workday_fills_break_and_rest(self):
        day = date(2026, 9, 17)
        grid = new_grid(day, day)
        assign_span(grid, datetime.combine(day, time(8, 0)), datetime.combine(day, time(12, 0)),
                    "Інша робота", "test", 60)
        assign_span(grid, datetime.combine(day, time(13, 0)), datetime.combine(day, time(17, 0)),
                    "Інша робота", "test", 60)
        classify_and_fill(grid)
        cells = grid[day]
        self.assertEqual(cells[7 * 60]["activity"], "Відпочинок")
        self.assertEqual(cells[9 * 60]["activity"], "Інша робота")
        self.assertEqual(cells[12 * 60 + 30]["activity"], "Перерва")
        self.assertEqual(cells[18 * 60]["activity"], "Відпочинок")
        summary = summarize_day(cells)
        self.assertEqual(summary["Інша робота"], 8 * 60)
        self.assertEqual(summary["Перерва"], 60)
        self.assertEqual(summary["Відпочинок"], 15 * 60)
        self.assertEqual(sum(summary[k] for k in (
            "Керування", "Інша робота", "Готовність", "Перерва",
            "Відпочинок", "Відсутність", "Невизначено"
        )), 1440)

    def test_tachograph_rest_inside_active_envelope_is_break(self):
        day = date(2026, 9, 17)
        grid = new_grid(day, day)
        assign_span(grid, datetime.combine(day, time(8, 0)), datetime.combine(day, time(10, 0)),
                    "Керування", "tacho", 100)
        assign_span(grid, datetime.combine(day, time(10, 0)), datetime.combine(day, time(10, 30)),
                    RAW_REST, "tacho", 100)
        assign_span(grid, datetime.combine(day, time(10, 30)), datetime.combine(day, time(12, 0)),
                    "Керування", "tacho", 100)
        classify_and_fill(grid)
        self.assertEqual(grid[day][10 * 60 + 15]["activity"], "Перерва")
        self.assertIn("розрахунково", grid[day][10 * 60 + 15]["note"])

    def test_empty_day_is_fully_undefined_not_fake_rest(self):
        day = date(2026, 9, 17)
        grid = new_grid(day, day)
        classify_and_fill(grid)
        summary = summarize_day(grid[day])
        self.assertEqual(summary["Невизначено"], 1440)
        self.assertEqual(summary["Відпочинок"], 0)
        self.assertEqual(summary["Покриття"], 0.0)
        rows = compress_day(grid[day])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["duration_min"], 1440)
        self.assertEqual(rows[0]["activity"], "Невизначено")

    def test_pdf_smoke(self):
        import main as core
        day = date(2026, 9, 17)
        grid = new_grid(day, day)
        assign_span(grid, datetime.combine(day, time(8, 0)), datetime.combine(day, time(12, 0)),
                    "Керування", "ТАХО — підтверджено вручну", 100, vehicle="TEST 123")
        classify_and_fill(grid)
        summary = summarize_day(grid[day])
        data = {
            "driver_name": "Тестовий Водій",
            "start_day": day,
            "end_day": day,
            "period_days": 1,
            "generated_at": datetime(2026, 9, 17, 12, 0),
            "days": [{
                "date": day,
                "day_type": "Робота",
                "summary": summary,
                "intervals": compress_day(grid[day]),
                "warnings": [],
            }],
            "overall": {},
        }
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "activity-register.pdf"
            export_activity_register_pdf(core, data, path)
            self.assertTrue(path.is_file())
            self.assertGreater(path.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
