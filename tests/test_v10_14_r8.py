# -*- coding: utf-8 -*-
"""10.14-r8 — existing assignment order editing is strictly reachable."""
import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace
import unittest
from unittest import mock

import function_registry
import main
import operations_orders as ops
import operations_orders_ui
from runtime_reachability import runtime_routes, assert_widget_reachable, activate_widget


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


class ExistingAssignmentEditGuardR8Tests(unittest.TestCase):
    def test_r8_identity_and_registry(self):
        self.assertEqual(main.APP_VERSION, "10.14-r8")
        routes = {route.function_id: route for route in function_registry.FUNCTION_ROUTES}
        self.assertIn("operations.assignment_existing", routes)
        self.assertTrue(routes["operations.assignment_existing"].runtime_smoke)
        self.assertGreaterEqual(len(function_registry.required_route_ids()), 26)

    @runtime_routes("operations.assignment_existing")
    def test_existing_order_edit_shows_rows_and_opens_bulk_picker(self):
        route_id = "operations.assignment_existing"
        order = {
            "id": 25,
            "order_type": ops.TYPE_VEHICLE_ASSIGNMENT,
            "order_no": "25",
            "order_date": "2026-11-08",
            "order_series": ops.ORDER_SERIES_WORK,
            "place": "с. Муроване",
            "subject": "Про закріплення автотранспортних засобів",
            "preamble": "Для виконання виробничих завдань",
            "body_text": "",
            "control_employee_id": None,
            "status": ops.ORDER_DRAFT,
            "paper_original_signed": 0,
            "last_name": "",
            "first_name": "",
            "middle_name": "",
        }
        assignments = [
            {
                "id": 101, "order_id": 25, "sequence_no": 1,
                "vehicle_id": 10, "employee_id": 1,
                "vehicle_name": "Автобус 10", "make_model": "MAN",
                "plate": "BC0010AA",
                "last_name": "Іваненко", "first_name": "Іван", "middle_name": "",
                "valid_from": "2026-11-08", "valid_until": "",
            },
            {
                "id": 102, "order_id": 25, "sequence_no": 2,
                "vehicle_id": 11, "employee_id": 2,
                "vehicle_name": "Автобус 11", "make_model": "Mercedes",
                "plate": "BC0011AA",
                "last_name": "Петренко", "first_name": "Петро", "middle_name": "",
                "valid_from": "2026-11-08", "valid_until": "",
            },
        ]

        def fit(win, width, height, min_width, min_height):
            if width == 900:
                win.geometry("900x760+40+40")
            else:
                win.geometry("1100x760+20+20")

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
                     {"id": 1, "label": "Іваненко Іван — Водій"},
                     {"id": 2, "label": "Петренко Петро — Водій"},
                 ]), \
                 mock.patch.object(operations_orders_ui.ops, "list_orders", return_value=[order]), \
                 mock.patch.object(operations_orders_ui.ops, "order_assignments", return_value=assignments), \
                 mock.patch.object(operations_orders_ui.ops, "list_vehicle_choices", return_value=[
                     {"id": 10, "label": "BC0010AA · MAN", "name": "MAN", "plate": "BC0010AA"},
                     {"id": 11, "label": "BC0011AA · Mercedes", "name": "Mercedes", "plate": "BC0011AA"},
                 ]), \
                 mock.patch.object(operations_orders_ui.ops, "list_driver_choices", return_value=[
                     {"id": 1, "label": "Іваненко Іван — Водій", "name": "Іваненко Іван", "position": "Водій"},
                     {"id": 2, "label": "Петренко Петро — Водій", "name": "Петренко Петро", "position": "Водій"},
                 ]):
                win = operations_orders_ui.open_operations_center(app, core)
                app.update_idletasks()
                app.update()

                order_tree = next(
                    w for w in walk(win)
                    if str(w.winfo_class()) == "Treeview"
                    and "date" in tuple(str(x) for x in w.cget("columns"))
                    and "no" in tuple(str(x) for x in w.cget("columns"))
                )
                order_tree.selection_set("25")
                order_tree.focus("25")
                order_tree.event_generate("<<TreeviewSelect>>")
                app.update_idletasks()
                app.update()

                edit = button_by_text(win, "Редагувати наказ")
                self.assertIsNotNone(edit)
                activate_widget(edit, route_id, container=win)
                app.update_idletasks()
                app.update()

                dialogs = [
                    w for w in walk(win)
                    if isinstance(w, tk.Toplevel) and w is not win
                    and str(w.title()) == "Редагувати наказ"
                ]
                self.assertEqual(len(dialogs), 1)
                dialog = dialogs[0]
                assert_widget_reachable(dialog, route_id)

                current_tree = getattr(dialog, "_taxo_existing_assignment_tree", None)
                bulk_button = getattr(dialog, "_taxo_existing_assignment_bulk_button", None)
                manage_button = getattr(dialog, "_taxo_existing_assignment_manage_button", None)
                self.assertIsNotNone(current_tree)
                self.assertIsNotNone(bulk_button)
                self.assertIsNotNone(manage_button)
                assert_widget_reachable(current_tree, route_id, container=dialog)
                self.assertEqual(len(current_tree.get_children()), 2)
                assert_widget_reachable(manage_button, route_id, container=dialog)

                activate_widget(bulk_button, route_id, container=dialog)
                app.update_idletasks()
                app.update()

                bulk_dialogs = [
                    w for w in walk(win)
                    if isinstance(w, tk.Toplevel) and w is not win
                    and str(w.title()) == "Додати кілька закріплень"
                ]
                self.assertEqual(len(bulk_dialogs), 1)
                bulk_dialog = bulk_dialogs[0]
                assert_widget_reachable(bulk_dialog, route_id)
                listboxes = [
                    w for w in walk(bulk_dialog)
                    if str(w.winfo_class()) == "Listbox"
                ]
                self.assertEqual(len(listboxes), 2)
                for lb in listboxes:
                    assert_widget_reachable(lb, route_id, container=bulk_dialog)
                    self.assertEqual(lb.size(), 2)
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
