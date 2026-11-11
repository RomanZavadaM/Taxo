# -*- coding: utf-8 -*-
"""10.16-r9: the driver card editor is independent of the registry table."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path
from unittest import mock

import driver_form_ui
import driver_registry_ui
import main

ROOT = Path(__file__).resolve().parents[1]


class DriverFormSeparationR9Tests(unittest.TestCase):
    def test_version_and_start_guard_include_new_form(self):
        self.assertEqual(main.APP_VERSION, "10.16-r9")
        self.assertEqual((ROOT / "VERSION.txt").read_text("utf-8"),
                         "Version: 10.16-r9\n")
        start = (ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo 10.16-r9", start)
        self.assertIn("driver_registry_ui.py", start)
        self.assertIn("driver_form_ui.py", start)

    def test_registry_exports_the_existing_entry_point(self):
        self.assertIs(driver_registry_ui.driver_form, driver_form_ui.driver_form)
        self.assertIn("from driver_form_ui import driver_form",
                      inspect.getsource(driver_registry_ui))
        self.assertNotIn("def driver_form(",
                         inspect.getsource(driver_registry_ui))

    def test_card_still_owns_validation_and_driver_role_history(self):
        source = inspect.getsource(driver_form_ui.driver_form)
        for marker in (
            "Картка водія", "Активний водій",
            "last_name_en", "first_name_en",
            "parse_display_date(",
            "role_action == \"finish\"",
            "role_action == \"void\"",
            "role_action == \"activate\"",
            "finish_driver_role(",
            "void_legacy_driver_role(",
            "activate_driver_role(",
            "con.commit()",
            "app.load_drivers()",
            "app.load_employee_registry()",
        ):
            self.assertIn(marker, source)
        self.assertNotIn("import main", inspect.getsource(driver_form_ui))

    def test_main_adapter_still_routes_to_the_form_with_dependencies(self):
        app = object.__new__(main.App)
        with mock.patch.object(driver_registry_ui, "driver_form",
                               return_value="driver-card") as edited:
            result = main.App.driver_form(app, {"id": 17})
        self.assertEqual(result, "driver-card")
        self.assertEqual(edited.call_args.args[1], {"id": 17})
        for key in ("db_factory", "fit_window_to_screen", "calendar_button",
                    "finish_driver_role", "void_legacy_driver_role",
                    "activate_driver_role"):
            self.assertIn(key, edited.call_args.kwargs)


if __name__ == "__main__":
    unittest.main()
