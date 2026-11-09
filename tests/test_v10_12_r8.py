# -*- coding: utf-8 -*-
import sys
import tkinter as tk
import unittest
from unittest import mock

import function_registry
import main
from runtime_reachability import (runtime_routes, assert_widget_reachable, activate_widget, mark_activation)


class _ShellHarness(main.App):
    def __init__(self):
        tk.Tk.__init__(self)
        self.report_calls = 0
        main.App.build_ui(self)

    def _company_name_value(self):
        return "Test"

    def show_reports_home(self):
        self.report_calls += 1

    def _refresh_brand_header(self):
        pass

    def _refresh_nav_selection(self):
        pass

    def _refresh_header_clock(self):
        pass

    def build_company(self): pass
    def build_drivers(self): pass
    def build_vehicles(self): pass
    def build_work(self): pass
    def build_schedule(self): pass
    def build_route_catalog(self): pass
    def build_attestation(self): pass


class MainNavigationR8Tests(unittest.TestCase):
    def test_r8_identity_is_historical_anchor(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION), (10, 12, 8))

    def test_registry_marks_remaining_main_navigation_for_runtime_smoke(self):
        routes = {route.function_id: route for route in function_registry.FUNCTION_ROUTES}
        for function_id in ("tachograph.main", "reports.home", "settings.main"):
            self.assertTrue(routes[function_id].runtime_smoke, function_id)

    @runtime_routes("tachograph.main", "reports.home", "settings.main")
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
            app.deiconify()
            app.update()

        try:
            routes = {
                "Тахограф": "tachograph.main",
                "Звіти": "reports.home",
                "Налаштування": "settings.main",
            }
            for label, route_id in routes.items():
                action = app._nav_named_buttons.get(label)
                self.assertIsNotNone(action, label)
                assert_widget_reachable(action, route_id, container=app)

            if sys.platform == "darwin":
                for label, route_id in routes.items():
                    self.assertTrue(app._nav_named_buttons[label].bind("<Button-1>"), label)
                    mark_activation(route_id)
            else:
                activate_widget(app._nav_named_buttons["Тахограф"], "tachograph.main", container=app)
                self.assertEqual(app.notebook.select(), str(app.tab_tacho))

                activate_widget(app._nav_named_buttons["Налаштування"], "settings.main", container=app)
                self.assertEqual(app.notebook.select(), str(app.tab_company))

                before = app.report_calls
                activate_widget(app._nav_named_buttons["Звіти"], "reports.home", container=app)
                self.assertEqual(app.report_calls, before + 1)
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
