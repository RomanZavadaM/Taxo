# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import unittest
from types import SimpleNamespace
from unittest import mock

import function_registry
import main
import personnel_data_center_r6


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


class _DummyCon:
    def close(self):
        pass


class _DataCenterHost(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.calls = []
        self.personnel_overview_page = ttk.Frame(self)
        self.personnel_overview_page.pack(fill="both", expand=True)
        bar = ttk.Frame(self.personnel_overview_page)
        bar.pack(fill="x")
        ttk.Button(
            bar,
            text="Дані / Дія / документи…",
            command=lambda: None,
        ).pack(side="right")

    def title(self, *_args):
        return "Taxo test"

    def import_personnel_registry_xlsx(self):
        self.calls.append("import")

    def open_employee_military_working_data(self):
        self.calls.append("working-data")

    def open_personnel_data_center(self):
        self.calls.append("card-documents")

    def open_employee_document_register(self):
        self.calls.append("document-register")

    def open_required_employee_documents_r7(self):
        self.calls.append("document-control")

    def open_diia_reconciliation_cycle(self):
        self.calls.append("diia")

    def open_military_accounting_overview(self):
        self.calls.append("military")


class PersonnelDataCenterActionsR6Tests(unittest.TestCase):
    def test_r6_identity_is_historical_anchor(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION), (10, 12, 6))

    def test_registry_marks_all_primary_data_center_actions_for_runtime_smoke(self):
        routes = {route.function_id: route for route in function_registry.FUNCTION_ROUTES}
        expected = (
            "personnel.registry_import",
            "personnel.registry_bulk",
            "personnel.working_data",
            "personnel.card_documents",
            "personnel.document_register",
            "personnel.document_control",
            "personnel.diia_cycle",
            "personnel.military",
        )
        for function_id in expected:
            self.assertIn(function_id, routes)
            self.assertTrue(routes[function_id].runtime_smoke, function_id)

    def test_all_primary_data_center_actions_are_visible_and_invoke_expected_route(self):
        core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            APP_VERSION="10.12-r6",
            db=lambda: _DummyCon(),
        )

        with mock.patch.object(personnel_data_center_r6, "_latest_imports", lambda _con: {}), \
             mock.patch.object(personnel_data_center_r6, "_selected_employee_id", lambda _app: None):
            App = personnel_data_center_r6.install(core, _DataCenterHost)
            App.open_personnel_registry_bulk_actions_r6 = lambda self: self.calls.append("bulk")
            root = tk.Tk()
            root.geometry("1160x820")
            app = App(root)
            app.pack(fill="both", expand=True)
            app.open_personnel_data_center_r6()

        try:
            root.update()
            win = app._personnel_data_center_r6_window
            labels = (
                ("Завантажити XLSX / звірити…", "import"),
                ("Масові дії з останнього імпорту…", "bulk"),
                ("Робочі дані з реєстрів", "working-data"),
                ("Картка та документи", "card-documents"),
                ("Відкрити реєстр документів", "document-register"),
                ("Контроль обов'язкових документів…", "document-control"),
                ("Офіційний цикл Дії…", "diia"),
                ("Військовий облік / строки…", "military"),
            )
            for label, expected_call in labels:
                button = button_by_text(win, label)
                self.assertIsNotNone(button, label)
                self.assertTrue(button.winfo_ismapped(), label)
                button.invoke()
                self.assertEqual(app.calls[-1], expected_call)
            self.assertEqual(
                app.calls,
                [expected for _label, expected in labels],
            )
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
