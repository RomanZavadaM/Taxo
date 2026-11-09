# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import unittest
from types import SimpleNamespace
from unittest import mock

import function_registry
import military_transport_ui
import personnel_data_center_r6
import personnel_month_schedule_r8
import v1084_features
from runtime_reachability import runtime_routes, activate_widget


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


def invoke_action(widget):
    invoke = getattr(widget, "invoke", None)
    if callable(invoke):
        return invoke()
    widget.event_generate("<Button-1>", x=1, y=1)
    widget.update()


def show_root(root):
    root.deiconify()
    root.update()


class _PlainApp:
    def __init__(self, root):
        self.root = root

    def title(self, *_args):
        return "Taxo test"

    def winfo_children(self):
        return self.root.winfo_children()


class _BasePersonnel(_PlainApp):
    def __init__(self, root):
        super().__init__(root)
        self.personnel_overview_page = ttk.Frame(root)
        self.personnel_overview_page.pack(fill="both", expand=True)
        bar = ttk.Frame(self.personnel_overview_page)
        bar.pack(fill="x")
        ttk.Button(bar, text="Новий працівник").pack(side="right")


class _BaseSchedule(_PlainApp):
    def __init__(self, root):
        super().__init__(root)
        self.personnel_planning_page = ttk.Frame(root)
        self.personnel_planning_page.pack(fill="both", expand=True)


class _BaseVehicles(_PlainApp):
    def __init__(self, root):
        super().__init__(root)
        self.tab_vehicles = ttk.Frame(root)
        self.tab_vehicles.pack(fill="both", expand=True)
        bar = ttk.Frame(self.tab_vehicles)
        bar.pack(fill="x")
        ttk.Button(bar, text="Контроль документів").pack(side="left")


class _BaseNav(_PlainApp):
    def __init__(self, root):
        super().__init__(root)
        nav = tk.Frame(root)
        nav.pack(fill="x")
        self._nav_icons = {}
        self._nav_named_buttons = {}
        anchor = tk.Button(nav, text="Експлуатація")
        anchor.pack(fill="x")
        self._nav_named_buttons["Експлуатація"] = anchor


class _DummyCon:
    def commit(self): pass
    def close(self): pass


class FunctionRegistryR2Tests(unittest.TestCase):
    def test_registry_is_valid_and_contains_known_loss_routes(self):
        self.assertTrue(function_registry.validate_routes())
        ids = set(function_registry.required_route_ids())
        for expected in (
            "personnel.data_center",
            "personnel.simple_month_schedule",
            "maintenance.stoir",
            "vehicles.military",
            "personnel.bulk_replan",
        ):
            self.assertIn(expected, ids)

    def test_simple_month_schedule_is_permanent_in_personnel_ui_source(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        source = (root / "src/taxo/personnel_v91.py").read_text(encoding="utf-8")
        self.assertIn('primary, text="Простий місячний графік…"', source)
        self.assertIn("open_simple_month_schedule_r8", source)

    @runtime_routes("personnel.data_center")
    def test_personnel_data_center_dynamic_entry_is_mapped_and_invokes_callback(self):
        calls = []
        core = SimpleNamespace(tk=tk, ttk=ttk, APP_VERSION="10.12-r2")
        App = personnel_data_center_r6.install(core, _BasePersonnel)
        App.open_personnel_data_center_r6 = lambda self: calls.append("data-center")
        root = tk.Tk()
        root.geometry("900x600")
        app = App(root)
        try:
            show_root(root)
            button = button_by_text(app.personnel_overview_page, "Дані / Дія / документи…")
            self.assertIsNotNone(button)
            activate_widget(button, "personnel.data_center", container=root)
            self.assertEqual(calls, ["data-center"])
        finally:
            root.destroy()

    @runtime_routes("personnel.simple_month_schedule")
    def test_simple_month_schedule_fallback_is_mapped_and_invokes_callback(self):
        calls = []
        core = SimpleNamespace(tk=tk, ttk=ttk, APP_VERSION="10.12-r2")
        App = personnel_month_schedule_r8.install(core, _BaseSchedule)
        App.open_simple_month_schedule_r8 = lambda self: calls.append("simple-month")
        root = tk.Tk()
        root.geometry("900x600")
        app = App(root)
        try:
            show_root(root)
            button = button_by_text(app.personnel_planning_page, "Простий місячний графік…")
            self.assertIsNotNone(button)
            activate_widget(button, "personnel.simple_month_schedule", container=root)
            self.assertEqual(calls, ["simple-month"])
        finally:
            root.destroy()

    @runtime_routes("vehicles.military")
    def test_military_transport_entry_is_mapped_and_invokes_callback(self):
        calls = []
        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            APP_VERSION="10.12-r2",
            db=lambda: _DummyCon(),
        )
        with mock.patch.object(military_transport_ui.mt, "ensure_schema"), \
             mock.patch.object(military_transport_ui.mt, "ensure_next_reporting_action"):
            App = military_transport_ui.install(core, _BaseVehicles)
            App.open_military_transport_dashboard = lambda self: calls.append("military-transport")
            root = tk.Tk()
            root.geometry("900x600")
            app = App(root)
        try:
            show_root(root)
            button = button_by_text(app.tab_vehicles, "Військово-транспортний облік")
            self.assertIsNotNone(button)
            activate_widget(button, "vehicles.military", container=root)
            self.assertEqual(calls, ["military-transport"])
        finally:
            root.destroy()

    @runtime_routes("maintenance.stoir")
    def test_stoir_navigation_is_mapped_and_invokes_callback(self):
        calls = []
        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            APP_VERSION="10.12-r2",
            PALETTE={"sidebar":"#000000","blue_dark":"#111111"},
            nav_photo=lambda parent, *_args: tk.PhotoImage(master=parent, width=1, height=1),
        )
        with mock.patch.object(v1084_features.maintenance, "ensure_schema"):
            App = v1084_features.install(core, _BaseNav)
            App.open_vehicle_maintenance = lambda self: calls.append("stoir")
            root = tk.Tk()
            root.geometry("900x600")
            app = App(root)
        try:
            show_root(root)
            button = app._nav_named_buttons.get("СТОІР")
            self.assertIsNotNone(button)
            activate_widget(button, "maintenance.stoir", container=root)
            self.assertEqual(calls, ["stoir"])
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
