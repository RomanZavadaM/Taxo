# -*- coding: utf-8 -*-
"""10.24-r6: order participant changes must round-trip to every output surface."""
import sqlite3
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from types import SimpleNamespace

from docx import Document
from tkinter import ttk

import operations_orders as ops
import order_entities_ui
import workspace
from order_document_formats import build_order_docx
from pdf_test_utils import open_pdf
from v1073_features import export_order_pdf_with_appendices


def _buttons(widget, label):
    result = []
    def walk(parent):
        for child in parent.winfo_children():
            try:
                if (
                    child.winfo_class() in ("TButton", "Button")
                    and str(child.cget("text")) == label
                ):
                    result.append(child)
            except Exception:
                pass
            walk(child)
    walk(widget)
    return result


def _entries(widget):
    result = []
    def walk(parent):
        for child in parent.winfo_children():
            if isinstance(child, ttk.Entry):
                result.append(child)
            walk(child)
    walk(widget)
    return result


def _listboxes(widget):
    result = []
    def walk(parent):
        for child in parent.winfo_children():
            if isinstance(child, tk.Listbox):
                result.append(child)
            walk(child)
    walk(widget)
    return result


class OrderParticipantE2ER6Tests(unittest.TestCase):
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
                (1,'Ivanenko','Ivan','','Driver','001','1111111111',1,11),
                (2,'Petrenko','Petro','','Mechanic','002','2222222222',1,NULL);
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
            order_no="E2E-6",
            order_date="23.11.2026",
            subject="Participant end-to-end",
            body_text="Check every output surface.",
        )
        self.entity_id = ops.add_order_entity(
            con,
            self.order_id,
            ops.ORDER_ENTITY_EMPLOYEE,
            1,
            role="Participant",
            note="Initial",
        )
        con.commit()
        con.close()

    def connect(self, root=None):
        target = workspace.paths_for(root or self.workspace)["main_db"]
        con = sqlite3.connect(str(target))
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def _order_and_entities(self, root=None):
        con = self.connect(root)
        try:
            order = ops.get_order(con, self.order_id)
            entities = tuple(ops.list_order_entities(con, self.order_id))
            return order, entities
        finally:
            con.close()

    def test_live_edit_and_remove_refresh_existing_preview(self):
        root = tk.Tk()
        root.geometry("1180x760+10+10")
        tab = ttk.Frame(root)
        tab.pack(fill="both", expand=True)
        order_tree = ttk.Treeview(root)
        messages = []
        preview = {"text": "", "count": 0}

        def refresh_preview(order_id):
            self.assertEqual(int(order_id), self.order_id)
            order, entities = self._order_and_entities()
            preview["text"] = ops.order_preview_text(order, entities=entities)
            preview["count"] += 1
            return 1

        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            db=self.connect,
            configure_toplevel=lambda *_a, **_k: None,
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: messages.append((a, k)),
                showerror=lambda *a, **k: self.fail(
                    "Unexpected participant error: %r" % (a,)
                ),
                askyesno=lambda *a, **k: True,
            ),
        )
        order, _ = self._order_and_entities()
        snapshot = dict(order)
        try:
            refresh = order_entities_ui.install_order_entities_tab(
                core,
                ops,
                root,
                tab,
                order_tree,
                lambda quiet=True: snapshot,
                lambda *_args: True,
                refresh_open_order_previews=refresh_preview,
            )
            refresh()
            root.update()

            tree = next(
                widget
                for frame in tab.winfo_children()
                if isinstance(frame, ttk.Frame)
                for widget in frame.winfo_children()
                if isinstance(widget, ttk.Treeview)
            )
            tree.selection_set(str(self.entity_id))

            edit = _buttons(tab, "Змінити роль / примітку…")
            self.assertEqual(len(edit), 1)
            edit[0].invoke()
            root.update()

            dialog = next(
                child for child in root.winfo_children()
                if isinstance(child, tk.Toplevel)
            )
            entries = _entries(dialog)
            self.assertEqual(len(entries), 2)
            entries[0].delete(0, "end")
            entries[0].insert(0, "Responsible")
            entries[1].delete(0, "end")
            entries[1].insert(0, "Updated")
            _buttons(dialog, "Зберегти зміни")[0].invoke()
            root.update()

            self.assertEqual(preview["count"], 1)
            self.assertIn("Responsible", preview["text"])
            self.assertIn("Ivanenko Ivan", preview["text"])

            tree.selection_set(str(self.entity_id))
            _buttons(tab, "Прибрати вибрані")[0].invoke()
            root.update()
            self.assertEqual(preview["count"], 2)
            self.assertNotIn("Ivanenko Ivan", preview["text"])

            _buttons(tab, "Додати працівників…")[0].invoke()
            root.update()
            picker = next(
                child for child in root.winfo_children()
                if isinstance(child, tk.Toplevel)
            )
            picker_entries = _entries(picker)
            self.assertGreaterEqual(len(picker_entries), 3)
            search = picker_entries[0]
            search.delete(0, "end")
            search.insert(0, "Petrenko")
            root.update()
            lb = _listboxes(picker)[0]
            self.assertEqual(lb.size(), 1)
            lb.selection_set(0)
            _buttons(picker, "Додати вибрані")[0].invoke()
            root.update()

            self.assertEqual(preview["count"], 3)
            self.assertIn("Petrenko Petro", preview["text"])
        finally:
            root.destroy()

    def test_preview_explains_that_participants_print_as_separate_page(self):
        order, entities = self._order_and_entities()
        text = ops.order_preview_text(order, entities=entities)
        self.assertIn(
            "у DOCX/PDF/JPG цей перелік друкується окремою структурованою сторінкою",
            text,
        )
        entities_ui = (
            Path(__file__).resolve().parents[1]
            / "src" / "taxo" / "order_entities_ui.py"
        ).read_text("utf-8")
        self.assertIn(
            "зі структурованого переліку наказу",
            entities_ui,
        )
        self.assertNotIn(
            "зі структурованого переліку чернетки",
            entities_ui,
        )

    def test_add_edit_remove_paths_all_call_live_preview_refresh(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src" / "taxo" / "order_entities_ui.py"
        ).read_text("utf-8")
        self.assertGreaterEqual(
            source.count('refresh_live_preview(order["id"])'),
            3,
        )
        register = (
            Path(__file__).resolve().parents[1]
            / "src" / "taxo" / "order_register_ui.py"
        ).read_text("utf-8")
        self.assertIn(
            "refresh_open_order_previews=refresh_open_order_previews",
            register,
        )
        self.assertIn(
            '"entity_update":"Змінено роль / примітку"',
            register,
        )

    def test_docx_and_pdf_contain_same_frozen_participant_snapshot(self):
        order, entities = self._order_and_entities()
        output = Path(self.temp.name) / "outputs"
        output.mkdir()
        docx_path = output / "order.docx"
        pdf_path = output / "order.pdf"

        build_order_docx(
            docx_path,
            ops,
            order,
            entities=entities,
            company={"name": "Test Company"},
        )

        class Core:
            def db(inner_self):
                return self.connect()

        export_order_pdf_with_appendices(
            Core(),
            pdf_path,
            order,
            assignments=(),
            company={"name": "Test Company"},
        )

        doc = Document(str(docx_path))
        docx_text = "\n".join(
            [p.text for p in doc.paragraphs]
            + [
                cell.text
                for table in doc.tables
                for row in table.rows
                for cell in row.cells
            ]
        )
        self.assertIn("Ivanenko Ivan", docx_text)
        self.assertIn("Participant", docx_text)
        self.assertIn("001", docx_text)

        with open_pdf(pdf_path) as pdf:
            self.assertGreaterEqual(pdf.page_count, 2)
            pdf_text = "\n".join(page.get_text() for page in pdf)
        self.assertIn("Ivanenko Ivan", pdf_text)
        self.assertIn("Participant", pdf_text)
        self.assertIn("001", pdf_text)

    def test_full_workspace_backup_restore_keeps_frozen_participant_snapshot(self):
        before_order, before_entities = self._order_and_entities()
        before = dict(before_entities[0])

        archive = workspace.create_workspace_backup_archive(
            self.workspace,
            Path(self.temp.name) / "orders-backup.zip",
            app_version="10.24-r5",
        )
        restored = Path(self.temp.name) / "restored"
        workspace.restore_workspace_backup_archive(archive, restored)

        con = self.connect(restored)
        try:
            after_order = ops.get_order(con, self.order_id)
            after_entities = tuple(
                ops.list_order_entities(con, self.order_id)
            )
        finally:
            con.close()

        self.assertEqual(dict(after_order), dict(before_order))
        self.assertEqual(len(after_entities), 1)
        after = dict(after_entities[0])
        for key in (
            "id",
            "order_id",
            "entity_type",
            "entity_id",
            "role",
            "note",
            "snapshot_json",
            "sequence_no",
        ):
            self.assertEqual(after[key], before[key])

    def test_runtime_pdf_wrapper_is_registered_before_current_feature_layers(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src" / "taxo" / "feature_layers.py"
        ).read_text("utf-8")
        self.assertIn(
            'FeatureLayer("v1073", install_v1073)',
            source,
        )
        self.assertIn(
            'FeatureLayer("v1024-r3-correspondence-ui"',
            source,
        )
        self.assertLess(
            source.index('FeatureLayer("v1073", install_v1073)'),
            source.index('FeatureLayer("v1024-r3-correspondence-ui"'),
        )


if __name__ == "__main__":
    unittest.main()
