# -*- coding: utf-8 -*-
"""Missing employee document files are reported without changing records."""
import sqlite3
import tempfile
import tkinter as tk
import unittest
from tkinter import ttk
from types import SimpleNamespace
from datetime import date
from pathlib import Path

import employee_document_control_r7 as control
import personnel_registry as personnel
import workspace
from test_v10_10_r7 import make_db


class DocumentFileControlR4Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "workspace"
        self.root.mkdir()
        root = self.root

        class Core:
            DATA_ROOT = root

            @staticmethod
            def real_data_path(value):
                return workspace.resolved_path(value, root)

        self.core = Core
        self.con = make_db()
        control.save_requirement(self.con, 1, "Тест", required=True, expiry_control=True)
        self.document_id = personnel.save_employee_document(self.con, 1, {
            "doc_type": "Тест", "number": "SYNTHETIC", "expiry_date": "2030-01-01",
            "file_path": "workspace://Data/EmployeeDocuments/employee_000001/test.pdf",
        })
        self.con.commit()
        self.path = self.root / "Data/EmployeeDocuments/employee_000001/test.pdf"

    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()

    def set_document(self, path, expiry="2030-01-01"):
        self.con.execute("UPDATE employee_documents SET file_path=?, expiry_date=? WHERE id=?",
                         (str(path), expiry, self.document_id))
        self.con.commit()

    def row(self, problems=False):
        return control.document_control_rows(self.con, today=date(2026, 11, 10),
                                             problems_only=problems, core=self.core)

    def test_missing_then_restored_file_and_no_database_changes(self):
        before = tuple(self.con.execute("SELECT * FROM employee_documents WHERE id=?",
                                        (self.document_id,)).fetchone())
        row = self.row(True)[0]
        self.assertTrue(row["file_missing"])
        self.assertFalse(row["file_backed_up"])
        self.assertEqual(row["state"], control.STATE_FILE_MISSING)
        self.assertEqual(before, tuple(self.con.execute("SELECT * FROM employee_documents WHERE id=?",
                                                       (self.document_id,)).fetchone()))
        self.assertFalse(self.root.joinpath("Data").exists())
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b"synthetic")
        row = self.row()[0]
        self.assertEqual(row["state"], control.STATE_OK)
        self.assertFalse(row["file_missing"])
        self.assertTrue(row["file_backed_up"])
        self.assertEqual(self.row(True), [])

    def test_legacy_absolute_and_relative_paths_resolve_inside_workspace(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b"synthetic")
        for value in ("Data/EmployeeDocuments/employee_000001/test.pdf",
                      "Z:/old-taxo/Data/EmployeeDocuments/employee_000001/test.pdf",
                      str(self.path)):
            with self.subTest(path=value):
                self.set_document(value)
                row = self.row()[0]
                self.assertEqual(row["state"], control.STATE_OK)
                self.assertTrue(row["file_backed_up"])
                self.assertFalse(row["file_missing"])

    def test_external_url_and_missing_local_file_are_distinct(self):
        external = Path(self.tmp.name) / "external.pdf"
        external.write_bytes(b"external")
        self.set_document(external)
        row = self.row(True)[0]
        self.assertFalse(row["file_missing"])
        self.assertFalse(row["file_backed_up"])
        self.assertEqual(row["state"], control.STATE_COPY_REQUIRED)
        external.unlink()
        self.assertEqual(self.row(True)[0]["state"], control.STATE_FILE_MISSING)
        self.set_document("https://example.invalid/document")
        row = self.row(True)[0]
        self.assertFalse(row["file_missing"])
        self.assertFalse(row["file_backed_up"])
        self.assertEqual(row["state"], control.STATE_COPY_REQUIRED)

    def test_optional_expired_and_invalid_paths_are_visible(self):
        control.save_requirement(self.con, 1, "Тест", required=False, expiry_control=True)
        self.set_document("workspace://Data/EmployeeDocuments/missing.pdf", "2020-01-01")
        row = self.row(True)[0]
        self.assertEqual(row["state"], control.STATE_EXPIRED)
        self.assertTrue(row["file_missing"])
        self.assertIn("файл документа не знайдено", row["state_label"])
        self.set_document("workspace://../outside.pdf")
        self.assertEqual(self.row(True)[0]["state"], control.STATE_FILE_MISSING)
        self.assertFalse(self.row()[0]["file_backed_up"])


class DocumentControlWindowR4Tests(unittest.TestCase):
    def test_missing_file_shown_and_refresh_removes_resolved_problem(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "workspace"
            root.mkdir()
            dbfile = root / "test.sqlite3"
            seed = make_db()
            control.save_requirement(seed, 1, "Тест", required=True, expiry_control=True)
            personnel.save_employee_document(seed, 1, {
                "doc_type": "Тест", "number": "UI-SYNTHETIC",
                "expiry_date": "2030-01-01",
                "file_path": "workspace://Data/EmployeeDocuments/example.pdf",
            })
            seed.commit()
            dest = sqlite3.connect(str(dbfile))
            seed.backup(dest)
            dest.close()
            seed.close()

            def db():
                con = sqlite3.connect(str(dbfile))
                con.row_factory = sqlite3.Row
                return con

            core = SimpleNamespace(DATA_ROOT=root, tk=tk, ttk=ttk, db=db,
                                   real_data_path=lambda value: workspace.resolved_path(value, root))
            app_class = control.install(core, tk.Tk)
            app = app_class()
            try:
                app.open_required_employee_documents_r7()
                app.update()
                win = app._required_employee_documents_r7_window

                def walk(widget):
                    for child in widget.winfo_children():
                        yield child
                        yield from walk(child)

                widgets = list(walk(win))
                tree = next(w for w in widgets if isinstance(w, ttk.Treeview))
                items = tree.get_children()
                self.assertEqual(len(items), 1)
                values = tree.item(items[0], "values")
                self.assertEqual(values[-1], control.STATE_LABELS[control.STATE_FILE_MISSING])

                copy = root / "Data/EmployeeDocuments/example.pdf"
                copy.parent.mkdir(parents=True, exist_ok=True)
                copy.write_bytes(b"synthetic")
                button = next(w for w in widgets if isinstance(w, ttk.Button)
                              and str(w.cget("text")) == "Оновити")
                button.invoke()
                app.update()
                self.assertEqual(tree.get_children(), ())
            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main()
