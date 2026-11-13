# -*- coding: utf-8 -*-
"""10.17-r10: sortable order-history timestamps and read-only dialog."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import main
import order_register_ui
from table_sorting import sorted_row_ids

ROOT = Path(__file__).resolve().parents[1]


class OrderHistorySortingR10Tests(unittest.TestCase):
    def test_candidate_identity(self):
        self.assertIn(main.APP_VERSION, ("10.17-r10", "10.18-r1", "10.18-r2", "10.18-r3", "10.18-r4", "10.18-r5"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        self.assertIn("Taxo " + main.APP_VERSION, (ROOT / "START.bat").read_text("utf-8"))

    def test_same_day_timestamp_sort_uses_time_not_just_date(self):
        rows = [
            ("late", "2026-11-12 15:10:02"),
            ("early", "2026-11-12 08:02:01"),
            ("other", "2025-12-31 23:59:59"),
            ("empty", ""),
        ]
        self.assertEqual(
            sorted_row_ids(rows, "at", value_type="datetime"),
            ["other", "early", "late", "empty"],
        )
        self.assertEqual(
            sorted_row_ids(rows, "at", True, value_type="datetime"),
            ["late", "early", "other", "empty"],
        )

    def test_timestamp_accepts_iso_and_local_display(self):
        rows = [
            ("utc", "2026-11-12T15:00:00Z"),
            ("local", "12.11.2026 14:59"),
            ("iso", "2026-11-12 15:01:00"),
        ]
        self.assertEqual(
            sorted_row_ids(rows, "at", value_type="datetime"),
            ["local", "utc", "iso"],
        )

    def test_history_dialog_has_four_clickable_headings(self):
        source = inspect.getsource(order_register_ui.install_order_register)
        self.assertIn('("at", "Коли", 170, "datetime")', source)
        self.assertIn('("entity", "Об\'єкт", 120, "text")', source)
        self.assertIn('("action", "Дія", 150, "text")', source)
        self.assertIn('("note", "Примітка", 420, "text")', source)
        self.assertIn("command=lambda name=key: sort_history(name)", source)
        self.assertIn('arrow = " ▼" if descending else " ▲"', source)

    def test_history_is_read_only_and_has_explicit_close(self):
        source = inspect.getsource(order_register_ui.install_order_register)
        history = source.split("    def show_history():", 1)[1].split(
            "    def _order_print_data(", 1
        )[0]
        self.assertIn("ops.order_history(con2,row[\"id\"])", history)
        self.assertIn('text="Закрити",command=dlg.destroy', history)
        self.assertNotIn("con2.commit()", history)
        self.assertNotIn("con2.execute(", history)
        self.assertNotIn("WM_DELETE_WINDOW", history)


if __name__ == "__main__":
    unittest.main()
