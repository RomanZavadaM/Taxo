# -*- coding: utf-8 -*-
"""10.14-r9 — open order preview must sync automatically after assignment changes."""
from pathlib import Path
import sqlite3
import tempfile
import time
import workspace
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

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


class _AppHarness(tk.Tk):
    def __init__(self):
        super().__init__()
        self._operations_center_window = None

    def _company_name_value(self):
        return "Ізольований тест"


class LivePreviewSyncR9Tests(unittest.TestCase):
    def test_r9_identity_and_registry(self):
        self.assertIn(main.APP_VERSION, ("10.14-r9", "10.14-r10", "10.15-r1", "10.15-r2", "10.15-r3", "10.15-r4", "10.15-r5"))
        routes = {route.function_id: route for route in function_registry.FUNCTION_ROUTES}
        self.assertIn("operations.assignment_preview_sync", routes)
        self.assertTrue(routes["operations.assignment_preview_sync"].required)
        self.assertTrue(routes["operations.assignment_preview_sync"].runtime_smoke)
        self.assertGreaterEqual(len(function_registry.required_route_ids()), 27)

    @runtime_routes("operations.assignment_preview_sync")
    def test_open_preview_auto_updates_after_adding_single_assignment(self):
        route_id = "operations.assignment_preview_sync"
        order = {
            "id": 28,
            "order_type": ops.TYPE_VEHICLE_ASSIGNMENT,
            "order_no": "28",
            "order_date": "2026-11-09",
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
        state = {"rows": []}
        assignment_row = {
            "id": 301,
            "order_id": 28,
            "sequence_no": 1,
            "vehicle_id": 10,
            "employee_id": 1,
            "vehicle_name": "Автобус MAN",
            "make_model": "MAN A21 Lion's City NL273",
            "plate": "BC8824EM",
            "last_name": "Рудинець",
            "first_name": "Петро",
            "middle_name": "",
            "position": "Водій",
            "valid_from": "2026-11-09",
            "valid_until": "",
        }

        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: None,
                showerror=lambda *a, **k: None,
                showwarning=lambda *a, **k: None,
                askyesno=lambda *a, **k: False,
            ),
            filedialog=SimpleNamespace(asksaveasfilename=lambda *a, **k: ""),
            db=lambda: _DummyConnection(),
            configure_toplevel=lambda *a, **k: None,
            fit_window_to_screen=main.fit_window_to_screen,
            OUTPUT_DIR=Path("."),
        )
        app = _AppHarness()
        app.geometry("1200x820+10+10")
        app.withdraw()

        def add_pair(_con, order_id, vehicle_id, employee_id, **kwargs):
            self.assertEqual(int(order_id), 28)
            self.assertEqual((int(vehicle_id), int(employee_id)), (10, 1))
            state["rows"] = [dict(assignment_row)]
            return 301

        try:
            with mock.patch.object(operations_orders_ui.ops, "ensure_schema"), \
                 mock.patch.object(operations_orders_ui.ops, "settings", return_value={
                     "operations_responsible_employee_id": None,
                     "military_transport_responsible_employee_id": None,
                     "order_place": "",
                 }), \
                 mock.patch.object(operations_orders_ui.ops, "list_employee_choices", return_value=[]), \
                 mock.patch.object(operations_orders_ui.ops, "list_orders", return_value=[order]), \
                 mock.patch.object(operations_orders_ui.ops, "get_order", return_value=order), \
                 mock.patch.object(
                     operations_orders_ui.ops,
                     "order_assignments",
                     side_effect=lambda _con, _oid: list(state["rows"]),
                 ), \
                 mock.patch.object(operations_orders_ui.ops, "list_order_entities", return_value=[]), \
                 mock.patch.object(operations_orders_ui.ops, "employee_name", return_value=""), \
                 mock.patch.object(operations_orders_ui.ops, "list_vehicle_choices", return_value=[
                     {
                         "id": 10,
                         "label": "BC8824EM · MAN A21 Lion's City NL273",
                         "name": "Автобус MAN",
                         "plate": "BC8824EM",
                     }
                 ]), \
                 mock.patch.object(operations_orders_ui.ops, "list_driver_choices", return_value=[
                     {
                         "id": 1,
                         "label": "Рудинець Петро — Водій",
                         "name": "Рудинець Петро",
                         "position": "Водій",
                     }
                 ]), \
                 mock.patch.object(operations_orders_ui.ops, "add_vehicle_assignment", side_effect=add_pair), \
                 mock.patch.object(operations_orders_ui.ops, "verify_vehicle_assignment_pairs", return_value=1):
                win = operations_orders_ui.open_operations_center(app, core)
                app.update_idletasks()
                app.update()

                # Open the real combined catalog from Operations and then
                # preview an order without selecting it in the old table.
                with tempfile.TemporaryDirectory() as directory:
                    data = Path(directory) / "Data"
                    data.mkdir()
                    catalog_db = sqlite3.connect(str(data / "driver_worktime.sqlite3"))
                    catalog_db.execute(
                        "CREATE TABLE operations_orders (id INTEGER PRIMARY KEY, "
                        "order_date TEXT, order_no TEXT, order_type TEXT, subject TEXT)")
                    catalog_db.execute(
                        "INSERT INTO operations_orders VALUES "
                        "(28, '2026-11-09', '28', 'work', 'Тестовий наказ')")
                    catalog_db.commit()
                    catalog_db.close()
                    with mock.patch.object(workspace, "load_workspace_root", return_value=Path(directory)):
                        catalog_button = button_by_text(win, "Документи…")
                        self.assertIsNotNone(catalog_button)
                        catalog_button.invoke()
                        app.update()
                        catalog_win = next(
                            widget for widget in walk(win)
                            if isinstance(widget, tk.Toplevel)
                            and str(widget.title()) == "Документи"
                        )
                        tree = catalog_win._taxo_catalog_tree
                        deadline = time.monotonic() + 10
                        while not tree.get_children() and time.monotonic() < deadline:
                            app.update()
                            time.sleep(0.02)
                        self.assertEqual(len(tree.get_children()), 1)
                        tree.selection_set(tree.get_children()[0])
                        open_button = button_by_text(catalog_win, "Відкрити вибране")
                        self.assertIsNotNone(open_button)
                        open_button.invoke()
                        app.update()
                        direct_preview = next(
                            widget for widget in walk(win)
                            if isinstance(widget, tk.Toplevel)
                            and widget is not win
                            and str(widget.title()) == "Перегляд наказу №28"
                        )
                        self.assertTrue(direct_preview.winfo_exists())
                        direct_preview.destroy()
                        catalog_win.destroy()

                order_tree = next(
                    widget for widget in walk(win)
                    if str(widget.winfo_class()) == "Treeview"
                    and "date" in tuple(str(x) for x in widget.cget("columns"))
                    and "no" in tuple(str(x) for x in widget.cget("columns"))
                )
                order_tree.selection_set("28")
                order_tree.focus("28")
                order_tree.event_generate("<<TreeviewSelect>>")
                app.update()

                preview_button = button_by_text(win, "Переглянути / друк")
                self.assertIsNotNone(preview_button)
                preview_button.invoke()
                app.update_idletasks()
                app.update()

                preview_dialog = next(
                    widget for widget in walk(win)
                    if isinstance(widget, tk.Toplevel)
                    and widget is not win
                    and str(widget.title()) == "Перегляд наказу №28"
                )
                viewer = next(
                    widget for widget in walk(preview_dialog)
                    if str(widget.winfo_class()) == "Text"
                )
                assert_widget_reachable(preview_dialog, route_id)
                self.assertTrue(viewer.winfo_ismapped())
                self.assertGreater(viewer.winfo_width(), 1)
                self.assertGreater(viewer.winfo_height(), 1)
                self.assertIn("закріплення ще не додані", viewer.get("1.0", "end"))

                notebooks = [widget for widget in walk(win) if isinstance(widget, ttk.Notebook)]
                self.assertEqual(len(notebooks), 1)
                book = notebooks[0]
                assignments_tab = next(
                    tab for tab in book.tabs()
                    if str(book.tab(tab, "text")) == "Закріплення водіїв"
                )
                book.select(assignments_tab)
                app.update_idletasks()
                app.update()

                add_one = button_by_text(win, "Додати одну пару")
                self.assertIsNotNone(add_one)
                add_one.invoke()
                app.update_idletasks()
                app.update()

                assignment_dialog = next(
                    widget for widget in walk(win)
                    if isinstance(widget, tk.Toplevel)
                    and widget is not win
                    and str(widget.title()) == "Додати закріплення"
                )
                combos = [
                    widget for widget in walk(assignment_dialog)
                    if str(widget.winfo_class()) == "TCombobox"
                ]
                self.assertEqual(len(combos), 2)
                for combo in combos:
                    combo.current(0)

                add_button = button_by_text(assignment_dialog, "Додати")
                self.assertIsNotNone(add_button)
                activate_widget(add_button, route_id, container=assignment_dialog)
                app.update_idletasks()
                app.update()

                self.assertTrue(preview_dialog.winfo_exists())
                current_text = viewer.get("1.0", "end")
                self.assertNotIn("закріплення ще не додані", current_text)
                self.assertIn("MAN A21 Lion's City NL273", current_text)
                self.assertIn("BC8824EM", current_text)
                self.assertIn("Рудинець Петро", current_text)
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
