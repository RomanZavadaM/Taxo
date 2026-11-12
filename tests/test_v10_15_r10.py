# -*- coding: utf-8 -*-
"""10.15-r10 — реєстр працівників відокремлено від main.py зі збереженням App API."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path
from unittest import mock

import employee_registry_ui
import main

ROOT = Path(__file__).resolve().parents[1]


class EmployeeRegistryUiSeparationR10Tests(unittest.TestCase):
    def test_version_and_start_require_employee_registry_ui(self):
        self.assertIn(main.APP_VERSION, ("10.15-r10", "10.16-r1", "10.16-r2", "10.16-r3", "10.16-r4", "10.16-r5", "10.16-r6", "10.16-r7", "10.16-r8", "10.16-r9", "10.16-r10", "10.17-r1", "10.17-r2", "10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6", "10.17-r7", "10.17-r8"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        start = (ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("employee_registry_ui.py", start)

    def test_employee_full_name_contract_is_preserved(self):
        row = {
            "last_name": "Коваль",
            "first_name": "Іван",
            "middle_name": "Петрович",
        }
        self.assertEqual(
            employee_registry_ui.employee_full_name(row),
            "Коваль Іван Петрович",
        )

    def test_main_employee_methods_stay_as_compatible_adapters(self):
        source = inspect.getsource(main.App)
        self.assertIn(
            "return employee_registry_ui.employee_full_name(row)",
            source,
        )
        self.assertIn(
            "return employee_registry_ui.show_employee_registry(",
            source,
        )
        self.assertIn(
            "return employee_registry_ui.selected_employee(self, db)",
            source,
        )
        self.assertIn(
            "return employee_registry_ui.employee_form(",
            source,
        )

    def test_selected_employee_adapter_returns_module_result(self):
        app = object.__new__(main.App)
        with mock.patch.object(
            employee_registry_ui,
            "selected_employee",
            return_value={"id": 17},
        ) as fn:
            result = main.App.selected_employee(app)
        self.assertEqual(result, {"id": 17})
        fn.assert_called_once_with(app, main.db)

    def test_employee_form_adapter_keeps_role_helpers_explicit(self):
        app = object.__new__(main.App)
        with mock.patch.object(
            employee_registry_ui,
            "employee_form",
            return_value="ok",
        ) as fn:
            result = main.App.employee_form(app, {"id": 3})
        self.assertEqual(result, "ok")
        kwargs = fn.call_args.kwargs
        self.assertIs(kwargs["db_factory"], main.db)
        self.assertIs(kwargs["finish_driver_role"], main.finish_driver_role)
        self.assertIs(kwargs["void_legacy_driver_role"], main.void_legacy_driver_role)
        self.assertIs(kwargs["activate_driver_role"], main.activate_driver_role)

    def test_registry_module_does_not_import_main(self):
        source = (ROOT / "src/taxo/employee_registry_ui.py").read_text("utf-8")
        self.assertNotIn("import main", source)


if __name__ == "__main__":
    unittest.main()
