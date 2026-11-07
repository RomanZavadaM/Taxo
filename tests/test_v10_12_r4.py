# -*- coding: utf-8 -*-
import sys
import tkinter as tk
from tkinter import ttk
import unittest
from types import SimpleNamespace
from unittest import mock

import function_registry
import main
import military_transport_statement_ui
import v1072_features


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


def show_root(root):
    root.deiconify()
    root.update()


class _BaseNav:
    def __init__(self, root):
        self.root = root
        self._nav_icons = {}
        self._nav_named_buttons = {}
        nav = tk.Frame(root)
        nav.pack(fill="x")
        anchor = tk.Button(nav, text="Маршрути")
        anchor.pack(fill="x")
        self._nav_named_buttons["Маршрути"] = anchor

    def title(self, *_args):
        return "Taxo test"

    def winfo_children(self):
        return self.root.winfo_children()

    def open_employee_military_working_data(self):
        return None


class _BaseMilitaryStatement:
    def __init__(self, root):
        self.root = root
        self._military_transport_window = None

    def title(self, *_args):
        return "Taxo test"

    def open_military_transport_dashboard(self):
        win = tk.Toplevel(self.root)
        self._military_transport_window = win
        bar = ttk.Frame(win)
        bar.pack(fill="x")
        ttk.Button(bar, text="Зафіксувати подання").pack(side="left")
        return win


class ReachabilityR4Tests(unittest.TestCase):
    def test_r4_identity_is_historical_anchor(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION), (10, 12, 4))

    def test_registry_requires_runtime_smoke_for_nested_statement(self):
        routes = {route.function_id: route for route in function_registry.FUNCTION_ROUTES}
        self.assertTrue(routes["operations.center"].runtime_smoke)
        self.assertTrue(routes["maintenance.stoir"].runtime_smoke)
        self.assertTrue(routes["vehicles.military"].runtime_smoke)
        self.assertTrue(routes["vehicles.military.statement"].runtime_smoke)

    def test_operations_navigation_is_mapped_and_invokes(self):
        calls = []
        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            APP_VERSION="10.12-r4",
            PALETTE={"sidebar": "#000000", "blue_dark": "#111111"},
            nav_photo=lambda parent, *_args: tk.PhotoImage(master=parent, width=1, height=1),
        )
        with mock.patch.object(v1072_features.ops, "ensure_schema"), \
             mock.patch.object(v1072_features, "_install_statement_sources"):
            App = v1072_features.install(core, _BaseNav)
            App.open_operations_center = lambda self: calls.append("operations")
            root = tk.Tk()
            root.geometry("900x600")
            app = App(root)
        try:
            show_root(root)
            action = app._nav_named_buttons.get("Експлуатація")
            self.assertIsNotNone(action)
            self.assertTrue(action.winfo_ismapped())
            if callable(getattr(action, "invoke", None)):
                action.invoke()
                self.assertEqual(calls, ["operations"])
            else:
                self.assertTrue(action.bind("<Button-1>"))
        finally:
            root.destroy()

    def test_nested_statement_entry_is_mapped_and_invokes(self):
        calls = []
        core = SimpleNamespace(tk=tk, ttk=ttk, APP_VERSION="10.12-r4")
        with mock.patch.object(military_transport_statement_ui.statement, "ensure_schema"):
            App = military_transport_statement_ui.install(core, _BaseMilitaryStatement)
            App.open_military_transport_statement = lambda self: calls.append("statement")
            root = tk.Tk()
            root.geometry("900x600")
            app = App(root)
        try:
            app.open_military_transport_dashboard()
            show_root(root)
            win = app._military_transport_window
            self.assertIsNotNone(win)
            action = button_by_text(win, "Відомість (додаток 1)")
            self.assertIsNotNone(action)
            self.assertTrue(action.winfo_ismapped())
            action.invoke()
            self.assertEqual(calls, ["statement"])
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
