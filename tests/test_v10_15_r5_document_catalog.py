# -*- coding: utf-8 -*-
"""Read-only combined catalog of existing orders and paper documents."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from tkinter import ttk
from types import SimpleNamespace
from unittest import mock

import document_catalog as catalog
import document_catalog_ui as catalog_ui
import workspace


class CombinedCatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "workspace"
        self.root.mkdir()
        self.db = self.root / "Data" / "driver_worktime.sqlite3"
        self.db.parent.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def seed_orders(self, count):
        con = sqlite3.connect(str(self.db))
        try:
            con.execute("CREATE TABLE operations_orders "
                        "(id INTEGER PRIMARY KEY, order_date TEXT, order_no TEXT, "
                        "order_type TEXT, subject TEXT)")
            con.executemany("INSERT INTO operations_orders VALUES (?, ?, ?, ?, ?)", [
                (i, "2026-11-10", "№%04d" % i, "work", "Тема %04d" % i)
                for i in range(1, count + 1)
            ])
            con.commit()
        finally:
            con.close()

    def paper_index(self, rows):
        folder = self.root / "Data" / "PaperDocuments"
        folder.mkdir(exist_ok=True)
        (folder / "index.json").write_text(
            json.dumps(rows, ensure_ascii=False), encoding="utf-8")
        return folder

    def test_missing_sources_are_not_created(self):
        missing = Path(self.tmp.name) / "does-not-exist"
        result = catalog.read_catalog(missing)
        self.assertEqual(result["total"], 0)
        self.assertIn("не знайдено", result["order_status"])
        self.assertIn("ще не створений", result["paper_status"])
        self.assertFalse(missing.exists())

    def test_search_and_pages_include_older_orders_without_database_changes(self):
        self.seed_orders(1050)
        before = self.db.read_bytes()
        result = catalog.read_catalog(self.root, page_size=100)
        self.assertEqual(result["total"], 1050)
        self.assertEqual(result["pages"], 11)
        last = catalog.read_catalog(self.root, page=10, page_size=100)
        self.assertEqual(len(last["rows"]), 50)
        found = catalog.read_catalog(self.root, "Тема 0001")
        self.assertEqual(found["total"], 1)
        self.assertEqual(found["rows"][0]["source_id"], 1)
        self.assertEqual(found["rows"][0]["file_state"], "Файл не прив'язаний")
        self.assertEqual(self.db.read_bytes(), before)
        self.assertFalse((self.root / "Data" / "PaperDocuments").exists())

    def test_sources_are_independent_and_known_missing_file_is_not_unknown_order(self):
        self.seed_orders(1)
        folder = self.paper_index([{
            "id": "old-paper", "date": "2026-11-09", "kind": "Інструктаж",
            "title": "Тема", "person": "Водій", "file": "missing.docx"
        }])
        result = catalog.read_catalog(self.root)
        self.assertEqual(result["total"], 2)
        paper = next(row for row in result["rows"] if row["source"] == "paper")
        self.assertEqual(paper["file_state"], "Файл не знайдено")
        (folder / "index.json").write_text("{", encoding="utf-8")
        result = catalog.read_catalog(self.root)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["rows"][0]["source"], "order")
        self.assertIn("Помилка каталогу", result["paper_status"])
        self.assertEqual((folder / "index.json").read_text(encoding="utf-8"), "{")

    def test_old_database_without_orders_is_not_migrated(self):
        con = sqlite3.connect(str(self.db))
        con.execute("CREATE TABLE previous_data(id INTEGER)")
        con.commit()
        con.close()
        before = self.db.read_bytes()
        folder = self.paper_index([{
            "id": "doc", "date": "2026-11-09", "kind": "Стажування",
            "title": "Зразок", "person": "Водій", "file": "example.docx"
        }])
        (folder / "example.docx").write_bytes(b"synthetic document")
        result = catalog.read_catalog(self.root)
        self.assertEqual(result["total"], 1)
        self.assertIn("Таблиці наказів", result["order_status"])
        self.assertEqual(result["rows"][0]["file_state"], "Файл доступний")
        self.assertEqual(self.db.read_bytes(), before)

    def test_unsafe_filename_is_shown_and_never_openable(self):
        self.paper_index([{
            "id": "doc", "date": "2026-11-09", "kind": "Інструктаж",
            "title": "Зразок", "file": "../outside.docx"
        }])
        result = catalog.read_catalog(self.root)
        self.assertEqual(result["total"], 1)
        self.assertIsNone(result["rows"][0]["file_path"])
        self.assertEqual(result["rows"][0]["file_state"], "Небезпечний шлях")
        self.assertIn("Проблемних", result["paper_status"])

    def test_catalog_survives_backup_and_restore_without_output(self):
        self.seed_orders(2)
        folder = self.paper_index([{
            "id": "doc", "date": "2026-11-09", "kind": "Інструктаж",
            "title": "Перевірка", "person": "Тест", "file": "example.docx"
        }])
        (folder / "example.docx").write_bytes(b"synthetic document")
        before = catalog.read_catalog(self.root)
        archive = workspace.create_workspace_backup_archive(
            self.root, Path(self.tmp.name) / "backup.zip", app_version="10.15-r5")
        restored = Path(self.tmp.name) / "restored"
        workspace.restore_workspace_backup_archive(archive, restored)
        after = catalog.read_catalog(restored)
        self.assertEqual(after["total"], before["total"])
        row = next(row for row in after["rows"] if row["source"] == "paper")
        self.assertEqual(row["file_state"], "Файл доступний")
        self.assertEqual(row["file_path"].read_bytes(), b"synthetic document")
        self.assertEqual(catalog.read_catalog(restored, "Тема 0001")["total"], 1)


class CombinedCatalogWindowTests(unittest.TestCase):
    def test_actual_window_opens_paper_and_invokes_order_callback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            data = root / "Data"
            data.mkdir(parents=True)
            db = data / "driver_worktime.sqlite3"
            con = sqlite3.connect(str(db))
            con.execute("CREATE TABLE operations_orders "
                        "(id INTEGER PRIMARY KEY, order_date TEXT, order_no TEXT, "
                        "order_type TEXT, subject TEXT)")
            con.execute("INSERT INTO operations_orders VALUES (3, '2026-11-10', "
                        "'3', 'work', 'Тестовий наказ')")
            con.commit()
            con.close()
            folder = data / "PaperDocuments"
            folder.mkdir()
            (folder / "a.docx").write_bytes(b"synthetic")
            (folder / "index.json").write_text(json.dumps([{
                "id": "a", "date": "2026-11-09", "kind": "Інструктаж",
                "title": "Тест", "file": "a.docx"
            }], ensure_ascii=False), encoding="utf-8")
            app = tk.Tk()
            app.geometry("900x600")
            opened = []
            app._taxo_preview_catalog_order = opened.append
            messages = SimpleNamespace(showinfo=lambda *a, **k: None,
                                       showerror=lambda *a, **k: self.fail(str(a)))
            core = SimpleNamespace(tk=tk, ttk=ttk, messagebox=messages)
            try:
                with mock.patch.object(catalog_ui.paperwork, "open_file") as open_file:
                    win = catalog_ui.open_document_catalog(app, core, root)
                    app.update()
                    tree = win._taxo_catalog_tree
                    self.assertEqual(len(tree.get_children()), 2)
                    for iid in tree.get_children():
                        tree.selection_set(iid)
                        win._taxo_catalog_open()
                    self.assertEqual(opened, [3])
                    open_file.assert_called_once_with(folder / "a.docx")
                    self.assertTrue(win.winfo_ismapped())
            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main()
