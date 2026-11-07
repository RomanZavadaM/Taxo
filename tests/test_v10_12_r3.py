# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import unittest
from pathlib import Path
from types import SimpleNamespace

import main
import personnel_data_center_r6


ROOT = Path(__file__).resolve().parents[1]


def walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from walk(child)


def buttons(root, text):
    result = []
    for widget in walk(root):
        try:
            if widget.winfo_class() in ("TButton", "Button") and str(widget.cget("text")) == text:
                result.append(widget)
        except Exception:
            pass
    return result


def show_root(root):
    root.deiconify()
    root.update()


class _PlainApp:
    def __init__(self, root):
        self.root = root

    def title(self, *_args):
        return "Taxo test"


class _NoAnchorApp(_PlainApp):
    def __init__(self, root):
        super().__init__(root)
        self.personnel_overview_page = ttk.Frame(root)
        self.personnel_overview_page.pack(fill="both", expand=True)
        bar = ttk.Frame(self.personnel_overview_page)
        bar.pack(fill="x")
        self.legacy = ttk.Button(bar, text="Реєстр документів")
        self.legacy.pack(side="right")


class _PermanentRouteApp(_PlainApp):
    def __init__(self, root):
        super().__init__(root)
        self.personnel_overview_page = ttk.Frame(root)
        self.personnel_overview_page.pack(fill="both", expand=True)
        bar = ttk.Frame(self.personnel_overview_page)
        bar.pack(fill="x")
        self.route = ttk.Button(bar, text="Дані / Дія / документи…")
        self.route.pack(side="right")
        self.legacy = ttk.Button(bar, text="Реєстр документів")
        self.legacy.pack(side="right")


class _FallbackApp(_PlainApp):
    def __init__(self, root):
        super().__init__(root)
        self.personnel_overview_page = ttk.Frame(root)
        self.personnel_overview_page.pack(fill="both", expand=True)
        bar = ttk.Frame(self.personnel_overview_page)
        bar.pack(fill="x")
        self.anchor = ttk.Button(bar, text="Новий працівник")
        self.anchor.pack(side="right")
        self.legacy = ttk.Button(bar, text="Реєстр документів")
        self.legacy.pack(side="right")


class PersonnelDataCenterRouteR3Tests(unittest.TestCase):
    def test_r3_identity_is_historical_anchor(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        current = (ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()
        self.assertTrue(current.startswith("Version: "))
        self.assertGreaterEqual(key(main.APP_VERSION), (10, 12, 3))
        self.assertEqual(key(current[len("Version: "):]), key(main.APP_VERSION))

    def test_personnel_ui_owns_permanent_data_center_action(self):
        source = (ROOT / "src/taxo/personnel_v91.py").read_text(encoding="utf-8")
        self.assertIn('hero, text="Дані / Дія / документи…"', source)
        self.assertIn("open_personnel_data_center_r6", source)

    def test_missing_replacement_anchor_keeps_legacy_route_visible(self):
        core = SimpleNamespace(tk=tk, ttk=ttk, APP_VERSION="10.12-r3")
        App = personnel_data_center_r6.install(core, _NoAnchorApp)
        root = tk.Tk()
        root.geometry("900x600")
        app = App(root)
        try:
            show_root(root)
            self.assertTrue(app.legacy.winfo_ismapped())
            self.assertEqual(buttons(app.personnel_overview_page, "Дані / Дія / документи…"), [])
            self.assertFalse(getattr(app, "_personnel_data_center_r6_installed", False))
        finally:
            root.destroy()

    def test_permanent_route_is_reused_before_legacy_entries_are_hidden(self):
        core = SimpleNamespace(tk=tk, ttk=ttk, APP_VERSION="10.12-r3")
        App = personnel_data_center_r6.install(core, _PermanentRouteApp)
        root = tk.Tk()
        root.geometry("900x600")
        app = App(root)
        try:
            show_root(root)
            routes = buttons(app.personnel_overview_page, "Дані / Дія / документи…")
            self.assertEqual(len(routes), 1)
            self.assertTrue(routes[0].winfo_ismapped())
            self.assertFalse(app.legacy.winfo_ismapped())
            self.assertIs(app._personnel_data_center_r6_button, routes[0])
            self.assertTrue(app._personnel_data_center_r6_installed)
        finally:
            root.destroy()

    def test_legacy_fallback_creates_replacement_then_hides_old_entry(self):
        calls = []
        core = SimpleNamespace(tk=tk, ttk=ttk, APP_VERSION="10.12-r3")
        App = personnel_data_center_r6.install(core, _FallbackApp)
        App.open_personnel_data_center_r6 = lambda self: calls.append("data-center")
        root = tk.Tk()
        root.geometry("900x600")
        app = App(root)
        try:
            show_root(root)
            routes = buttons(app.personnel_overview_page, "Дані / Дія / документи…")
            self.assertEqual(len(routes), 1)
            self.assertTrue(routes[0].winfo_ismapped())
            self.assertFalse(app.legacy.winfo_ismapped())
            routes[0].invoke()
            self.assertEqual(calls, ["data-center"])
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
