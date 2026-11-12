# -*- coding: utf-8 -*-
"""10.17-r7: typed sorting and selection persistence for employee registers."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import employee_registry_ui
import main
import operations_settings_ui
import personnel_month_schedule_r8
import personnel_v91
import table_sorting

ROOT = Path(__file__).resolve().parents[1]


class EmployeeRegisterSortingR7Tests(unittest.TestCase):
    def test_revision_identity(self):
        self.assertIn(main.APP_VERSION, ("10.17-r7", "10.17-r8", "10.17-r9"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        self.assertIn("Taxo " + main.APP_VERSION, (ROOT / "START.bat").read_text("utf-8"))

    def test_sorting_supports_dates_numbers_durations_and_status(self):
        dates = [("a", "10.11.2026"), ("b", "02.01.2025"), ("c", "")]
        self.assertEqual(
            table_sorting.sorted_row_ids(
                dates, "employment", value_type="date"
            ),
            ["b", "a", "c"],
        )
        numbers = [("a", "1250,50"), ("b", "99.90"), ("c", "")]
        self.assertEqual(
            table_sorting.sorted_row_ids(
                numbers, "tariff", value_type="number"
            ),
            ["b", "a", "c"],
        )
        durations = [("a", "40:00"), ("b", "8:30"), ("c", "36:00")]
        self.assertEqual(
            table_sorting.sorted_row_ids(
                durations, "weeknorm", value_type="duration"
            ),
            ["b", "c", "a"],
        )
        statuses = [("off", "Звільнений"), ("on", "Працює")]
        self.assertEqual(
            table_sorting.sorted_row_ids(
                statuses,
                "status",
                value_type="status",
                status_order=("Працює", "Звільнений"),
            ),
            ["on", "off"],
        )

    def test_primary_personnel_register_has_typed_click_sorting(self):
        source = inspect.getsource(personnel_v91.install)
        self.assertIn(
            'command=lambda name=key:self._sort_personnel_overview(name)',
            source,
        )
        self.assertIn('("employment","Прийнятий",100,"date")', source)
        self.assertIn('("weeknorm","Норма/тиж.",90,"duration")', source)
        self.assertIn('("status","Стан",90,"status")', source)
        self.assertIn("core.sort_treeview(", source)
        self.assertIn("value_type=value_type", source)
        self.assertIn("status_order=status_order", source)

    def test_primary_refresh_keeps_sort_and_selected_employee(self):
        source = inspect.getsource(personnel_v91.install)
        self.assertIn("selected_ids = tuple(tree.selection())", source)
        self.assertIn(
            'selected_sort = getattr(self, "personnel_overview_sort", None)',
            source,
        )
        self.assertIn("self._apply_personnel_overview_sort(selected_sort)", source)
        self.assertIn("tree.selection_set(retained)", source)
        self.assertIn("tree.see(retained[0])", source)
        self.assertIn('iid=str(row["id"])', source)

    def test_legacy_employee_register_uses_same_contract(self):
        build = inspect.getsource(employee_registry_ui.show_employee_registry)
        refresh = inspect.getsource(employee_registry_ui.load_employee_registry)
        self.assertIn('command=lambda name=key: sort_by_header(name)', build)
        self.assertIn('"employment": "date"', build)
        self.assertIn('"tariff": "number"', build)
        self.assertIn('"status": "status"', build)
        self.assertIn('iid=str(row["id"])', refresh)
        self.assertIn("selected_sort", refresh)
        self.assertIn("selection_set(retained)", refresh)

    def test_audited_settings_and_schedule_windows_save_only_explicitly(self):
        settings = inspect.getsource(
            operations_settings_ui.install_operations_settings
        )
        self.assertNotIn("Toplevel(", settings)
        self.assertIn('text="Зберегти"', settings)
        self.assertIn("command=save_settings", settings)

        schedule = inspect.getsource(personnel_month_schedule_r8.install)
        self.assertIn('text="Записати план"', schedule)
        self.assertIn('text="Закрити", command=win.destroy', schedule)
        self.assertNotIn("WM_DELETE_WINDOW", schedule)


if __name__ == "__main__":
    unittest.main()
