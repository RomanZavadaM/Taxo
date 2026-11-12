# -*- coding: utf-8 -*-
"""10.16-r4 — робочі вікна документів ТЗ відокремлені від правил і даних."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path
from unittest import mock

import main
import vehicle_documents
import vehicle_documents_ui
import vehicle_registry_ui

ROOT = Path(__file__).resolve().parents[1]


class VehicleDocumentsUiSeparationR4Tests(unittest.TestCase):
    def test_version_and_start_require_vehicle_documents_ui_module(self):
        self.assertIn(main.APP_VERSION, ("10.16-r4", "10.16-r5", "10.16-r6", "10.16-r7", "10.16-r8", "10.16-r9", "10.16-r10", "10.17-r1", "10.17-r2", "10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6", "10.17-r7"))
        self.assertIn(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            ("Version: 10.16-r4\n", "Version: 10.16-r5\n", "Version: 10.16-r6\n", "Version: 10.16-r7\n", "Version: 10.16-r8\n", "Version: 10.16-r9\n", "Version: 10.16-r10\n", "Version: 10.17-r1\n", "Version: 10.17-r2\n", "Version: 10.17-r3\n", "Version: 10.17-r4\n", "Version: 10.17-r5\n", "Version: 10.17-r6\n"),
        )
        start = (ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo %s" % main.APP_VERSION, start)
        self.assertIn("vehicle_documents.py", start)
        self.assertIn("vehicle_documents_ui.py", start)

    def test_domain_module_no_longer_contains_vehicle_document_windows(self):
        source = inspect.getsource(vehicle_documents)
        self.assertNotIn("class VehicleDocumentsWindow", source)
        self.assertNotIn("tk.Toplevel", source)
        self.assertIn("def ensure_vehicle_documents_schema(", source)
        self.assertIn("def vehicle_document_summary(", source)
        self.assertIn("def copy_document_file(", source)

    def test_ui_module_owns_vehicle_document_windows(self):
        source = inspect.getsource(vehicle_documents_ui)
        self.assertIn("class VehicleDocumentsWindow", source)
        self.assertIn("def open_vehicle_documents(", source)
        self.assertIn("def open_vehicle_document_control(", source)
        self.assertIn("Контроль документів транспортних засобів", source)
        self.assertNotIn("import main", source)

    def test_vehicle_registry_uses_ui_module_explicitly(self):
        source = inspect.getsource(vehicle_registry_ui)
        self.assertIn("from vehicle_documents_ui import (", source)
        self.assertIn("open_vehicle_documents", source)
        self.assertIn("open_vehicle_document_control", source)

    def test_legacy_domain_entry_points_delegate_without_changing_arguments(self):
        parent = object()
        db_factory = object()
        data_root = object()
        vehicle = {"id": 17}
        on_change = object()
        with mock.patch.object(
            vehicle_documents_ui,
            "open_vehicle_documents",
            return_value="vehicle-window",
        ) as open_window:
            result = vehicle_documents.open_vehicle_documents(
                parent,
                db_factory,
                data_root,
                vehicle,
                on_change=on_change,
            )
        self.assertEqual(result, "vehicle-window")
        open_window.assert_called_once_with(
            parent,
            db_factory,
            data_root,
            vehicle,
            on_change=on_change,
        )

        on_open_vehicle = object()
        with mock.patch.object(
            vehicle_documents_ui,
            "open_vehicle_document_control",
            return_value="control-window",
        ) as open_control:
            result = vehicle_documents.open_vehicle_document_control(
                parent,
                db_factory,
                data_root,
                on_open_vehicle=on_open_vehicle,
            )
        self.assertEqual(result, "control-window")
        open_control.assert_called_once_with(
            parent,
            db_factory,
            data_root,
            on_open_vehicle=on_open_vehicle,
        )


if __name__ == "__main__":
    unittest.main()
