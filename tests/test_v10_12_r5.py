# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import unittest
from types import SimpleNamespace
from unittest import mock

import function_registry
import main
import personnel_v91
import v1064_features as waybill_layout


def walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from walk(child)


def widget_by_prefix(root, prefix, classes):
    for widget in walk(root):
        try:
            if widget.winfo_class() in classes and str(widget.cget("text")).startswith(prefix):
                return widget
        except Exception:
            pass
    return None


class _PlannerHost(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

    def title(self, *_args):
        return "Taxo test"


class _Messages:
    @staticmethod
    def showerror(*_args, **_kwargs):
        return None

    @staticmethod
    def showinfo(*_args, **_kwargs):
        return None

    @staticmethod
    def askyesno(*_args, **_kwargs):
        return False


class FragileLayoutR5Tests(unittest.TestCase):
    def test_identity_is_10_12_r5(self):
        self.assertEqual(main.APP_VERSION, "10.12-r5")

    def test_registry_requires_runtime_smoke_for_historically_fragile_controls(self):
        routes = {route.function_id: route for route in function_registry.FUNCTION_ROUTES}
        self.assertTrue(routes["personnel.bulk_replan"].runtime_smoke)
        self.assertTrue(routes["waybills.actions"].runtime_smoke)

    def test_bulk_replan_checkbox_is_visible_at_minimum_window_size(self):
        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            employee_day_time=lambda *_args, **_kwargs: {},
            collect_monthly_work_balance=lambda *_args, **_kwargs: {},
            APP_VERSION="10.12-r5",
            PALETTE={"muted": "#666666"},
            fit_window_to_screen=lambda win, *_args: win.geometry("780x560"),
            calendar_button=lambda parent, _var: ttk.Button(parent, text="Дата"),
            messagebox=_Messages,
        )

        with mock.patch.object(personnel_v91, "ensure_work_regime_schema", lambda _core: None):
            App = personnel_v91.install(core, _PlannerHost)
            App._active_employee_map = lambda self: {}
            root = tk.Tk()
            root.geometry("900x650")
            app = App(root)
            app.pack(fill="both", expand=True)
        try:
            app.show_general_personnel_shift_planner()
            root.update()
            win = app._personnel_shift_win
            self.assertEqual(win.winfo_width(), 780)
            self.assertEqual(win.winfo_height(), 560)
            control = widget_by_prefix(
                win,
                "Перепланувати: замінити існуючий ПЛАН",
                ("TCheckbutton", "Checkbutton"),
            )
            self.assertIsNotNone(control)
            self.assertTrue(control.winfo_ismapped())
            self.assertGreater(control.winfo_width(), 1)
            self.assertGreater(control.winfo_height(), 1)
        finally:
            root.destroy()

    def test_all_nine_waybill_actions_remain_visible_and_invokable_when_wrapped(self):
        calls = []
        root = tk.Tk()
        root.geometry("520x300")
        frame = ttk.Frame(root)
        frame.pack(fill="x")
        buttons = []
        for label in waybill_layout.WAYBILL_ACTION_LABELS:
            button = ttk.Button(
                frame,
                text=label,
                command=lambda value=label: calls.append(value),
            )
            button.pack(side="left")
            buttons.append(button)

        try:
            root.update_idletasks()
            rows = waybill_layout._grid_waybill_actions(
                frame, buttons, available_width=480
            )
            root.update()
            self.assertGreaterEqual(rows, 2)
            self.assertEqual(len(buttons), 9)
            for button in buttons:
                self.assertTrue(button.winfo_ismapped(), button.cget("text"))
                self.assertTrue(button.grid_info())
                button.invoke()
            self.assertEqual(calls, list(waybill_layout.WAYBILL_ACTION_LABELS))
            used_rows = {int(button.grid_info()["row"]) for button in buttons}
            self.assertGreaterEqual(len(used_rows), 2)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
