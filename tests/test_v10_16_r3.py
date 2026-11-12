# -*- coding: utf-8 -*-
"""10.16-r3 — реєстр і картка водія мають окремий UI-модуль."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path
from unittest import mock

import driver_registry_ui
import main

ROOT = Path(__file__).resolve().parents[1]


class DriverRegistrySeparationR3Tests(unittest.TestCase):
    def test_version_and_start_require_driver_registry_module(self):
        self.assertIn(main.APP_VERSION, ("10.16-r3", "10.16-r4", "10.16-r5", "10.16-r6", "10.16-r7", "10.16-r8", "10.16-r9", "10.16-r10", "10.17-r1", "10.17-r2", "10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6", "10.17-r7", "10.17-r8"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        start = (ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("driver_registry_ui.py", start)

    def test_main_driver_registry_methods_are_compatible_adapters(self):
        source = inspect.getsource(main.App)
        for marker in (
            "driver_registry_ui.build_drivers(self)",
            "driver_registry_ui.driver_form(",
            "driver_registry_ui.delete_driver(",
            "driver_registry_ui.selected_driver(self, db)",
            "driver_registry_ui.driver_by_id(driver_id, db)",
            "driver_registry_ui.driver_full_name(driver)",
            "driver_registry_ui.load_drivers(",
        ):
            self.assertIn(marker, source)

    def test_driver_role_history_helpers_remain_explicit_dependencies(self):
        app = object.__new__(main.App)
        with mock.patch.object(
            driver_registry_ui,
            "driver_form",
            return_value="ok",
        ) as fn:
            result = main.App.driver_form(app, {"id": 5})
        self.assertEqual(result, "ok")
        kwargs = fn.call_args.kwargs
        self.assertIs(kwargs["db_factory"], main.db)
        self.assertIs(kwargs["finish_driver_role"], main.finish_driver_role)
        self.assertIs(
            kwargs["void_legacy_driver_role"],
            main.void_legacy_driver_role,
        )
        self.assertIs(
            kwargs["activate_driver_role"],
            main.activate_driver_role,
        )

    def test_worktime_and_attestation_driver_selection_stay_outside_registry(self):
        module = (ROOT / "src/taxo/driver_registry_ui.py").read_text("utf-8")
        app_source = inspect.getsource(main.App)
        self.assertNotIn("def refresh_work_driver_choices(", module)
        self.assertNotIn("def refresh_att_driver_choices(", module)
        self.assertIn("def refresh_work_driver_choices(", app_source)
        self.assertIn("def refresh_att_driver_choices(", app_source)

    def test_driver_full_name_contract_is_preserved(self):
        row = {
            "last_name": "Коваль",
            "first_name": "Іван",
            "middle_name": "Петрович",
        }
        self.assertEqual(
            driver_registry_ui.driver_full_name(row),
            "Коваль Іван Петрович",
        )
        self.assertEqual(driver_registry_ui.driver_full_name(None), "")

    def test_registry_module_does_not_import_main(self):
        source = (ROOT / "src/taxo/driver_registry_ui.py").read_text("utf-8")
        self.assertNotIn("import main", source)


if __name__ == "__main__":
    unittest.main()
