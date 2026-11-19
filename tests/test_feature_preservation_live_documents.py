# -*- coding: utf-8 -*-
"""Strict live Tk checks for new document catalog routes (post-10.22).

These tests open the real catalog, not a synthetic button-only mock.
They are deliberately separate from the structural surface contracts.
"""
from pathlib import Path
import ast
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
import gc
import time
import tkinter as tk
from tkinter import ttk

import document_catalog_ui
from document_library_collections import read_collection_state
from runtime_reachability import (
    runtime_routes, activate_widget, assert_widget_reachable, mark_activation
)


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

    def close_window(self, root):
        # Allow any outstanding catalog read and queued Tk callbacks to
        # finish on the GUI thread before destroying the interpreter.
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            root.update()
            if document_catalog_ui._READER_SLOT.acquire(blocking=False):
                document_catalog_ui._READER_SLOT.release()
                break
            time.sleep(0.02)
        root.update()
        root.destroy()
        # Python 3.8/Tk on Windows 7 must finalize Tcl variables on the
        # thread that owned the GUI, not later inside the catalog reader.
        gc.collect()

    def test_background_catalog_reader_never_captures_tk_state(self):
        # Guard against Win7 Tcl_AsyncDelete: a worker must not own the
        # whole state dictionary with Tk variables and widget callbacks.
        code = Path(document_catalog_ui.__file__).read_text(encoding="utf-8")
        tree = ast.parse(code)
        readers = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "worker"
            and any(
                isinstance(child, ast.Call)
                and isinstance(child.func, ast.Attribute)
                and child.func.attr == "paginate_sources"
                for child in ast.walk(node)
            )
        ]
        self.assertEqual(len(readers), 1)
        used = {
            name.id for name in ast.walk(readers[0])
            if isinstance(name, ast.Name) and isinstance(name.ctx, ast.Load)
        }
        self.assertNotIn(
            "state", used,
            "Catalog reader captures Tk-bearing state: unsafe on Win7"
        )

    @runtime_routes(
        "documents.catalog_filters",
        "documents.catalog_folders",
        "documents.catalog_tree_modes",
    )
    def test_real_document_catalog_controls_and_persistence(self):
        # One real Tk interpreter covers all three routes. This prevents
        # multiple Tcl interpreter teardowns in the Win7 Python 3.8 suite.
        with TemporaryDirectory() as directory:
            workspace = Path(directory)
            data = workspace / "Data" / "PaperDocuments"
            data.mkdir(parents=True)
            (data / "example.docx").write_bytes(b"test")
            (data / "index.json").write_text(
                '[{"id":"doc-1","date":"2026-11-18","kind":"Інструкція",'
                '"title":"Перевірка дерева","file":"example.docx"}]',
                encoding="utf-8",
            )
            from document_library_collections import create_collection
            create_collection(workspace, "Моя перевірочна папка")
            root, win = self.open_window(workspace)
            try:
                search = win._taxo_catalog_search
                search.set("невідомий документ")
                root.update()
                reset = button(win, "Скинути фільтри")
                self.assertIsNotNone(reset, "Reset control disappeared")
                activate_widget(reset, "documents.catalog_filters", container=win)
                self.assertEqual(search.get(), "")

                selector = library_selector(win)
                self.assertIsNotNone(selector, "Document tree selector missing")
                assert_widget_reachable(
                    selector, "documents.catalog_tree_modes", container=win
                )
                tree = win._taxo_library_tree

                def switch_and_find(mode, expected):
                    selector.set(mode)
                    selector.event_generate("<<ComboboxSelected>>")
                    deadline = time.monotonic() + 10
                    while time.monotonic() < deadline:
                        root.update()
                        labels = [
                            str(tree.item(item, "text"))
                            for parent in ("",) + tuple(tree.get_children())
                            for item in tree.get_children(parent)
                        ]
                        if any(expected in label for label in labels):
                            return
                        time.sleep(0.02)
                    self.fail(
                        "Document tree mode %s did not show %s" % (mode, expected)
                    )

                switch_and_find("Мої папки", "Моя перевірочна папка")
                create = button(win, "Нова папка…")
                self.assertIsNotNone(create, "Create-folder control disappeared")
                activate_widget(create, "documents.catalog_folders", container=win)
                names = [x.name for x in read_collection_state(workspace).collections]
                self.assertIn("Тестова папка", names)

                switch_and_find("За видами", "Інструкція")
                switch_and_find("За датами", "2026")
                mark_activation("documents.catalog_tree_modes")
            finally:
                self.close_window(root)


if __name__ == "__main__":
    import unittest
    unittest.main()
