# -*- coding: utf-8 -*-
"""Strict live Tk checks for new document catalog routes (post-10.22).

These tests open the real catalog, not a synthetic button-only mock.
They are deliberately separate from the structural surface contracts.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
import gc
import time
import tkinter as tk
from tkinter import ttk

import document_catalog_ui
from document_library_collections import read_collection_state
from runtime_reachability import runtime_routes, activate_widget


def walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from walk(child)


def button(root, label):
    for child in walk(root):
        try:
            if child.winfo_class() in ("Button", "TButton") and str(child.cget("text")) == label:
                return child
        except Exception:
            pass
    return None


def library_selector(root):
    for child in walk(root):
        try:
            if child.winfo_class() == "TCombobox":
                values = tuple(str(v) for v in child.cget("values"))
                if "Мої папки" in values and "За видами" in values:
                    return child
        except Exception:
            pass
    return None


class NewDocumentLiveRouteTests(TestCase):
    def tearDown(self):
        # The catalog loads in a background thread; avoid finalizers leaking
        # across independent real-Tk tests (especially on macOS).
        end = time.monotonic() + 10
        while time.monotonic() < end:
            if document_catalog_ui._READER_SLOT.acquire(blocking=False):
                document_catalog_ui._READER_SLOT.release()
                gc.collect()
                return
            time.sleep(0.02)
        self.fail("Catalog reader did not become idle")

    def open_window(self, workspace):
        root = tk.Tk()
        root.geometry("1200x850")
        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: None,
                showerror=lambda *a, **k: self.fail("Catalog error: %s" % (a,)),
            ),
            simpledialog=SimpleNamespace(askstring=lambda *a, **k: "Тестова папка"),
        )
        win = document_catalog_ui.open_document_catalog(root, core, workspace)
        root.update()
        return root, win

    @runtime_routes("documents.catalog_filters")
    def test_real_catalog_filter_reset_is_visible_and_activatable(self):
        with TemporaryDirectory() as directory:
            root, win = self.open_window(Path(directory))
            try:
                search = win._taxo_catalog_search
                search.set("невідомий документ")
                root.update()
                reset = button(win, "Скинути фільтри")
                self.assertIsNotNone(reset, "Reset control disappeared")
                activate_widget(reset, "documents.catalog_filters", container=win)
                self.assertEqual(search.get(), "")
            finally:
                root.destroy()

    @runtime_routes("documents.catalog_folders")
    def test_real_catalog_my_folders_entry_creates_folder(self):
        with TemporaryDirectory() as directory:
            workspace = Path(directory)
            root, win = self.open_window(workspace)
            try:
                select = library_selector(win)
                self.assertIsNotNone(select, "Folder navigation disappeared")
                select.set("Мої папки")
                select.event_generate("<<ComboboxSelected>>")
                root.update()
                create = button(win, "Нова папка…")
                self.assertIsNotNone(create, "Create-folder control disappeared")
                activate_widget(create, "documents.catalog_folders", container=win)
                names = [x.name for x in read_collection_state(workspace).collections]
                self.assertIn("Тестова папка", names)
            finally:
                root.destroy()


if __name__ == "__main__":
    import unittest
    unittest.main()
