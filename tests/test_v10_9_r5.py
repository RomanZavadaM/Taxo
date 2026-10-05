# -*- coding: utf-8 -*-
import unittest
from datetime import date, datetime, time
from pathlib import Path

import activity_register_60 as register


class ActivityRegisterSafetyR5Tests(unittest.TestCase):
    def test_missing_minutes_are_not_inferred_as_rest_or_break(self):
        day = date(2026, 10, 1)
        grid = register.new_grid(day, day)
        register.assign_span(grid, datetime.combine(day, time(8)), datetime.combine(day, time(9)), "Керування", "confirmed", 70)
        register.assign_span(grid, datetime.combine(day, time(10)), datetime.combine(day, time(11)), "Інша робота", "confirmed", 65)
        register.classify_and_fill(grid)
        self.assertEqual(grid[day][9 * 60 + 30]["activity"], "Невизначено")
        self.assertEqual(grid[day][7 * 60]["activity"], "Невизначено")
        self.assertEqual(grid[day][12 * 60]["activity"], "Невизначено")

    def test_explicit_tachograph_rest_is_still_classified(self):
        day = date(2026, 10, 1)
        grid = register.new_grid(day, day)
        register.assign_span(grid, datetime.combine(day, time(8)), datetime.combine(day, time(9)), "Керування", "manual", 100)
        register.assign_span(grid, datetime.combine(day, time(9)), datetime.combine(day, time(9, 30)), register.RAW_REST, "manual", 100)
        register.assign_span(grid, datetime.combine(day, time(9, 30)), datetime.combine(day, time(10)), "Керування", "manual", 100)
        register.assign_span(grid, datetime.combine(day, time(18)), datetime.combine(day, time(19)), register.RAW_REST, "manual", 100)
        register.classify_and_fill(grid)
        self.assertEqual(grid[day][9 * 60 + 10]["activity"], "Перерва")
        self.assertEqual(grid[day][18 * 60 + 10]["activity"], "Відпочинок")

    def test_auto_candidate_cannot_replace_confirmed_work(self):
        day = date(2026, 10, 1)
        grid = register.new_grid(day, day)
        register.assign_minute(grid[day], 500, "Інша робота", "Факт роботи", 65)
        register.assign_minute(grid[day], 500, "Керування", "ТАХО — авто-кандидат", 40)
        self.assertEqual(grid[day][500]["activity"], "Інша робота")
        self.assertEqual(grid[day][500]["source"], "Факт роботи")

    def test_manual_tachograph_can_replace_lower_priority_source(self):
        day = date(2026, 10, 1)
        grid = register.new_grid(day, day)
        register.assign_minute(grid[day], 500, "Інша робота", "Факт роботи", 65)
        register.assign_minute(grid[day], 500, "Керування", "ТАХО — підтверджено вручну", 100)
        self.assertEqual(grid[day][500]["activity"], "Керування")

    def test_source_contains_safe_auto_priority(self):
        source = Path(register.__file__).read_text(encoding="utf-8")
        self.assertIn("100 if manual else 40", source)
        self.assertNotIn("100 if manual else 80", source)
        self.assertIn("відпочинок не припускається автоматично", source)

    def test_r5_identity_is_historical_after_rollover(self):
        root = Path(__file__).resolve().parents[1]
        notes = root / "docs" / "releases" / "RELEASE_NOTES_v10.9-r5.md"
        audit = root / "docs" / "maintenance" / "AUDIT_TACHOGRAPH_ACTIVITY_SAFETY_v10.9-r5.md"
        self.assertTrue(notes.is_file())
        self.assertTrue(audit.is_file())
        self.assertIn("10.9-r5", notes.read_text("utf-8"))
        current = (root / "VERSION.txt").read_text("utf-8").strip()
        self.assertRegex(current, r"^Version: 10\.(?:9-r(?:[6-9]|10)|1\d(?:-r\d+)?)$")


if __name__ == "__main__":
    unittest.main()
