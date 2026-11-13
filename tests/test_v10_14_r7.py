# -*- coding: utf-8 -*-
"""10.14-r7 — strict meta-gate for live UI reachability."""
import tkinter as tk
from tkinter import ttk
import unittest
from types import SimpleNamespace
from unittest import mock

import function_registry
import main
import safety_instructions_ui
from runtime_reachability import (
    runtime_routes,
    assert_widget_reachable,
    activate_widget,
    validate_runtime_coverage,
)


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


class _DummyCon:
    def close(self):
        pass


class StrictReachabilityGateR7Tests(unittest.TestCase):
    def test_identity_is_r7(self):
        self.assertIn(main.APP_VERSION, ("10.14-r7", "10.14-r8", "10.14-r9", "10.14-r10", "10.15-r1", "10.15-r2", "10.15-r3", "10.15-r4", "10.15-r5", "10.15-r7", "10.15-r8", "10.15-r9", "10.15-r10", "10.16-r1", "10.16-r2", "10.16-r3", "10.16-r4", "10.16-r5", "10.16-r6", "10.16-r7", "10.16-r8", "10.16-r9", "10.16-r10", "10.17-r1", "10.17-r2", "10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6", "10.17-r7", "10.17-r8", "10.17-r9", "10.17-r10", "10.18-r1", "10.18-r2", "10.18-r3", "10.18-r4", "10.18-r5", "10.18-r6", "10.18-r7"))

    def test_every_runtime_smoke_route_has_a_registered_strict_live_test(self):
        self.assertTrue(validate_runtime_coverage(function_registry.FUNCTION_ROUTES))
        runtime_ids = {
            route.function_id for route in function_registry.FUNCTION_ROUTES
            if route.runtime_smoke
        }
        self.assertGreaterEqual(len(runtime_ids), 25)

    @runtime_routes("operations.instructions")
    def test_instruction_tab_is_visible_and_primary_action_is_usable(self):
        root = tk.Tk()
        root.geometry("1000x700")
        book = ttk.Notebook(root)
        book.pack(fill="both", expand=True)
        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            db=lambda: _DummyCon(),
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: None,
                showerror=lambda *a, **k: None,
            ),
            filedialog=SimpleNamespace(asksaveasfilename=lambda *a, **k: ""),
        )
        app = SimpleNamespace()
        try:
            with mock.patch.object(
                safety_instructions_ui.ops,
                "list_employee_choices",
                return_value=[
                    {"id": 1, "label": "Іваненко Іван — Водій", "name": "Іваненко Іван"},
                    {"id": 2, "label": "Петренко Петро — Водій", "name": "Петренко Петро"},
                ],
            ):
                tab = safety_instructions_ui.install_instruction_tab(app, core, book)
            book.select(tab)
            root.deiconify()
            root.update()

            assert_widget_reachable(tab, "operations.instructions", container=root)
            select_all = button_by_text(tab, "Вибрати всіх")
            self.assertIsNotNone(select_all)
            activate_widget(select_all, "operations.instructions", container=tab)

            people = [
                widget for widget in walk(tab)
                if callable(getattr(widget, "curselection", None))
                and str(widget.cget("selectmode")) == "extended"
            ]
            self.assertEqual(len(people), 1)
            self.assertEqual(tuple(int(i) for i in people[0].curselection()), (0, 1))
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
