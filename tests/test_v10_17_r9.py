# -*- coding: utf-8 -*-
"""10.17-r9 driver register sorting and pool-window explicit close."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import driver_registry_ui
import main
from table_sorting import sorted_row_ids

ROOT = Path(__file__).resolve().parents[1]


class DriverRegisterR9Tests(unittest.TestCase):
    def test_revision_identity(self):
        self.assertIn(main.APP_VERSION, ("10.17-r9", "10.17-r10", "10.18-r1", "10.18-r2"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        self.assertIn("Taxo " + main.APP_VERSION, (ROOT / "START.bat").read_text("utf-8"))

    def test_driver_columns_use_correct_types_and_click_sort(self):
        build = inspect.getsource(driver_registry_ui.build_drivers)
        self.assertIn('"id": "number"', build)
        self.assertIn('"birth": "date"', build)
        self.assertIn('"employment": "date"', build)
        self.assertIn('"active": "status"', build)
        self.assertIn('("Так", "Ні")', build)
        self.assertIn('command=lambda name=key: sort_by_header(name)', build)
        self.assertIn('suffix = " ▼" if current[1] else " ▲"', build)

    def test_refresh_preserves_selection_by_driver_id_and_sort(self):
        source = inspect.getsource(driver_registry_ui.load_drivers)
        self.assertIn('selected_ids = tuple(app.driver_tree.selection())', source)
        self.assertIn('selected_sort = getattr(app, "driver_registry_sort", None)', source)
        self.assertIn('iid=str(driver["id"])', source)
        self.assertIn("sort_treeview(", source)
        self.assertIn("selection_set(retained)", source)
        self.assertIn("app.driver_tree.see(retained[0])", source)
        self.assertIn("app.refresh_att_driver_choices()", source)
        self.assertIn("app.refresh_work_driver_choices()", source)

    def test_driver_date_number_status_sort_semantics(self):
        dates = [("later", "31.12.2026"), ("earlier", "02.01.1980")]
        self.assertEqual(
            sorted_row_ids(dates, "birth", value_type="date"),
            ["earlier", "later"],
        )
        self.assertEqual(
            sorted_row_ids(
                [("ten", "10"), ("two", "2")], "id", value_type="number"
            ),
            ["two", "ten"],
        )
        self.assertEqual(
            sorted_row_ids(
                [("no", "Ні"), ("yes", "Так")],
                "active", value_type="status", status_order=("Так", "Ні"),
            ),
            ["yes", "no"],
        )

    def test_pool_close_is_separate_from_deactivation(self):
        source = inspect.getsource(main.App.show_waybill_number_pools)
        self.assertIn('text="Деактивувати / активувати пул"', source)
        self.assertIn('command=self.toggle_waybill_number_pool', source)
        self.assertIn('text="Закрити вікно",command=win.destroy', source)
        self.assertNotIn("WM_DELETE_WINDOW", source)
        self.assertIn("self.pool_win.winfo_exists()", source)


if __name__ == "__main__":
    unittest.main()
