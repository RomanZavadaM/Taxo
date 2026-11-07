# -*- coding: utf-8 -*-
import sqlite3
import tkinter as tk
import unittest
from types import SimpleNamespace
from tkinter import ttk
from unittest import mock

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


class AssignmentOrderBaseSelectorsR4Tests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys=ON")
        self.con.executescript(
            """
            CREATE TABLE employees(
                id INTEGER PRIMARY KEY,
                last_name TEXT, first_name TEXT, middle_name TEXT,
                position TEXT, active INTEGER DEFAULT 1, driver_id INTEGER
            );
            CREATE TABLE employee_roles(employee_id INTEGER, role TEXT);
            CREATE TABLE drivers(
                id INTEGER PRIMARY KEY,
                active INTEGER DEFAULT 1,
                driver_end_date TEXT DEFAULT ''
            );
            CREATE TABLE vehicles(
                id INTEGER PRIMARY KEY,
                name TEXT, plate TEXT, make_model TEXT, active INTEGER DEFAULT 1
            );
            CREATE TABLE employee_military_profile(
                employee_id INTEGER PRIMARY KEY,
                military_specialty TEXT, military_rank TEXT
            );

            INSERT INTO employees VALUES(1,'Іваненко','Іван','','Водій',1,NULL);
            INSERT INTO employee_roles VALUES(1,'Водій');
            INSERT INTO employees VALUES(2,'Механік','Марко','','Механік',1,NULL);
            INSERT INTO employee_roles VALUES(2,'Механік');
            INSERT INTO employees VALUES(3,'Петренко','Петро','','Водій',1,33);
            INSERT INTO drivers VALUES(33,1,'');
            INSERT INTO employees VALUES(4,'Старий','Водій','','Водій',1,44);
            INSERT INTO drivers VALUES(44,0,'2026-10-31');
            INSERT INTO employees VALUES(5,'Неактивний','Водій','','Водій',0,NULL);
            INSERT INTO employee_roles VALUES(5,'Водій автотранспортних засобів');

            INSERT INTO vehicles VALUES(10,'Автобус 10','BC0010AA','MAN',1);
            INSERT INTO vehicles VALUES(20,'Автобус 20','BC0020AA','Mercedes',0);
            """
        )
        ops.ensure_schema_on_connection(self.con)

    def tearDown(self):
        self.con.close()

    def test_identity_is_10_13_r4(self):
        self.assertEqual(main.APP_VERSION, "10.13-r4")

    def test_driver_choices_use_driver_base_not_all_employees(self):
        current = ops.list_driver_choices(self.con, active_only=True)
        self.assertEqual([row["id"] for row in current], [1, 3])
        self.assertNotIn(2, [row["id"] for row in current])
        historical = ops.list_driver_choices(self.con, active_only=False)
        self.assertEqual({row["id"] for row in historical}, {1, 3, 4, 5})

    def test_assignment_order_can_create_first_pair_from_database(self):
        oid = ops.create_vehicle_assignment_order(
            self.con,
            order_no="101",
            order_date="07.11.2026",
            place="Львів",
            subject="Про закріплення транспортного засобу",
            initial_vehicle_id=10,
            initial_employee_id=1,
        )
        order = ops.get_order(self.con, oid)
        rows = ops.order_assignments(self.con, oid)
        self.assertEqual(order["order_type"], ops.TYPE_VEHICLE_ASSIGNMENT)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["vehicle_id"], 10)
        self.assertEqual(rows[0]["employee_id"], 1)
        self.assertEqual(rows[0]["valid_from"], "2026-11-07")

    def test_incomplete_first_pair_is_rejected_before_order_is_created(self):
        before = self.con.execute("SELECT COUNT(*) FROM operations_orders").fetchone()[0]
        with self.assertRaisesRegex(ValueError, "транспортний засіб, і водія"):
            ops.create_vehicle_assignment_order(
                self.con, order_no="102", order_date="07.11.2026",
                initial_vehicle_id=10, initial_employee_id=None,
            )
        after = self.con.execute("SELECT COUNT(*) FROM operations_orders").fetchone()[0]
        self.assertEqual(after, before)

    def test_empty_first_pair_preserves_old_draft_workflow(self):
        oid = ops.create_vehicle_assignment_order(
            self.con, order_no="103", order_date="07.11.2026"
        )
        self.assertEqual(ops.order_assignments(self.con, oid), [])

    def test_live_order_dialog_uses_active_vehicle_and_driver_sources(self):
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
            fit_window_to_screen=lambda *a, **k: None,
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
                 mock.patch.object(
                     operations_orders_ui.ops, "list_vehicle_choices",
                     return_value=[{"id": 10, "label": "BC0010AA · MAN", "name": "MAN", "plate": "BC0010AA"}],
                 ) as vehicle_choices, \
                 mock.patch.object(
                     operations_orders_ui.ops, "list_driver_choices",
                     return_value=[{"id": 1, "label": "Іваненко Іван — Водій", "name": "Іваненко Іван", "position": "Водій"}],
                 ) as driver_choices:
                win = operations_orders_ui.open_operations_center(app, core)
                app.update_idletasks()
                button = button_by_text(win, "Закріпити ТЗ за водіями")
                self.assertIsNotNone(button)
                button.invoke()
                app.update_idletasks()
                app.update()

                dialogs = [
                    w for w in walk(win)
                    if isinstance(w, tk.Toplevel) and w is not win
                    and str(w.title()) == "Створити наказ"
                ]
                self.assertTrue(dialogs)
                texts = []
                for widget in walk(win):
                    try:
                        value = str(widget.cget("text"))
                    except Exception:
                        continue
                    if value:
                        texts.append(value)
                self.assertIn("Транспортний засіб", texts)
                self.assertIn("Водій із бази водіїв", texts)
                vehicle_choices.assert_called_with(mock.ANY, active_only=True)
                driver_choices.assert_called_with(mock.ANY, active_only=True)
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
