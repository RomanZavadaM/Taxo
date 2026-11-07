# -*- coding: utf-8 -*-
import tkinter as tk
import unittest
from types import SimpleNamespace
from tkinter import ttk
from unittest import mock

import main
import operations_orders as ops
import operations_orders_ui
import vehicle_maintenance as maint
import vehicle_maintenance_ui as maintenance_ui
import v10710_features


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
        self._maintenance_center_window = None
        self._operations_center_window = None
        self.documents_opened = False

    def _company_name_value(self):
        return "Ізольований тест"

    def vehicle_document_control(self):
        self.documents_opened = True


class OperationsStoirUsabilityR2Tests(unittest.TestCase):
    def test_r2_identity_is_historical_anchor(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION), (10, 13, 2))

    def test_stoir_humanizes_internal_values(self):
        self.assertEqual(
            maintenance_ui._maintenance_event_label(maint.MAINTENANCE_SEASONAL),
            "Сезонне ТО",
        )
        self.assertEqual(
            maintenance_ui._maintenance_event_label(maint.MAINTENANCE_REPAIR),
            "Ремонт",
        )
        self.assertEqual(
            maintenance_ui._odometer_source_label("waybill_end"),
            "Шляховий лист — повернення",
        )
        self.assertEqual(
            maintenance_ui._display_day("2026-11-07"),
            "07.11.2026",
        )
        self.assertEqual(
            maintenance_ui._display_timestamp("2026-11-07T13:45:00"),
            "07.11.2026 13:45",
        )
        self.assertIn(
            "Інше джерело",
            maintenance_ui._odometer_source_label("future_source"),
        )

    def test_fleet_has_explicit_open_selected_vehicle_action(self):
        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: None,
                showerror=lambda *a, **k: None,
            ),
            db=lambda: _DummyConnection(),
            configure_toplevel=lambda *a, **k: None,
            fit_window_to_screen=lambda *a, **k: None,
        )
        plan = {
            "current_odometer_km": 100000,
            "average_daily_km": 100.0,
            "profile": {
                "profile_kind": maint.PROFILE_PASSENGER_BUS,
                "to1_interval_km": 5000,
                "to2_interval_km": 20000,
                "source_kind": "regulation_102",
                "source_note": "",
                "warning_km": 1000,
            },
            "to1": {"due": None, "status": "unknown", "forecast_date": None},
            "to2": {"due": None, "status": "unknown", "forecast_date": None},
        }
        fleet = [{
            "vehicle": {
                "id": 1,
                "plate": "BC0001AA",
                "name": "Тестовий автобус",
                "make_model": "Test Bus",
            },
            "plan": plan,
            "open_requests": 0,
        }]
        app = _AppHarness()
        app.withdraw()
        try:
            with mock.patch.object(maintenance_ui.maint, "ensure_schema"), \
                 mock.patch.object(maintenance_ui, "_vehicle_rows", return_value=[
                     {"id": 1, "plate": "BC0001AA", "name": "Тестовий автобус",
                      "make_model": "Test Bus", "active": 1}
                 ]), \
                 mock.patch.object(maintenance_ui.maint, "vehicle_plan", return_value=plan), \
                 mock.patch.object(maintenance_ui.maint, "repair_requests", return_value=[]), \
                 mock.patch.object(maintenance_ui.maint, "fleet_maintenance_report", return_value=fleet), \
                 mock.patch.object(maintenance_ui, "best_current_document", return_value=None):
                win = maintenance_ui.open_maintenance_center(app, core)
                win.geometry("920x600")
                app.update_idletasks()
                app.update()
                book = next(w for w in walk(win) if isinstance(w, ttk.Notebook))
                report_tab = book.tabs()[0]
                book.select(report_tab)
                app.update_idletasks()
                trees = [w for w in walk(win) if isinstance(w, ttk.Treeview)]
                report_tree = next(
                    tree for tree in trees
                    if tuple(tree["columns"]) == ("vehicle", "odometer", "avg", "to1", "to2", "requests")
                )
                report_tree.selection_set("1")
                button = button_by_text(win, "Відкрити вибране ТЗ")
                self.assertIsNotNone(button)
                self.assertTrue(button.winfo_ismapped())
                button.invoke()
                app.update_idletasks()
                self.assertEqual(book.tab(book.select(), "text"), "Огляд ТЗ / прогноз")
        finally:
            app.destroy()

    def test_orders_actions_are_split_across_rows_at_minimum_width(self):
        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: None,
                showerror=lambda *a, **k: None,
                askyesno=lambda *a, **k: False,
            ),
            db=lambda: _DummyConnection(),
            configure_toplevel=lambda *a, **k: None,
            fit_window_to_screen=lambda *a, **k: None,
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
                 mock.patch.object(operations_orders_ui.ops, "list_employee_choices", return_value=[]), \
                 mock.patch.object(operations_orders_ui.ops, "list_orders", return_value=[]):
                win = operations_orders_ui.open_operations_center(app, core)
                win.geometry("940x600")
                app.update_idletasks()
                app.update()
                labels = (
                    "Новий наказ…",
                    "Редагувати чернетку",
                    "Ввести в дію в Taxo",
                    "Історія…",
                    "Скасувати чернетку",
                    "Сформувати PDF",
                    "Позначити оригінал підписаним",
                )
                buttons = [button_by_text(win, label) for label in labels]
                self.assertTrue(all(button is not None for button in buttons))
                rows = {int(button.grid_info()["row"]) for button in buttons}
                self.assertGreaterEqual(len(rows), 3)
                for button in buttons:
                    self.assertTrue(button.winfo_ismapped())
        finally:
            app.destroy()

    def test_document_desk_adds_new_order_action_without_losing_catalog_route(self):
        source = open(v10710_features.__file__, "r", encoding="utf-8").read()
        self.assertIn("Оформити новий наказ…", source)
        self.assertIn("Каталог типів наказів", source)


if __name__ == "__main__":
    unittest.main()
