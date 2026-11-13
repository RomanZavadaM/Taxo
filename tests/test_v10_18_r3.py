# -*- coding: utf-8 -*-
"""10.18-r3: STOIR working-table sorting and stable selection."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import main
import vehicle_maintenance_ui

ROOT = Path(__file__).resolve().parents[1]


class StoirTableSortingR3Tests(unittest.TestCase):
    def test_candidate_identity(self):
        self.assertIn(main.APP_VERSION, ("10.18-r3", "10.18-r4", "10.18-r5", "10.18-r6", "10.18-r7"))
        self.assertEqual((ROOT / "VERSION.txt").read_text("utf-8"), "Version: " + main.APP_VERSION + "\n")
        self.assertIn("Taxo " + main.APP_VERSION, (ROOT / "START.bat").read_text("utf-8"))

    def test_four_working_tables_use_explicit_types(self):
        source = inspect.getsource(vehicle_maintenance_ui.open_maintenance_center)
        for marker in (
            '("at", "Дата / час", "datetime", None)',
            '("km", "Одометр, км", "number", None)',
            '("date", "Дата", "date", None)',
            '("id", "№", "number", None)',
            '("reported", "Зареєстровано", "datetime", None)',
            '("priority", "Пріоритет", "status"',
            '("status", "Статус", "status"',
            '("odometer", "Одометр", "number", None)',
            '("avg", "Сер. км/день", "number", None)',
            '("requests", "Відкриті заявки", "number", None)',
        ):
            self.assertIn(marker, source)

    def test_refresh_uses_stable_ids_for_all_tables(self):
        source = inspect.getsource(vehicle_maintenance_ui.open_maintenance_center)
        self.assertIn("SELECT id,reading_at,reading_km", source)
        self.assertGreaterEqual(source.count('iid=str(row["id"])'), 3)
        self.assertIn('iid=str(vehicle["id"])', source)
        for marker in (
            "apply_mileage_sort()",
            "apply_service_sort()",
            "apply_request_sort()",
            "apply_report_sort()",
            'restore_tree_selection(mileage_tree, selected_rows["mileage"])',
            'restore_tree_selection(service_tree, selected_rows["service"])',
            'restore_tree_selection(request_tree, selected_rows["requests"])',
            'restore_tree_selection(report_tree, selected_rows["fleet"])',
        ):
            self.assertIn(marker, source)

    def test_request_actions_still_resolve_real_request_id(self):
        source = inspect.getsource(vehicle_maintenance_ui.open_maintenance_center)
        self.assertIn('values = request_tree.item(selected[0], "values")', source)
        self.assertIn('"SELECT * FROM vehicle_repair_requests WHERE id=?"', source)
        self.assertIn("(int(values[0]),)", source)

    def test_r3_does_not_add_delete_or_db_write_to_sort_configuration(self):
        source = inspect.getsource(vehicle_maintenance_ui.open_maintenance_center)
        sort_block = source.split("    sort_state = {}", 1)[1].split("    inspection_box =", 1)[0]
        self.assertNotIn("core.db()", sort_block)
        self.assertNotIn(".execute(", sort_block)
        self.assertNotIn(".commit()", sort_block)


if __name__ == "__main__":
    unittest.main()
