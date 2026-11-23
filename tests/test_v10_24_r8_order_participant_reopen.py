# -*- coding: utf-8 -*-
"""10.24-r8: reopening an order must preserve participant context and data."""
import sqlite3
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from types import SimpleNamespace
from tkinter import ttk

import operations_orders as ops
import order_entities_ui
import workspace


def _walk(widget):
    yield widget
    for child in widget.winfo_children():
        yield from _walk(child)


def _label_text(widget, root):
    try:
        var_name = str(widget.cget("textvariable") or "")
    except Exception:
        var_name = ""
    if var_name:
        try:
            return str(root.getvar(var_name))
        except Exception:
            pass
    try:
        return str(widget.cget("text") or "")
    except Exception:
        return ""


class OrderParticipantReopenR8Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / "work"
        paths = workspace.ensure_workspace(self.workspace)
        self.db_path = paths["main_db"]
        con = self.connect()
        con.executescript("""
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
                employee_id INTEGER PRIMARY KEY,
                registry_person_id TEXT DEFAULT ''
            );
            CREATE TABLE vehicles (
                id INTEGER PRIMARY KEY, name TEXT, plate TEXT, make_model TEXT,
                vin TEXT, garage_no TEXT, active INTEGER DEFAULT 1
            );
            INSERT INTO employees VALUES
                (1,'Ivanenko','Ivan','','Driver','001','1111111111',1,11);
            INSERT INTO employee_roles VALUES (1,'Driver');
            INSERT INTO drivers VALUES (11,1,'');
            INSERT INTO vehicles VALUES
                (10,'Bus 10','BC0010AA','MAN Lion',
                 'WMA00000000000010','10',1);
        """)
        ops.ensure_schema_on_connection(con)
        self.order_id = ops.create_order(
            con,
            order_type=ops.TYPE_OCCUPATIONAL_SAFETY,
            order_no="E2E-8",
            order_date="23.11.2026",
            subject="Reopen participant control",
            body_text="Verify fresh UI round-trip.",
        )
        self.entity_id = ops.add_order_entity(
            con,
            self.order_id,
            ops.ORDER_ENTITY_EMPLOYEE,
            1,
            role="Responsible",
            note="Keep after reopen",
        )
        con.commit()
        row = con.execute(
            "SELECT snapshot_json FROM operations_order_entities WHERE id=?",
            (self.entity_id,),
        ).fetchone()
        self.snapshot_before = row["snapshot_json"]
        con.close()

    def connect(self):
        con = sqlite3.connect(str(self.db_path))
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def _open_entities_surface(self):
        root = tk.Tk()
        root.geometry("1024x700+10+10")
        host = ttk.Frame(root)
        host.pack(fill="both", expand=True)
        order_tree = ttk.Treeview(root)
        order_tree.insert("", "end", iid=str(self.order_id), values=("order",))
        messages = []

        def selected_order(quiet=False):
            sel = order_tree.selection()
            if not sel:
                return None
            con = self.connect()
            try:
                return ops.get_order(con, int(sel[0]))
            finally:
                con.close()

        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            db=self.connect,
            configure_toplevel=lambda *_a, **_k: None,
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: messages.append(("info", a, k)),
                showerror=lambda *a, **k: self.fail(
                    "Unexpected participant error: %r" % (a,)
                ),
                askyesno=lambda *_a, **_k: True,
            ),
        )
        refresh = order_entities_ui.install_order_entities_tab(
            core,
            ops,
            root,
            host,
            order_tree,
            selected_order,
            lambda row, *_a, **_k: row is not None,
        )
        order_tree.selection_set(str(self.order_id))
        order_tree.event_generate("<<TreeviewSelect>>")
        root.update_idletasks()
        root.update()
        return root, host, order_tree, refresh

    def _surface_state(self, root, host):
        labels = [
            _label_text(widget, root)
            for widget in _walk(host)
            if isinstance(widget, ttk.Label)
        ]
        trees = [
            widget for widget in _walk(host)
            if isinstance(widget, ttk.Treeview)
        ]
        self.assertEqual(len(trees), 1)
        tree = trees[0]
        rows = [
            tuple(tree.item(iid, "values"))
            for iid in tree.get_children("")
        ]
        return "\n".join(labels), tree, rows

    def test_fresh_ui_reopen_keeps_identity_participants_and_status_changes(self):
        root1, host1, _orders1, _refresh1 = self._open_entities_surface()
        try:
            text1, entity_tree1, rows1 = self._surface_state(root1, host1)
            self.assertIn("Наказ №E2E-8", text1)
            self.assertIn("23.11.2026", text1)
            self.assertIn("Чернетка", text1)
            self.assertIn("Reopen participant control", text1)
            self.assertEqual(len(rows1), 1)
            self.assertIn("Responsible", rows1[0])
            self.assertIn("Ivanenko Ivan", rows1[0])
            self.assertIn("Keep after reopen", rows1[0])
            entity_tree1.selection_set(str(self.entity_id))
        finally:
            root1.destroy()

        # A genuinely fresh widget tree simulates closing and reopening the
        # operations window. The source of truth must be the persisted DB.
        root2, host2, orders2, refresh2 = self._open_entities_surface()
        try:
            text2, entity_tree2, rows2 = self._surface_state(root2, host2)
            self.assertIn("Наказ №E2E-8", text2)
            self.assertIn("Чернетка", text2)
            self.assertEqual(rows2, rows1)

            # Status transitions belong to the order, not to the participant
            # snapshot. Refreshing the same open order must retain selection
            # and participant data while updating the visible order state.
            entity_tree2.selection_set(str(self.entity_id))
            con = self.connect()
            try:
                ops.approve_order(con, self.order_id)
                con.commit()
            finally:
                con.close()
            orders2.event_generate("<<TreeviewSelect>>")
            refresh2()
            root2.update_idletasks()
            root2.update()

            text3, entity_tree3, rows3 = self._surface_state(root2, host2)
            self.assertIn("Діє в Taxo", text3)
            self.assertEqual(rows3, rows2)
            self.assertEqual(
                tuple(entity_tree3.selection()),
                (str(self.entity_id),),
            )
        finally:
            root2.destroy()

        con = self.connect()
        try:
            row = con.execute(
                """SELECT role,note,snapshot_json,sequence_no
                   FROM operations_order_entities WHERE id=?""",
                (self.entity_id,),
            ).fetchone()
        finally:
            con.close()
        self.assertEqual(row["role"], "Responsible")
        self.assertEqual(row["note"], "Keep after reopen")
        self.assertEqual(row["snapshot_json"], self.snapshot_before)
        self.assertEqual(int(row["sequence_no"]), 1)


if __name__ == "__main__":
    unittest.main()
