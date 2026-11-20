# -*- coding: utf-8 -*-
"""10.23-r2: editing existing order participants must preserve identity/history."""
import json
import sqlite3
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from tkinter import ttk
from types import SimpleNamespace

import operations_orders as ops
import order_entities_ui
from runtime_reachability import runtime_routes, activate_widget


def buttons(widget, label):
    result = []
    def walk(parent):
        for child in parent.winfo_children():
            try:
                if child.winfo_class() in ("TButton", "Button") and str(child.cget("text")) == label:
                    result.append(child)
            except Exception:
                pass
            walk(child)
    walk(widget)
    return result


class OrderEntityEditR2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "orders.sqlite3"
        self.con = self.connect()
        self.addCleanup(self.close_current)
        self.con.executescript("""
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY, last_name TEXT, first_name TEXT,
                middle_name TEXT, position TEXT, personnel_no TEXT,
                rnokpp TEXT, active INTEGER DEFAULT 1, driver_id INTEGER
            );
            CREATE TABLE employee_roles (employee_id INTEGER, role TEXT);
            CREATE TABLE drivers (
                id INTEGER PRIMARY KEY, active INTEGER DEFAULT 1,
                driver_end_date TEXT DEFAULT ''
            );
            CREATE TABLE employee_military_profile (
                employee_id INTEGER PRIMARY KEY, registry_person_id TEXT DEFAULT ''
            );
            CREATE TABLE vehicles (
                id INTEGER PRIMARY KEY, name TEXT, plate TEXT, make_model TEXT,
                vin TEXT, garage_no TEXT, active INTEGER DEFAULT 1
            );
            INSERT INTO employees VALUES
                (1,'Іваненко','Іван','','Водій','001','1111111111',1,11),
                (2,'Петренко','Петро','','Механік','002','2222222222',1,NULL);
            INSERT INTO drivers VALUES (11,1,'');
            INSERT INTO employee_roles VALUES (1,'Водій');
            INSERT INTO vehicles VALUES
                (10,'Автобус 10','BC0010AA','MAN Lion','WMA00000000000010','10',1);
        """)
        ops.ensure_schema_on_connection(self.con)
        self.oid = ops.create_order(
            self.con, order_type=ops.TYPE_OCCUPATIONAL_SAFETY,
            order_no="EDIT-1", order_date="19.11.2026",
            subject="Тест редагування", body_text="Виконати вимоги."
        )
        self.link = ops.add_order_entity(
            self.con, self.oid, ops.ORDER_ENTITY_EMPLOYEE, 1,
            role="Учасник", note="Стара примітка"
        )
        self.con.commit()

    def connect(self):
        con = sqlite3.connect(str(self.path))
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def close_current(self):
        self.con.close()

    def reopen(self):
        self.con.commit()
        self.con.close()
        self.con = self.connect()

    def test_update_keeps_frozen_snapshot_sequence_and_audit_after_reopen(self):
        before = dict(ops.get_order_entity(self.con, self.link))
        self.assertTrue(ops.update_order_entity_fields(
            self.con, self.link, role="Відповідальний", note="Нова примітка"
        ))
        self.reopen()
        after = dict(ops.get_order_entity(self.con, self.link))
        for key in ("id", "order_id", "entity_type", "entity_id", "snapshot_json", "sequence_no"):
            self.assertEqual(before[key], after[key])
        self.assertEqual(after["role"], "Відповідальний")
        self.assertEqual(after["note"], "Нова примітка")
        self.assertEqual(json.loads(after["snapshot_json"])["name"], "Іваненко Іван")
        preview = ops.order_preview_text(
            ops.get_order(self.con, self.oid),
            entities=ops.list_order_entities(self.con, self.oid),
        )
        self.assertIn("Відповідальний", preview)
        self.assertIn("Іваненко Іван", preview)
        self.assertTrue(any(row["action"] == "entity_update"
                            for row in ops.order_history(self.con, self.oid)))

    def test_no_change_does_not_write_new_history(self):
        before = len(ops.order_history(self.con, self.oid))
        self.assertFalse(ops.update_order_entity_fields(
            self.con, self.link, role="Учасник", note="Стара примітка"
        ))
        self.assertEqual(len(ops.order_history(self.con, self.oid)), before)

    def test_duplicate_role_is_refused_without_altering_rows(self):
        second = ops.add_order_entity(
            self.con, self.oid, ops.ORDER_ENTITY_EMPLOYEE, 1,
            role="Інша роль"
        )
        before = dict(ops.get_order_entity(self.con, second))
        with self.assertRaisesRegex(ValueError, "вже є"):
            ops.update_order_entity_fields(
                self.con, second, role="Учасник", note="Не зберігати"
            )
        self.assertEqual(dict(ops.get_order_entity(self.con, second)), before)

    @runtime_routes("operations.entity_edit")
    def test_live_edit_button_saves_existing_row_and_reselects_it(self):
        app = tk.Tk()
        app.geometry("1200x800")
        win = tk.Toplevel(app)
        win.geometry("1120x710+30+30")
        outer = ttk.Frame(win)
        outer.pack(fill="both", expand=True)
        tab = ttk.Frame(outer)
        tab.pack(fill="both", expand=True)
        order_tree = ttk.Treeview(outer)
        messages = []
        core = SimpleNamespace(
            tk=tk, ttk=ttk,
            db=self.connect,
            configure_toplevel=lambda *a, **k: None,
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: messages.append((a, k)),
                showerror=lambda *a, **k: self.fail("Unexpected edit error: %s" % (a,)),
            ),
        )
        order_snapshot = dict(ops.get_order(self.con, self.oid))
        self.con.commit()  # do not hold a writer lock while the UI opens its own connection
        selected_order = lambda quiet=True: order_snapshot
        try:
            refresh = order_entities_ui.install_order_entities_tab(
                core, ops, win, tab, order_tree, selected_order,
                lambda *_args: True,
            )
            refresh()
            app.update()
            tables = [widget for widget in tab.winfo_children()
                      if isinstance(widget, ttk.Frame)]
            links = [
                widget for frame in tables for widget in frame.winfo_children()
                if isinstance(widget, ttk.Treeview)
            ]
            self.assertEqual(len(links), 1)
            links[0].selection_set(str(self.link))
            edit = buttons(win, "Змінити роль / примітку…")
            self.assertEqual(len(edit), 1)
            activate_widget(edit[0], "operations.entity_edit", container=win)
            app.update()
            dialogs = [child for child in win.winfo_children()
                       if isinstance(child, tk.Toplevel)]
            self.assertEqual(len(dialogs), 1)
            entries = []
            def find_entries(w):
                for child in w.winfo_children():
                    if isinstance(child, ttk.Entry):
                        entries.append(child)
                    find_entries(child)
            find_entries(dialogs[0])
            self.assertEqual(len(entries), 2)
            entries[0].delete(0, "end")
            entries[0].insert(0, "Керівник перевірки")
            entries[1].delete(0, "end")
            entries[1].insert(0, "Точно збережена примітка")
            save = buttons(dialogs[0], "Зберегти зміни")
            self.assertEqual(len(save), 1)
            save[0].invoke()
            self.assertEqual(links[0].selection(), (str(self.link),))
            check = self.connect()
            try:
                item = ops.get_order_entity(check, self.link)
                self.assertEqual(item["role"], "Керівник перевірки")
                self.assertEqual(item["note"], "Точно збережена примітка")
            finally:
                check.close()
            self.assertTrue(messages)
        finally:
            app.destroy()

    @runtime_routes("operations.entity_search_selection")
    def test_live_search_keeps_selected_people_across_filters(self):
        app = tk.Tk()
        app.geometry("1200x800")
        tab = ttk.Frame(app)
        tab.pack(fill="both", expand=True)
        order_tree = ttk.Treeview(app)
        messages = []
        core = SimpleNamespace(
            tk=tk, ttk=ttk, db=self.connect,
            configure_toplevel=lambda *_a, **_k: None,
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: messages.append(a),
                showerror=lambda *a, **k: self.fail("Unexpected picker error: %s" % (a,)),
            ),
        )
        snapshot = dict(ops.get_order(self.con, self.oid))
        self.con.commit()
        def walk(parent):
            for child in parent.winfo_children():
                yield child
                yield from walk(child)
        try:
            refresh = order_entities_ui.install_order_entities_tab(
                core, ops, app, tab, order_tree, lambda quiet=True: snapshot,
                lambda *_args: True,
            )
            refresh()
            app.update()
            self.assertTrue(any(isinstance(w, ttk.Label) and
                                "Тест редагування" in str(w.getvar(w.cget("textvariable")))
                                for w in walk(tab) if isinstance(w, ttk.Label) and w.cget("textvariable")))
            activate_widget(buttons(tab, "Додати працівників…")[0],"operations.entity_search_selection",container=app)
            app.update()
            dlg = next(w for w in app.winfo_children() if isinstance(w, tk.Toplevel))
            search = next(w for w in walk(dlg) if isinstance(w, ttk.Entry))
            lb = next(w for w in walk(dlg) if isinstance(w, tk.Listbox))
            search.insert(0, "Іваненко")
            app.update()
            self.assertEqual(lb.size(), 1)
            lb.selection_set(0)
            search.delete(0, "end")
            search.insert(0, "Петренко")
            app.update()
            self.assertEqual(lb.size(), 1)
            lb.selection_set(0)
            search.delete(0, "end")
            app.update()
            self.assertEqual(tuple(lb.curselection()), (0, 1))
            buttons(dlg, "Додати вибрані")[0].invoke()
            check = self.connect()
            try:
                self.assertEqual({row["entity_id"] for row in ops.list_order_entities(check, self.oid)}, {1, 2})
            finally:
                check.close()
            self.assertTrue(messages)
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
