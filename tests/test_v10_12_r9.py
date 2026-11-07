# -*- coding: utf-8 -*-
import tkinter as tk
import unittest
from unittest import mock

import function_registry
import main


def walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from walk(child)


def button_by_text(root, text):
    for widget in walk(root):
        try:
            if widget.winfo_class() in ("TButton", "Button") and str(widget.cget("text")) == text:
                return widget
        except Exception:
            pass
    return None


class _DriverReportHarness(main.App):
    def __init__(self):
        tk.Tk.__init__(self)
        self.schedule_date_var = tk.StringVar(value="07.11.2026")

    def _decorate_secondary_window(self, *_args, **_kwargs):
        pass

    def refresh_monthly_shift_schedule(self):
        return None


class DriverReportSelectionReachabilityR9Tests(unittest.TestCase):
    def test_identity_is_10_12_r9(self):
        self.assertEqual(main.APP_VERSION, "10.12-r9")

    def test_registry_requires_driver_report_selection_runtime_smoke(self):
        routes = {route.function_id: route for route in function_registry.FUNCTION_ROUTES}
        self.assertIn("drivers.report_selection", routes)
        self.assertTrue(routes["drivers.report_selection"].runtime_smoke)

    def test_driver_report_selection_is_visible_and_opens_selector(self):
        drivers = {
            "drivers": [
                {"id": 11, "name": "Водій Один"},
                {"id": 22, "name": "Водій Два"},
            ]
        }
        with mock.patch.object(main, "collect_monthly_shift_schedule", return_value=drivers):
            app = _DriverReportHarness()
            app.geometry("1000x700")
            app.deiconify()
            try:
                app.show_monthly_shift_schedule()
                app.update()

                button = button_by_text(app.monthly_shift_win, "Водії для звіту…")
                self.assertIsNotNone(button)
                self.assertTrue(button.winfo_ismapped())

                button.invoke()
                app.update()

                selectors = [
                    widget for widget in walk(app)
                    if isinstance(widget, tk.Toplevel)
                    and widget.winfo_exists()
                    and widget.title() == "Вибір водіїв для звіту"
                ]
                self.assertEqual(len(selectors), 1)
                popup = selectors[0]
                self.assertTrue(popup.winfo_ismapped())

                listboxes = [widget for widget in walk(popup) if isinstance(widget, tk.Listbox)]
                self.assertEqual(len(listboxes), 1)
                self.assertEqual(listboxes[0].size(), 2)

                apply_button = button_by_text(popup, "Застосувати")
                self.assertIsNotNone(apply_button)
                self.assertTrue(apply_button.winfo_ismapped())
            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main()
