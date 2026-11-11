# -*- coding: utf-8 -*-
"""10.15-r3 — printable paper forms, catalog, and backup-safe location."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace
from unittest import mock
import unittest
import zipfile
from datetime import date
from pathlib import Path

import main
import safety_instructions_ui as brief
import paper_documents as paper
import workspace
import driver_internship_ui
from runtime_reachability import runtime_routes, assert_widget_reachable, activate_widget

ROOT = Path(__file__).resolve().parents[1]


class PaperDocumentsR3Tests(unittest.TestCase):
    def test_version_and_live_controls(self):
        self.assertIn(main.APP_VERSION, ("10.15-r3", "10.15-r4", "10.15-r5", "10.15-r7", "10.15-r8", "10.15-r9", "10.15-r10", "10.16-r1", "10.16-r2", "10.16-r3", "10.16-r4", "10.16-r5", "10.16-r6", "10.16-r7"))
        self.assertIn("Version: " + main.APP_VERSION, (ROOT / "VERSION.txt").read_text("utf-8"))
        start = (ROOT / "START.bat").read_text("utf-8")
        for filename in ("paper_documents.py", "paper_documents_ui.py", "driver_internship_ui.py"):
            self.assertIn(filename, start)
        instructions = (ROOT / "src/taxo/safety_instructions_ui.py").read_text("utf-8")
        self.assertIn("Створити комплект DOCX для друку", instructions)
        self.assertIn("Каталог документів…", instructions)
        operations = (ROOT / "src/taxo/operations_orders_ui.py").read_text("utf-8")
        self.assertIn("install_internship_tab(app, core, book)", operations)

    def test_briefing_complete_printable_material_preserves_people_and_text(self):
        prepared = brief.prepare_list(
            "БДР", "Передрейсовий (цільовий)", "09.11.2026",
            "Безпечний рух на маршруті",
            ["Водій Один", "Водій Два"],
            people_records=(
                {"id": 12, "name": "Водій Один", "personnel_no": "012"},
                {"id": 19, "name": "Водій Два", "personnel_no": "019"},
            ),
            program_text="1. Перевірити дорожні умови.\n2. Дотримуватися дистанції.",
            source_note="Наказ №975",
        )
        doc = paper.build_briefing_docx(prepared)
        self.assertEqual(len(doc.tables), 1)
        self.assertEqual(len(doc.tables[0].rows), 3)
        flattened = "\n".join(p.text for p in doc.paragraphs)
        self.assertIn("Перевірити дорожні умови", flattened)
        self.assertIn("ЛИСТ ОЗНАЙОМЛЕННЯ", flattened)
        tabletext = " ".join(cell.text for row in doc.tables[0].rows for cell in row.cells)
        self.assertIn("Водій Один", tabletext)
        self.assertIn("Водій Два", tabletext)
        self.assertIn("Підпис працівника", tabletext)
        self.assertNotIn("проведено", json.dumps(prepared, default=str).lower())
        with tempfile.TemporaryDirectory() as directory:
            first = paper.save_document(directory, doc, "Інструктаж", prepared["topic"],
                                        prepared["day"].isoformat(), "Водій Один, Водій Два")
            second = paper.save_document(directory, doc, "Інструктаж", prepared["topic"],
                                         prepared["day"].isoformat(), "Водій Один, Водій Два")
            self.assertNotEqual(first, second)
            self.assertTrue(first.is_file() and second.is_file())
            self.assertTrue(str(first).startswith(str(Path(directory) / "Data")))
            found = paper.list_documents(directory, "Безпечний")
            self.assertEqual(len(found), 2)
            self.assertFalse(any(row["paper_signed"] for row in found))
            self.assertEqual(paper.document_path(directory, found[0]), second)

    def test_internship_form_contains_regulatory_sections_without_auto_admission(self):
        doc = paper.build_training_docx({
            "driver": "Стажист Один", "instructor": "Наставник Два",
            "vehicle": "Автобус АА0000АА", "training_kind": "Контрольна поїздка",
            "hours": "", "order": "№17 від 09.11.2026",
        })
        text = "\n".join(p.text for p in doc.paragraphs)
        for section in paper.TRAINING_SECTIONS:
            self.assertIn(section, text)
        self.assertIn("Наставник Два", text)
        self.assertIn("Автобус АА0000АА", text)
        self.assertIn("Допустити / не допустити", text)
        self.assertEqual(len(doc.tables), 3)
        self.assertEqual(len(doc.tables[0].rows), 5)
        self.assertIn("Підпис інструктора", doc.tables[0].rows[0].cells[-1].text)
        with tempfile.TemporaryDirectory() as directory:
            target = paper.save_document(directory, doc, "Стажування", "Контрольна поїздка",
                                         date(2026, 11, 9).isoformat(), "Стажист Один")
            self.assertTrue(target.exists())
            rows = paper.list_documents(directory, "Стажист")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["kind"], "Стажування")

    def test_full_backup_contains_paper_documents_and_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "work"
            paths = workspace.ensure_workspace(root)
            con = sqlite3.connect(str(paths["main_db"]))
            try:
                con.execute("CREATE TABLE backup_smoke(id INTEGER PRIMARY KEY)")
                con.commit()
            finally:
                con.close()
            document = paper.build_training_docx({
                "driver": "Тест Стажист", "instructor": "Тест Наставник", "vehicle": "Автобус"
            })
            target = paper.save_document(root, document, "Стажування",
                "Лист стажування", "2026-11-09", "Тест Стажист")
            archive = workspace.create_workspace_backup_archive(
                root, Path(directory) / "backup.zip", app_version="10.15-r3")
            with zipfile.ZipFile(archive) as zf:
                names = set(zf.namelist())
                self.assertIn("Data/PaperDocuments/index.json", names)
                self.assertIn("Data/PaperDocuments/" + target.name, names)

    def test_catalog_blocks_path_traversal_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertRaises(ValueError, paper.document_path, directory,
                              {"file": "../secret.docx"})
            self.assertRaises(ValueError, paper.document_path, directory,
                              {"file": "/absolute.docx"})
            self.assertEqual(paper.list_documents(directory), [])



class _DummyCon:
    def close(self):
        pass


def _walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from _walk(child)


def _button(widget, label):
    for child in _walk(widget):
        if child.winfo_class() in ("TButton", "Button") and str(child.cget("text")) == label:
            return child
    return None


class PaperworkLiveRouteR3Tests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.geometry("1100x750")
        self.book = ttk.Notebook(self.root)
        self.book.pack(fill="both", expand=True)
        self.core = SimpleNamespace(
            tk=tk, ttk=ttk, db=lambda: _DummyCon(),
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: None,
                showerror=lambda *a, **k: self.fail("Unexpected UI error: %r" % (a,)),
            ),
        )

    def tearDown(self):
        self.root.destroy()

    @runtime_routes("operations.printable_briefing")
    def test_live_briefing_print_action_is_reachable_and_saves_file(self):
        with tempfile.TemporaryDirectory() as directory, \
             mock.patch.object(brief, "load_workspace_root", return_value=directory), \
             mock.patch.object(brief.instruction_documents, "open_briefing_document"), \
             mock.patch.object(brief.ops, "list_employee_choices", return_value=[
                 {"id": 1, "label": "Водій Один", "name": "Водій Один", "personnel_no": "001"},
                 {"id": 2, "label": "Водій Два", "name": "Водій Два", "personnel_no": "002"},
             ]):
            tab = brief.install_instruction_tab(SimpleNamespace(), self.core, self.book)
            self.book.select(tab)
            self.root.update()
            select_all = _button(tab, "Вибрати всіх")
            select_all.invoke()
            control = _button(tab, "Створити комплект DOCX для друку")
            self.root.geometry("940x600")
            self.root.update()
            assert_widget_reachable(control, "operations.printable_briefing")
            activate_widget(control, "operations.printable_briefing")
            entries = paper.list_documents(directory)
            self.assertEqual(len(entries), 1)
            self.assertTrue(paper.document_path(directory, entries[0]).is_file())

    @runtime_routes("operations.driver_internship")
    def test_live_driver_internship_action_is_reachable_and_saves_file(self):
        with tempfile.TemporaryDirectory() as directory, \
             mock.patch.object(driver_internship_ui, "load_workspace_root", return_value=directory), \
             mock.patch.object(driver_internship_ui.internship_documents, "open_internship_document"), \
             mock.patch.object(driver_internship_ui.ops, "list_driver_choices", return_value=[
                 {"id": 1, "label": "Стажист Один", "name": "Стажист Один", "personnel_no": "001"},
                 {"id": 2, "label": "Наставник Два", "name": "Наставник Два", "personnel_no": "002"},
             ]), \
             mock.patch.object(driver_internship_ui.ops, "list_vehicle_choices", return_value=[
                 {"id": 5, "label": "Автобус AA0000AA"},
             ]):
            tab = driver_internship_ui.install_internship_tab(
                SimpleNamespace(), self.core, self.book)
            self.book.select(tab)
            self.root.update()
            controls = {
                int(widget.grid_info().get("row")): widget
                for widget in tab.winfo_children()
                if isinstance(widget, ttk.Combobox)
            }
            controls[2].set("Стажист Один")
            controls[3].set("Наставник Два")
            controls[4].set("Автобус AA0000AA")
            control = _button(tab, "Створити лист стажування DOCX")
            self.root.geometry("940x600")
            self.root.update()
            assert_widget_reachable(control, "operations.driver_internship")
            activate_widget(control, "operations.driver_internship")
            entries = paper.list_documents(directory)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["kind"], "Стажування")


if __name__ == "__main__":
    unittest.main()
