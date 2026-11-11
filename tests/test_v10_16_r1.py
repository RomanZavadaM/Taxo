# -*- coding: utf-8 -*-
"""10.16-r1 — центр наказів розділено за відповідальностями."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path
from unittest import mock

import main
import operations_orders_ui
import operations_settings_ui
import order_type_catalog_ui

ROOT = Path(__file__).resolve().parents[1]


class OperationsCenterSeparationR1Tests(unittest.TestCase):
    def test_version_and_start_require_new_operations_modules(self):
        self.assertIn(main.APP_VERSION, ("10.16-r1", "10.16-r2", "10.16-r3", "10.16-r4", "10.16-r5", "10.16-r6", "10.16-r7", "10.16-r8", "10.16-r9"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        start = (ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("operations_orders_ui.py", start)
        self.assertIn("operations_settings_ui.py", start)
        self.assertIn("order_type_catalog_ui.py", start)

    def test_operations_center_is_coordinator_for_settings_and_catalog(self):
        source = inspect.getsource(operations_orders_ui.open_operations_center)
        self.assertIn(
            "install_operations_settings(core, settings_tab, win)",
            source,
        )
        self.assertIn("install_order_type_catalog(", source)
        self.assertIn("install_instruction_tab(app, core, book)", source)
        self.assertIn("install_internship_tab(app, core, book)", source)

    def test_settings_module_keeps_numbering_and_responsible_contract(self):
        source = inspect.getsource(operations_settings_ui.install_operations_settings)
        for marker in (
            "Відповідальний за експлуатацію",
            "Відповідальний за військово-транспортний обов'язок",
            "Наступний № робочого / експлуатаційного наказу",
            "Наступний № кадрового наказу",
            "ops.save_settings",
        ):
            self.assertIn(marker, source)

    def test_catalog_module_keeps_expected_order_entry_points(self):
        source = inspect.getsource(order_type_catalog_ui.install_order_type_catalog)
        for marker in (
            "Закріпити ТЗ за водіями",
            "Організувати ТО / ремонти",
            "Повний каталог типів наказів",
            "Створити наказ за вибраним типом",
            "order_dialog(force_type=order_type)",
        ):
            self.assertIn(marker, source)

    def test_employee_mapping_contract_is_preserved(self):
        rows = [
            {"label": "Іван Коваль", "id": 3},
            {"label": "Олена Лев", "id": 7},
        ]
        with mock.patch.object(
            operations_settings_ui.ops,
            "list_employee_choices",
            return_value=rows,
        ) as choices:
            result_rows, by_label, by_id = operations_settings_ui._employee_maps(
                object()
            )
        self.assertEqual(result_rows, rows)
        self.assertEqual(by_label["Олена Лев"], 7)
        self.assertEqual(by_id[3], "Іван Коваль")
        choices.assert_called_once_with(mock.ANY, active_only=False)

    def test_new_modules_do_not_import_operations_center(self):
        settings_source = (ROOT / "src/taxo/operations_settings_ui.py").read_text("utf-8")
        catalog_source = (ROOT / "src/taxo/order_type_catalog_ui.py").read_text("utf-8")
        self.assertNotIn("import operations_orders_ui", settings_source)
        self.assertNotIn("import operations_orders_ui", catalog_source)


if __name__ == "__main__":
    unittest.main()
