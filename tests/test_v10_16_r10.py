# -*- coding: utf-8 -*-
"""10.16-r10: the vehicle card editor is independent of the registry table."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path
from unittest import mock

import main
import vehicle_form_ui
import vehicle_registry_ui

ROOT = Path(__file__).resolve().parents[1]


class VehicleFormSeparationR10Tests(unittest.TestCase):
    def test_version_and_start_guard_include_new_form(self):
        self.assertIn(main.APP_VERSION, ("10.16-r10", "10.17-r1", "10.17-r2", "10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6", "10.17-r7"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        start = (ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("vehicle_registry_ui.py", start)
        self.assertIn("vehicle_form_ui.py", start)

    def test_registry_exports_the_existing_entry_point(self):
        self.assertIs(vehicle_registry_ui.vehicle_form, vehicle_form_ui.vehicle_form)
        source = inspect.getsource(vehicle_registry_ui)
        self.assertIn("from vehicle_form_ui import vehicle_form", source)
        self.assertNotIn("def vehicle_form(", source)

    def test_card_keeps_validation_and_vehicle_storage_contract(self):
        source = inspect.getsource(vehicle_form_ui.vehicle_form)
        for marker in (
            "Автомобіль",
            "Вкажіть назву автомобіля.",
            "Рік має бути числом.",
            "temporary_registration_required",
            "UPDATE vehicles SET",
            "INSERT INTO vehicles",
            "con.commit()",
            "app.load_vehicles()",
        ):
            self.assertIn(marker, source)
        module_source = inspect.getsource(vehicle_form_ui)
        self.assertNotIn("import main", module_source)
        self.assertNotIn("vehicle_documents", module_source)

    def test_main_adapter_still_routes_to_registry_entry_point(self):
        app = object.__new__(main.App)
        with mock.patch.object(
            vehicle_registry_ui,
            "vehicle_form",
            return_value="vehicle-card",
        ) as edited:
            result = main.App.vehicle_form(app, {"id": 11})
        self.assertIsNone(result)
        edited.assert_called_once_with(
            app,
            main.db,
            main.fit_window_to_screen,
            vehicle={"id": 11},
        )


if __name__ == "__main__":
    unittest.main()
