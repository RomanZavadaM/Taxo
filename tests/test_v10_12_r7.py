# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import unittest
from types import SimpleNamespace

import function_registry
import main
import v10710_features as document_center


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


class _Messages:
    @staticmethod
    def showinfo(*_args, **_kwargs):
        return None


class _App:
    def __init__(self):
        self.calls = []

    def show_waybills_for_schedule(self):
        self.calls.append("waybills")

    def vehicle_document_control(self):
        self.calls.append("vehicle-docs")

    def open_military_transport_statement(self):
        self.calls.append("military-statement")

    def show_employee_registry(self):
        self.calls.append("employees")


class DocumentCenterReachabilityR7Tests(unittest.TestCase):
    def test_r7_identity_is_historical_anchor(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION), (10, 12, 7))

    def test_registry_requires_document_center_runtime_smoke(self):
        routes = {route.function_id: route for route in function_registry.FUNCTION_ROUTES}
        self.assertIn("documents.center", routes)
        self.assertTrue(routes["documents.center"].runtime_smoke)

    def test_document_center_actions_are_visible_and_invokable(self):
        root = tk.Tk()
        root.geometry("1050x760")
        win = tk.Toplevel(root)
        win.geometry("1000x700")
        book = ttk.Notebook(win)
        book.pack(fill="both", expand=True)
        for title in ("Накази", "Закріплення водіїв", "Відповідальні", "Каталог наказів"):
            tab = ttk.Frame(book)
            book.add(tab, text=title)

        app = _App()
        core = SimpleNamespace(ttk=ttk, messagebox=_Messages)

        try:
            document_center._install_document_tab(app, core, win)
            root.update()

            docs_tab = None
            for tab_id in book.tabs():
                if str(book.tab(tab_id, "text")) == "Документи":
                    docs_tab = tab_id
                    break
            self.assertIsNotNone(docs_tab)
            book.select(docs_tab)
            root.update()

            actions = (
                ("Шляхові листи на день", "waybills"),
                ("Контроль документів ТЗ", "vehicle-docs"),
                ("Відомість ТЦК — транспорт підприємства", "military-statement"),
                ("Реєстр усіх працівників", "employees"),
            )
            for label, expected in actions:
                button = button_by_text(win, label)
                self.assertIsNotNone(button, label)
                self.assertTrue(button.winfo_ismapped(), label)
                button.invoke()
                self.assertEqual(app.calls[-1], expected)

            self.assertEqual(
                app.calls,
                ["waybills", "vehicle-docs", "military-statement", "employees"],
            )

            internal = (
                ("Реєстр наказів", "Накази"),
                ("Закріплення водіїв", "Закріплення водіїв"),
                ("Відповідальні особи", "Відповідальні"),
                ("Каталог типів наказів", "Каталог наказів"),
            )
            for label, expected_tab in internal:
                book.select(docs_tab)
                root.update()
                button = button_by_text(win, label)
                self.assertIsNotNone(button, label)
                self.assertTrue(button.winfo_ismapped(), label)
                button.invoke()
                root.update()
                current = book.select()
                self.assertEqual(str(book.tab(current, "text")), expected_tab)

            before = len([tab for tab in book.tabs() if str(book.tab(tab, "text")) == "Документи"])
            document_center._install_document_tab(app, core, win)
            after = len([tab for tab in book.tabs() if str(book.tab(tab, "text")) == "Документи"])
            self.assertEqual(before, 1)
            self.assertEqual(after, 1)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
