# -*- coding: utf-8 -*-
"""r6 browser integration: workspace isolation and read-only user-facing model."""
from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import template_library_reader
import template_library_service
import template_library_feature
import template_library_ui
import feature_layers


class TemplateLibraryBrowserR6Tests(unittest.TestCase):
    def test_version_and_feature_registered(self):
        self.assertIn("v1018-r6-template-library-browser", feature_layers.feature_layer_ids())
        layer = next(x for x in feature_layers.FEATURE_LAYERS
                     if x.feature_id == "v1018-r6-template-library-browser")
        self.assertTrue(layer.uses_services)
        self.assertEqual(layer.domain, "documents")

    def test_missing_workspace_library_does_not_create_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Work"
            root.mkdir()
            with mock.patch.object(template_library_service, "inspect_library",
                                   wraps=template_library_reader.inspect_library) as reader:
                view = template_library_service.inspect_workspace_library(root, "10.18-r6")
            self.assertEqual(view.status, "NOT_INSTALLED")
            self.assertEqual(view.root, root / "TemplateLibrary")
            self.assertFalse((root / "TemplateLibrary").exists())
            reader.assert_called_once_with(root / "TemplateLibrary", "10.18-r6")

    def test_real_private_catalog_uses_no_embedded_user_or_private_data(self):
        for mod in (template_library_feature, template_library_service,
                    template_library_ui):
            code = inspect.getsource(mod)
            self.assertNotIn("roman_mmg2lw7", code)
            self.assertNotIn("transport-docs-catalog", code)
            self.assertNotIn("C:\\Users\\", code)
            self.assertNotIn("sqlite3", code)
            self.assertNotIn("DocumentVault", code)

    def test_available_model_retains_revisions_and_categories(self):
        from template_library_reader import LibrarySnapshot, TemplateSummary
        snapshot = LibrarySnapshot(
            "AVAILABLE", "Бібліотеку перевірено", Path("Work") / "TemplateLibrary",
            "taxo.templates.ua.transport", "0.1.0", (
                TemplateSummary("order.vehicle_assignment.drivers", "v1", "orders",
                                "Наказ про закріплення", "order", "assignment", "templates/order/a.json"),
                TemplateSummary("program.briefings.road_safety.quarterly", "v1",
                                "training-programs", "Тематика інструктажів",
                                "instruction_program", "briefing", "templates/instruction_program/b.json"),
            ),
        )
        view = template_library_service.view_from_snapshot(snapshot)
        self.assertEqual(view.status, "AVAILABLE")
        self.assertEqual(view.package_version, "0.1.0")
        self.assertEqual(len(view.rows), 2)
        self.assertEqual(view.rows[0].category, "Накази")
        self.assertEqual(view.rows[1].category, "Навчальні програми")
        self.assertIn("перегляду", view.summary)

    def test_incompatible_and_damaged_states_not_treated_as_installed(self):
        from template_library_reader import LibrarySnapshot
        for status in ("INCOMPATIBLE", "DAMAGED", "UNAVAILABLE"):
            model = template_library_service.view_from_snapshot(
                LibrarySnapshot(status, "Synthetic error", Path("Work") / "TemplateLibrary")
            )
            self.assertFalse(model.rows)
            self.assertNotEqual(model.summary, template_library_service.STATUS_LABELS["AVAILABLE"])

    def test_ui_entrypoint_dispatches_to_dedicated_child_window(self):
        services = object()
        fake_parent = object()
        class BaseApp:
            def build_menu(self):
                self.was_called = True
        app = template_library_feature.install(None, BaseApp, services)()
        with mock.patch.object(template_library_feature, "open_template_library",
                               return_value="child") as open_window:
            self.assertEqual(app.show_template_library(), "child")
            open_window.assert_called_once_with(app, services)

    def test_tk_window_has_refresh_close_and_worker_without_db(self):
        code = inspect.getsource(template_library_ui)
        for marker in ('"Закрити"', '"Оновити"', '"WM_DELETE_WINDOW"',
                       "win.after_cancel", "threading.BoundedSemaphore(1)",
                       "state[\"closed\"]", "inspect_workspace_library"):
            self.assertIn(marker, code)

    def test_feature_layer_not_placed_in_main_monolith(self):
        import main
        source = inspect.getsource(main)
        self.assertNotIn("def show_template_library(", source)
        self.assertNotIn("from template_library_service import", source)


if __name__ == "__main__":
    unittest.main()
