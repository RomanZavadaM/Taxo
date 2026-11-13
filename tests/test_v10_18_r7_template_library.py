# -*- coding: utf-8 -*-
"""10.18-r7: visible navigation to the existing read-only library browser."""
import unittest
from unittest import mock

import feature_layers
import template_library_operations_entry as entry


class DummyWindow:
    pass


class DummyApp:
    def __init__(self):
        self.calls = 0

    def show_template_library(self):
        self.calls += 1


class VisibleLibraryEntryR7Tests(unittest.TestCase):
    def test_r7_registered_after_browser(self):
        ids = feature_layers.feature_layer_ids()
        self.assertGreater(ids.index("v1018-r7-visible-library-entry"),
                           ids.index("v1018-r6-template-library-browser"))

    def test_button_opens_existing_library_browser_and_is_not_duplicated(self):
        window = DummyWindow()
        app = DummyApp()
        group = object()
        created = []

        class Button:
            def __init__(self, parent, text, command):
                self.parent, self.text, self.command = parent, text, command
                created.append(self)

            def grid(self, **kwargs):
                self.placement = kwargs

        with mock.patch.object(entry, "_find_orders_group", return_value=group):
            with mock.patch.object(entry.ttk, "Button", Button):
                self.assertTrue(entry.add_operations_library_button(window, app))
                self.assertFalse(entry.add_operations_library_button(window, app))
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0].text, "Бібліотека шаблонів…")
        self.assertEqual((created[0].placement["row"], created[0].placement["column"]),
                         (2, 1))
        created[0].command()
        self.assertEqual(app.calls, 1)

    def test_missing_group_does_not_destroy_or_replace_operations(self):
        window, app = DummyWindow(), DummyApp()
        with mock.patch.object(entry, "_find_orders_group", return_value=None):
            self.assertFalse(entry.add_operations_library_button(window, app))
        self.assertEqual(app.calls, 0)

    def test_existing_operations_entrypoint_called_and_return_value_preserved(self):
        import operations_orders_ui

        window, app = DummyWindow(), DummyApp()
        original = operations_orders_ui.open_operations_center

        with mock.patch.object(operations_orders_ui, "open_operations_center",
                               side_effect=lambda app, core: window) as current:
            with mock.patch.object(entry, "add_operations_library_button") as attach:
                result = entry.install(None, object, None)
                self.assertIs(result, object)
                self.assertIs(operations_orders_ui.open_operations_center(app, "core"), window)
                current.assert_called_once_with(app, "core")
                attach.assert_called_once_with(window, app)
        operations_orders_ui.open_operations_center = original

    def test_entry_has_no_private_paths_or_document_mutations(self):
        import inspect
        source = inspect.getsource(entry)
        for forbidden in ("sqlite3", "write_bytes", "write_text",
                          "C:\\Users\\", "Data/PaperDocuments", "transport-docs-catalog"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
