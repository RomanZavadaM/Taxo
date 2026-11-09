# -*- coding: utf-8 -*-
"""10.14-r6 — bulk driver/vehicle assignment must remain visibly reachable."""
import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace
import unittest
from unittest import mock

import function_registry
import main
import operations_orders as ops
import operations_orders_ui


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


class _DummyCursor(list):
    def fetchone(self):
        return self[0] if self else None
    def fetchall(self):
        return list(self)


class _DummyConnection:
    def execute(self, _sql, _args=()):
        return _DummyCursor()
    def close(self):
        pass


class _AppHarness(tk.Tk):
    def __init__(self):
        super().__init__()
        self._operations_center_window = None
    def _company_name_value(self):
        return "Ізольований тест"


class AssignmentVisibilityGuardR6Tests(unittest.TestCase):
    def test_r6_identity(self):
        self.assertEqual(main.APP_VERSION, "10.14-r6")

    def test_bulk_assignment_is_first_class_feature_loss_route(self):
        routes = {route.function_id: route for route in function_registry.FUNCTION_ROUTES}
        self.assertIn("operations.assignment_bulk", routes)
        self.assertTrue(routes["operations.assignment_bulk"].required)
        self.assertTrue(routes["operations.assignment_bulk"].runtime_smoke)
        self.assertGreaterEqual(len(function_registry.required_route_ids()), 25)

    def test_assignment_lists_are_mapped_and_inside_minimum_dialog(self):
        def fit(win, width, height, min_width, min_height):
            if width == 900:
                win.geometry("760x560")
            else:
                win.geometry("1000x700")

        core = SimpleNamespace(
            tk=tk, ttk=ttk,
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: None,
                showerror=lambda *a, **k: None,
                askyesno=lambda *a, **k: False,
            ),
            filedialog=SimpleNamespace(asksaveasfilename=lambda *a, **k: ""),
            db=lambda: _DummyConnection(),
            configure_toplevel=lambda *a, **k: None,
            fit_window_to_screen=fit,
            OUTPUT_DIR=__import__("pathlib").Path("."),
        )
        app = _AppHarness()
        app.withdraw()
        try:
            with mock.patch.object(operations_orders_ui.ops, "ensure_schema"), \
                 mock.patch.object(operations_orders_ui.ops, "settings", return_value={
                     "operations_responsible_employee_id": None,
                     "military_transport_responsible_employee_id": None,
                     "order_place": "",
                 }), \
                 mock.patch.object(operations_orders_ui.ops, "list_employee_choices", return_value=[
                     {"id": 1, "label": "Іваненко Іван — Водій"}
                 ]), \
                 mock.patch.object(operations_orders_ui.ops, "list_orders", return_value=[]), \
                 mock.patch.object(operations_orders_ui.ops, "list_vehicle_choices", return_value=[
                     {"id": 10, "label": "BC0010AA · MAN", "name": "MAN", "plate": "BC0010AA"},
                     {"id": 11, "label": "BC0011AA · MAN", "name": "MAN", "plate": "BC0011AA"},
                 ]), \
                 mock.patch.object(operations_orders_ui.ops, "list_driver_choices", return_value=[
                     {"id": 1, "label": "Іваненко Іван — Водій", "name": "Іваненко Іван", "position": "Водій"},
                     {"id": 2, "label": "Петренко Петро — Водій", "name": "Петренко Петро", "position": "Водій"},
                 ]):
                win = operations_orders_ui.open_operations_center(app, core)
                app.update_idletasks()
                app.update()

                notebooks = [w for w in walk(win) if isinstance(w, ttk.Notebook)]
                self.assertEqual(len(notebooks), 1)
                book = notebooks[0]
                catalog_tab = next(
                    tab for tab in book.tabs()
                    if str(book.tab(tab, "text")) == "Каталог наказів"
                )
                book.select(catalog_tab)
                app.update_idletasks()
                app.update()

                quick = button_by_text(win, "Закріпити ТЗ за водіями")
                self.assertIsNotNone(quick)
                self.assertTrue(quick.winfo_ismapped())
                quick.invoke()
                app.update_idletasks()
                app.update()

                dialogs = [
                    w for w in walk(win)
                    if isinstance(w, tk.Toplevel) and w is not win
                    and str(w.title()) == "Створити наказ"
                ]
                self.assertEqual(len(dialogs), 1)
                dialog = dialogs[0]
                vehicle_list = getattr(dialog, "_taxo_assignment_vehicle_list", None)
                driver_list = getattr(dialog, "_taxo_assignment_driver_list", None)
                self.assertIsNotNone(vehicle_list)
                self.assertIsNotNone(driver_list)
                self.assertEqual(vehicle_list.size(), 2)
                self.assertEqual(driver_list.size(), 2)
                for lb in (vehicle_list, driver_list):
                    self.assertTrue(lb.winfo_ismapped())
                    self.assertGreater(lb.winfo_width(), 1)
                    self.assertGreater(lb.winfo_height(), 1)
                    self.assertLessEqual(lb.winfo_rooty() + lb.winfo_height(),
                                         dialog.winfo_rooty() + dialog.winfo_height())

                assignment_tab = next(
                    tab for tab in book.tabs()
                    if str(book.tab(tab, "text")) == "Закріплення водіїв"
                )
                book.select(assignment_tab)
                app.update_idletasks()
                app.update()
                bulk = button_by_text(win, "Додати багато…")
                self.assertIsNotNone(bulk)
                self.assertTrue(bulk.winfo_ismapped())
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
