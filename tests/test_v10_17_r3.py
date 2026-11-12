# -*- coding: utf-8 -*-
"""10.17-r3: standalone operational windows expose explicit close controls."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import main
import vehicle_maintenance_ui
import military_transport_ui

ROOT = Path(__file__).resolve().parents[1]


class OperationWindowNavigationR3Tests(unittest.TestCase):
    def test_revision_and_start_identity(self):
        self.assertIn(main.APP_VERSION, ("10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        self.assertIn("Taxo " + main.APP_VERSION, (ROOT / "START.bat").read_text("utf-8"))

    def test_stoir_center_close_is_non_destructive(self):
        source = inspect.getsource(vehicle_maintenance_ui.open_maintenance_center)
        self.assertIn('text="Закрити", command=win.destroy', source)
        self.assertIn("app._maintenance_center_window = win", source)
        self.assertIn("existing.lift()", source)
        self.assertNotIn('command=app.destroy', source)

    def test_military_transport_close_is_non_destructive(self):
        source = inspect.getsource(military_transport_ui)
        self.assertIn('header, text="Військово-транспортний облік ТЗ"', source)
        self.assertIn('header, text="Закрити", command=win.destroy', source)
        self.assertIn('self._military_transport_window = win', source)
        self.assertNotIn('command=self.destroy', source)

    def test_no_storage_or_data_mutation_added_to_close_callbacks(self):
        for module in (vehicle_maintenance_ui, military_transport_ui):
            source = inspect.getsource(module)
            self.assertIn('text="Закрити", command=win.destroy', source)


if __name__ == "__main__":
    unittest.main()
