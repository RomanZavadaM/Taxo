# -*- coding: utf-8 -*-
"""10.16-r2 — реєстр наказів має окремий UI-контролер."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import main
import operations_orders_ui
import order_register_ui

ROOT = Path(__file__).resolve().parents[1]


class OrderRegisterSeparationR2Tests(unittest.TestCase):
    def test_version_and_start_require_order_register_module(self):
        self.assertIn(main.APP_VERSION, ("10.16-r2", "10.16-r3"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        start = (ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("order_register_ui.py", start)

    def test_operations_center_is_a_module_coordinator(self):
        source = inspect.getsource(operations_orders_ui.open_operations_center)
        self.assertIn("install_operations_settings(", source)
        self.assertIn("install_order_register(", source)
        self.assertIn("install_order_type_catalog(", source)
        self.assertIn("install_instruction_tab(", source)
        self.assertIn("install_internship_tab(", source)
        self.assertNotIn("def approve_selected(", source)
        self.assertNotIn("def show_history(", source)

    def test_register_module_keeps_owner_visible_order_actions(self):
        source = inspect.getsource(order_register_ui.install_order_register)
        for marker in (
            "Новий наказ…",
            "Переглянути / друк",
            "Нумерація наказів…",
            "Ввести в дію в Taxo",
            "Історія…",
            "Скасувати наказ",
            "Видалити наказ",
            "Підпис на папері: так / ні",
            "group_filter_var",
        ):
            self.assertIn(marker, source)

    def test_register_exposes_only_required_cross_module_actions(self):
        fields = tuple(order_register_ui.OrderRegisterController.__dataclass_fields__)
        self.assertEqual(
            fields,
            (
                "order_dialog",
                "preview_order",
                "preview_catalog_order",
                "refresh_orders",
            ),
        )

    def test_register_module_does_not_import_operations_center(self):
        source = (ROOT / "src/taxo/order_register_ui.py").read_text("utf-8")
        self.assertNotIn("import operations_orders_ui", source)


if __name__ == "__main__":
    unittest.main()
