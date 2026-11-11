# -*- coding: utf-8 -*-
import sqlite3
import tkinter as tk
import unittest
from types import SimpleNamespace
from tkinter import ttk
from unittest import mock

import main
import operations_orders_ui
import vehicle_maintenance as maint
import vehicle_maintenance_ui as maintenance_ui
import v10710_features


def walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from walk(child)


def button_texts(root):
    result = []
    for widget in walk(root):
        try:
            if widget.winfo_class() in ("TButton", "Button"):
                result.append(str(widget.cget("text")))
        except Exception:
            pass
    return result


class _DummyCursor(list):
    def fetchall(self):
        return list(self)


class _DummyConnection:
    def execute(self, _sql, _args=()):
        return _DummyCursor()

    def close(self):
        pass


class _MaintenanceHarness(tk.Tk):
    def __init__(self):
        super().__init__()
        self._maintenance_center_window = None
        self.documents_opened = False

    def vehicle_document_control(self):
        self.documents_opened = True


class OperationsStoirUsabilityR1Tests(unittest.TestCase):
    def test_r1_identity_is_historical_anchor(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION), (10, 13, 1))

    def test_stoir_domain_keeps_profile_and_closed_request_result(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.executescript(
            """
            CREATE TABLE vehicles(
                id INTEGER PRIMARY KEY,
                name TEXT, plate TEXT, make_model TEXT,
                active INTEGER DEFAULT 1
            );
            CREATE TABLE vehicle_odometer_readings(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                reading_km INTEGER,
                reading_at TEXT,
                source_type TEXT,
                notes TEXT DEFAULT ''
            );
            INSERT INTO vehicles(id,name,plate,make_model,active)
            VALUES(1,'Тестовий автобус','BC0001AA','Test Bus',1);
            """
        )
        maint.ensure_schema_on_connection(con)
        maint.save_profile(
            con, 1,
            profile_kind=maint.PROFILE_CUSTOM,
            to1_interval_km=7000,
            to2_interval_km=28000,
            source_kind="manufacturer",
            source_note="Документація виробника",
            warning_km=900,
        )
        request_id = maint.create_repair_request(
            con, 1, "Люфт у підвісці",
            priority="high", reporter="водій"
        )
        maint.update_repair_request(
            con, request_id,
            status=maint.REQUEST_CLOSED,
            assignee="механік",
            resolution="Шарнір замінено, перевірено",
        )
        con.commit()

        profile = maint.get_profile(con, 1)
        request = maint.repair_requests(con, 1)[0]
        self.assertEqual(profile["to1_interval_km"], 7000)
        self.assertEqual(profile["to2_interval_km"], 28000)
        self.assertEqual(profile["warning_km"], 900)
        self.assertEqual(profile["source_kind"], "manufacturer")
        self.assertEqual(request["status"], maint.REQUEST_CLOSED)
        self.assertEqual(request["assignee"], "механік")
        self.assertEqual(request["resolution"], "Шарнір замінено, перевірено")
        con.close()

    def test_live_stoir_window_exposes_complete_workflow(self):
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
                "id": 1, "plate": "BC0001AA",
                "name": "Тестовий автобус", "make_model": "Test Bus",
            },
            "plan": plan,
            "open_requests": 0,
        }]
        app = _MaintenanceHarness()
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
                app.update_idletasks()
                app.update()
                notebooks = [w for w in walk(win) if isinstance(w, ttk.Notebook)]
                self.assertEqual(len(notebooks), 1)
                book = notebooks[0]
                labels = [book.tab(tab_id, "text") for tab_id in book.tabs()]
                self.assertEqual(labels[0], "Стан автопарку")

                texts = button_texts(win)
                for label in (
                    "Налаштувати періодичність ТО…",
                    "Нова заявка…",
                    "Взяти в роботу…",
                    "Закрити з результатом…",
                    "Відкрити документи ТЗ…",
                ):
                    self.assertIn(label, texts)
        finally:
            app.destroy()

    def test_operations_ui_guides_order_lifecycle_and_guards_history(self):
        source = operations_orders_ui.__file__
        text = open(source, "r", encoding="utf-8").read()
        with open(
            "src/taxo/order_type_catalog_ui.py",
            "r",
            encoding="utf-8",
        ) as catalog_file:
            text += catalog_file.read()
        with open(
            "src/taxo/order_register_ui.py",
            "r",
            encoding="utf-8",
        ) as register_file:
            text += register_file.read()
        for marker in (
            "Що потрібно оформити?",
            "Новий наказ…",
            "Ввести в дію в Taxo",
            "Підпис на папері: так / ні",
            "Історія…",
            "Скасувати наказ",
            "Видалити наказ",
            "require_mutable_order",
        ):
            self.assertIn(marker, text)
        self.assertIn("def delete_selected_order():", text)

    def test_operations_document_desk_links_stoir(self):
        self.assertIn(
            ("СТОІР — стан автопарку", "open_vehicle_maintenance"),
            tuple(
                item
                for _group, actions in v10710_features.DOCUMENT_CENTER_GROUPS
                for item in actions
            ),
        )


if __name__ == "__main__":
    unittest.main()
