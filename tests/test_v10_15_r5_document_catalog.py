# -*- coding: utf-8 -*-
"""Read-only combined catalog of existing orders and paper documents."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import time
import threading
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

    def test_newest_paper_and_numeric_order_ids_are_first(self):
        self.seed_orders(120)
        folder = self.paper_index([{
            "id": "%04d" % (120 - i), "date": "2026-11-09",
            "created_at": "2026-11-10T%02d:%02d:00+00:00" % (i // 60, i % 60),
            "kind": "Інструктаж", "title": "Документ %d" % i, "file": "a.docx"
        } for i in range(120)])
        (folder / "a.docx").write_bytes(b"synthetic")
        rows = catalog.read_catalog(self.root, "Документ", page_size=100)["rows"]
        self.assertEqual(rows[0]["title"], "Документ 119")
        self.assertEqual(len(rows), 100)
        order_rows = catalog.read_catalog(self.root, "Тема", page_size=100)["rows"]
        self.assertEqual([row["source_id"] for row in order_rows[:3]], [120, 119, 118])

    def test_paper_only_mode_keeps_newly_created_backdated_document_first(self):
        self.seed_orders(1)
        folder = self.paper_index([
            {"id": "one", "date": "2026-11-10", "created_at": "2026-11-10T08:00:00+00:00",
             "kind": "Інструктаж", "title": "Раніше створений", "file": "a.docx"},
            {"id": "two", "date": "2026-01-01", "created_at": "2026-11-10T09:00:00+00:00",
             "kind": "Інструктаж", "title": "Щойно створений за минулий період", "file": "a.docx"},
        ])
        (folder / "a.docx").write_bytes(b"synthetic")
        snapshot = catalog.read_sources(self.root)
        result = catalog.paginate_sources(snapshot, source_filter="paper")
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["rows"][0]["source_id"], "two")

    def test_mixed_sources_sort_by_document_date_not_incompatible_timezones(self):
        self.seed_orders(1)
        folder = self.paper_index([{
            "id": "doc", "date": "2026-11-10",
            "created_at": "2026-11-10T00:01:00+00:00",
            "kind": "Інструктаж", "title": "Час UTC", "file": "a.docx"
        }])
        (folder / "a.docx").write_bytes(b"synthetic")
        con = sqlite3.connect(str(self.db))
        con.execute("ALTER TABLE operations_orders ADD COLUMN created_at TEXT")
        con.execute("UPDATE operations_orders SET created_at='2026-11-10T23:59:00'")
        con.commit()
        con.close()
        rows = catalog.read_catalog(self.root)["rows"]
        # Same document date: group sources instead of comparing UTC and
        # timezone-free historical timestamps as if they used the same zone.
        self.assertEqual([row["source"] for row in rows], ["paper", "order"])

    def test_uri_handles_local_and_unc_without_authority(self):
        self.assertEqual(catalog._readonly_sqlite_uri("file:///C:/Taxo/a%20b.db"),
                         "file:///C:/Taxo/a%20b.db?mode=ro")
        self.assertEqual(catalog._readonly_sqlite_uri("file://server/share/a%20b.db"),
                         "file:////server/share/a%20b.db?mode=ro")

    def test_committed_wal_is_read_without_uncommitted_rows(self):
        writer = sqlite3.connect(str(self.db))
        try:
            writer.execute("PRAGMA journal_mode=WAL")
            writer.execute("PRAGMA wal_autocheckpoint=0")
            writer.execute("CREATE TABLE operations_orders "
                           "(id INTEGER PRIMARY KEY, order_date TEXT, order_no TEXT, "
                           "order_type TEXT, subject TEXT)")
            writer.commit()
            writer.execute("INSERT INTO operations_orders VALUES "
                           "(1, '2026-11-10', '1', 'work', 'Підтверджений')")
            writer.commit()
            writer.execute("INSERT INTO operations_orders VALUES "
                           "(2, '2026-11-10', '2', 'work', 'Не підтверджений')")
            result = catalog.read_catalog(self.root)
            self.assertEqual(result["total"], 1)
            self.assertEqual(result["rows"][0]["source_id"], 1)
            self.assertEqual(writer.execute("SELECT COUNT(*) FROM operations_orders").fetchone()[0], 2)
            writer.rollback()
            self.assertEqual(writer.execute("SELECT COUNT(*) FROM operations_orders").fetchone()[0], 1)
        finally:
            writer.close()

    def test_catalog_directory_symlink_outside_workspace_is_reported(self):
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (outside / "index.json").write_text("[]", encoding="utf-8")
        link = self.root / "Data" / "PaperDocuments"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Directory symlink is unavailable on this runner")
        result = catalog.read_catalog(self.root)
        self.assertIn("Помилка каталогу", result["paper_status"])
        self.assertEqual(result["total"], 0)

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
                    tree = win._taxo_catalog_tree
                    deadline = time.monotonic() + 10
                    while len(tree.get_children()) != 2 and time.monotonic() < deadline:
                        app.update()
                        time.sleep(0.02)
                    self.assertEqual(len(tree.get_children()), 2)
                    for iid in tree.get_children():
                        tree.selection_set(iid)
                        win._taxo_catalog_open()
                    self.assertEqual(opened, [3])
                    open_file.assert_called_once_with(folder / "a.docx")
                    self.assertTrue(win.winfo_ismapped())
                    # A new search rereads a document created while the window is open.
                    (folder / "index.json").write_text(json.dumps([{
                        "id": "b", "date": "2026-11-10", "kind": "Інструктаж",
                        "title": "Новий запис", "file": "a.docx"
                    }], ensure_ascii=False), encoding="utf-8")
                    win._taxo_catalog_search.set("Новий запис")
                    deadline = time.monotonic() + 10
                    while time.monotonic() < deadline:
                        app.update()
                        ids = tree.get_children()
                        if len(ids) == 1 and "Новий запис" in str(tree.item(ids[0], "values")):
                            break
                        time.sleep(0.02)
                    self.assertEqual(len(tree.get_children()), 1)
                    self.assertIn("Новий запис", str(tree.item(tree.get_children()[0], "values")))
            finally:
                app.destroy()


    def test_slow_source_does_not_block_window_event_loop(self):
        app = tk.Tk()
        app.geometry("900x600")
        entered, release = threading.Event(), threading.Event()
        messages = SimpleNamespace(showinfo=lambda *a, **k: None,
                                   showerror=lambda *a, **k: self.fail(str(a)))
        core = SimpleNamespace(tk=tk, ttk=ttk, messagebox=messages)
        def slow_reader(_root):
            entered.set()
            release.wait(5)
            return {"rows": [], "paper_status": "OK", "order_status": "OK"}
        try:
            with mock.patch.object(catalog, "read_sources", side_effect=slow_reader):
                win = catalog_ui.open_document_catalog(app, core, ".")
                deadline = time.monotonic() + 3
                while not entered.is_set() and time.monotonic() < deadline:
                    app.update()
                    time.sleep(0.01)
                self.assertTrue(entered.is_set())
                app.update()
                self.assertTrue(win.winfo_ismapped())
                self.assertTrue(win.winfo_exists())
                release.set()
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    app.update()
                    time.sleep(0.02)
                    if not win._taxo_catalog_tree.get_children():
                        break
        finally:
            release.set()
            app.destroy()


    def test_replacing_catalog_directory_after_loading_cannot_open_external_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            folder = root / "Data" / "PaperDocuments"
            folder.mkdir(parents=True)
            (folder / "a.docx").write_bytes(b"internal")
            (folder / "index.json").write_text(json.dumps([{
                "id": "a", "date": "2026-11-09", "kind": "Інструктаж",
                "title": "Тест", "file": "a.docx"
            }], ensure_ascii=False), encoding="utf-8")
            outside = Path(tmp) / "outside"
            outside.mkdir()
            (outside / "a.docx").write_bytes(b"external")
            app = tk.Tk()
            errors = []
            messages = SimpleNamespace(showinfo=lambda *a, **k: None,
                                       showerror=lambda *a, **k: errors.append(a))
            core = SimpleNamespace(tk=tk, ttk=ttk, messagebox=messages)
            link = None
            try:
                with mock.patch.object(catalog_ui.paperwork, "open_file") as open_file:
                    win = catalog_ui.open_document_catalog(app, core, root)
                    tree = win._taxo_catalog_tree
                    deadline = time.monotonic() + 10
                    while not tree.get_children() and time.monotonic() < deadline:
                        app.update()
                        time.sleep(0.02)
                    self.assertEqual(len(tree.get_children()), 1)
                    folder.rename(root / "Data" / "PaperDocuments-original")
                    try:
                        folder.symlink_to(outside, target_is_directory=True)
                    except (OSError, NotImplementedError):
                        self.skipTest("Directory symlink is unavailable on this runner")
                    link = folder
                    tree.selection_set(tree.get_children()[0])
                    win._taxo_catalog_open()
                    self.assertTrue(errors)
                    open_file.assert_not_called()
            finally:
                app.destroy()
                if link is not None and link.is_symlink():
                    link.unlink()

    def test_closing_window_during_slow_read_cancels_ui_callbacks(self):
        app = tk.Tk()
        entered, release = threading.Event(), threading.Event()
        failures = []
        app.report_callback_exception = lambda *args: failures.append(args)
        messages = SimpleNamespace(showinfo=lambda *a, **k: None,
                                   showerror=lambda *a, **k: failures.append(a))
        core = SimpleNamespace(tk=tk, ttk=ttk, messagebox=messages)
        def slow_reader(_root):
            entered.set()
            release.wait(5)
            return {"rows": [], "paper_status": "OK", "order_status": "OK"}
        try:
            with mock.patch.object(catalog, "read_sources", side_effect=slow_reader):
                win = catalog_ui.open_document_catalog(app, core, ".")
                deadline = time.monotonic() + 3
                while not entered.is_set() and time.monotonic() < deadline:
                    app.update()
                    time.sleep(0.01)
                self.assertTrue(entered.is_set())
                win.destroy()
                release.set()
                deadline = time.monotonic() + 0.5
                while time.monotonic() < deadline:
                    app.update()
                    time.sleep(0.02)
                self.assertEqual(failures, [])
        finally:
            release.set()
            app.destroy()


    def test_page_change_does_not_cancel_pending_source_refresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            folder = root / "Data" / "PaperDocuments"
            folder.mkdir(parents=True)
            index = folder / "index.json"
            (folder / "a.docx").write_bytes(b"synthetic")
            def write_records(count):
                index.write_text(json.dumps([{
                    "id": str(i), "date": "2026-11-%02d" % (i + 1),
                    "kind": "Інструктаж", "title": "Запис %d" % i, "file": "a.docx"
                } for i in range(count)], ensure_ascii=False), encoding="utf-8")
            write_records(1)
            app = tk.Tk()
            messages = SimpleNamespace(showinfo=lambda *a, **k: None,
                                       showerror=lambda *a, **k: self.fail(str(a)))
            core = SimpleNamespace(tk=tk, ttk=ttk, messagebox=messages)
            started, release = threading.Event(), threading.Event()
            original = catalog.read_sources
            calls = []
            def gated_reader(path):
                calls.append(1)
                if len(calls) == 2:
                    started.set()
                    release.wait(5)
                return original(path)
            def find_button(parent, label):
                for child in parent.winfo_children():
                    if isinstance(child, ttk.Button) and child.cget("text") == label:
                        return child
                    result = find_button(child, label)
                    if result is not None:
                        return result
                return None
            try:
                with mock.patch.object(catalog, "read_sources", side_effect=gated_reader):
                    win = catalog_ui.open_document_catalog(app, core, root)
                    tree = win._taxo_catalog_tree
                    deadline = time.monotonic() + 10
                    while len(tree.get_children()) != 1 and time.monotonic() < deadline:
                        app.update()
                        time.sleep(0.02)
                    self.assertEqual(len(tree.get_children()), 1)
                    write_records(2)
                    find_button(win, "Оновити").invoke()
                    deadline = time.monotonic() + 3
                    while not started.is_set() and time.monotonic() < deadline:
                        app.update()
                        time.sleep(0.01)
                    self.assertTrue(started.is_set())
                    find_button(win, "Наступна").invoke()
                    release.set()
                    deadline = time.monotonic() + 10
                    while len(tree.get_children()) != 2 and time.monotonic() < deadline:
                        app.update()
                        time.sleep(0.02)
                    self.assertEqual(len(tree.get_children()), 2)
            finally:
                release.set()
                app.destroy()


if __name__ == "__main__":
    unittest.main()
