# -*- coding: utf-8 -*-
import sys
import tkinter as tk
import unittest
from unittest import mock

import function_registry
import main


class _ShellHarness(main.App):
    def __init__(self):
        tk.Tk.__init__(self)
        self.report_calls = 0
        main.App.build_ui(self)

    def _company_name_value(self):
        return "Test"

    def show_reports_home(self):
        self.report_calls += 1

    def build_company(self): pass
    def build_drivers(self): pass
    def build_vehicles(self): pass
    def build_work(self): pass
    def build_schedule(self): pass
    def build_route_catalog(self): pass
    def build_attestation(self): pass


def click_nav(root, widget):
    if callable(getattr(widget, "invoke", None)):
        widget.invoke()
    else:
        widget.event_generate("<Button-1>")
    root.update()


class MainNavigationR7Tests(unittest.TestCase):
    def test_identity_is_10_12_r7(self):
        self.assertEqual(main.APP_VERSION, "10.12-r7")

    def test_registry_marks_remaining_main_navigation_for_runtime_smoke(self):
        routes = {route.function_id: route for route in function_registry.FUNCTION_ROUTES}
        for function_id in ("tachograph.main", "reports.home", "settings.main"):
            self.assertTrue(routes[function_id].runtime_smoke, function_id)

    def test_tachograph_reports_and_settings_are_visible_and_route_correctly(self):
        def photo(parent, *_args, **_kwargs):
            return tk.PhotoImage(master=parent, width=1, height=1)

        with mock.patch.object(main, "apply_theme", lambda *_args, **_kwargs: None), \
             mock.patch.object(main, "install_runtime_icon", lambda *_args, **_kwargs: None), \
             mock.patch.object(main, "brand_photo", photo), \
             mock.patch.object(main, "nav_photo", photo), \
             mock.patch.object(main, "draw_brand_header", lambda *_args, **_kwargs: None), \
             mock.patch.object(main, "get_setting", lambda _key, default="": default), \
             mock.patch.object(main, "set_setting", lambda *_args, **_kwargs: None), \
             mock.patch.object(main, "TachographModule", None):
            app = _ShellHarness()
            app.geometry("1000x700")
            app.update()

        try:
            for label in ("Тахограф", "Звіти", "Налаштування"):
                action = app._nav_named_buttons.get(label)
                self.assertIsNotNone(action, label)
                self.assertTrue(action.winfo_ismapped(), label)

            click_nav(app, app._nav_named_buttons["Тахограф"])
            self.assertEqual(app.notebook.select(), str(app.tab_tacho))

            click_nav(app, app._nav_named_buttons["Налаштування"])
            self.assertEqual(app.notebook.select(), str(app.tab_company))

            before = app.report_calls
            click_nav(app, app._nav_named_buttons["Звіти"])
            self.assertEqual(app.report_calls, before + 1)
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
