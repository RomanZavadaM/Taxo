# -*- coding: utf-8 -*-
"""10.15-r9 — базовий UI транспорту винесено з main.py зі збереженням App API."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path
from unittest import mock

import main
import vehicle_registry_ui

ROOT = Path(__file__).resolve().parents[1]


class VehicleRegistryUiSeparationR9Tests(unittest.TestCase):
    def test_version_and_start_require_vehicle_registry_ui(self):
        self.assertIn(main.APP_VERSION, ("10.15-r9", "10.15-r10", "10.16-r1", "10.16-r2", "10.16-r3", "10.16-r4", "10.16-r5", "10.16-r6", "10.16-r7", "10.16-r8", "10.16-r9", "10.16-r10", "10.17-r1", "10.17-r2", "10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6", "10.17-r7", "10.17-r8", "10.17-r9", "10.17-r10", "10.18-r1", "10.18-r2", "10.18-r3"))
        self.assertEqual((ROOT / "VERSION.txt").read_text("utf-8"), "Version: " + main.APP_VERSION + "\n")
        start = (ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("vehicle_registry_ui.py", start)

    def test_vehicle_label_contract_is_preserved(self):
        row = {"name": "Автобус 1", "plate": "ВС1234АА", "make_model": "Еталон"}
        self.assertEqual(vehicle_registry_ui.vehicle_label(row), "Автобус 1 — ВС1234АА — Еталон")
        self.assertEqual(vehicle_registry_ui.vehicle_label(None), "")

    def test_main_vehicle_methods_stay_as_compatible_adapters(self):
        source = inspect.getsource(main.App)
        self.assertIn("vehicle_registry_ui.build_vehicles(self)", source)
        self.assertIn("vehicle_registry_ui.load_vehicles(self, db)", source)
        self.assertIn("return vehicle_registry_ui.selected_vehicle(self, db)", source)
        self.assertIn("return vehicle_registry_ui.vehicle_label(r)", source)
        self.assertIn("vehicle_registry_ui.vehicle_form(self, db, fit_window_to_screen, vehicle=vehicle)", source)

    def test_selected_vehicle_adapter_returns_module_result(self):
        app = object.__new__(main.App)
        with mock.patch.object(vehicle_registry_ui, "selected_vehicle", return_value={"id": 7}) as fn:
            result = main.App.selected_vehicle(app)
        self.assertEqual(result, {"id": 7})
        fn.assert_called_once_with(app, main.db)

    def test_registry_module_does_not_import_main(self):
        source = (ROOT / "src/taxo/vehicle_registry_ui.py").read_text("utf-8")
        self.assertNotIn("import main", source)


if __name__ == "__main__":
    unittest.main()
