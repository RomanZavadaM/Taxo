# -*- coding: utf-8 -*-
"""10.17-r5: tachograph child-window navigation and interval data safety."""
from __future__ import annotations

import inspect
import tkinter as tk
from tkinter import ttk
import unittest
from pathlib import Path
from unittest import mock

import main
import tachograph

ROOT = Path(__file__).resolve().parents[1]


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


def toplevel_by_title(root, title):
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and str(widget.title()) == title:
            return widget
    return None


class _RecordingConnection:
    def __init__(self):
        self.executed = []
        self.commits = 0
        self.closed = 0

    def execute(self, sql, args=()):
        self.executed.append((str(sql), tuple(args)))
        return self

    def commit(self):
        self.commits += 1

    def close(self):
        self.closed += 1


class TachographDialogCancellationR5Tests(unittest.TestCase):
    def test_revision_identity(self):
        self.assertEqual(main.APP_VERSION, "10.17-r5")
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: 10.17-r5\n",
        )
        self.assertIn(
            "Taxo 10.17-r5",
            (ROOT / "START.bat").read_text("utf-8"),
        )

    def test_manual_time_parser_rejects_values_outside_one_day(self):
        self.assertEqual(tachograph.TachographModule.parse("00:00"), 0)
        self.assertEqual(tachograph.TachographModule.parse("23:59"), 1439)
        for value in ("24:00", "23:60", "99:99", "-1:00", "abc", "12"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    tachograph.TachographModule.parse(value)

    def test_interval_form_has_separate_cancel_and_save_actions(self):
        source = inspect.getsource(tachograph.TachographModule.interval_form)
        self.assertIn('text="Скасувати",command=w.destroy', source)
        self.assertIn('text="Зберегти",command=save', source)
        self.assertNotIn('text="Скасувати",command=save', source)
        self.assertNotIn("WM_DELETE_WINDOW", source)
        self.assertIn("except ValueError:", source)
        self.assertIn("00:00 до 23:59", source)

        save_body = source.split("def save():", 1)[1]
        self.assertIn("UPDATE intervals SET", save_body)
        self.assertIn("INSERT INTO intervals", save_body)
        self.assertIn("con.commit()", save_body)
        self.assertIn("self.load_intervals()", save_body)

    def test_cancel_x_invalid_save_and_reopen_do_not_write_unexpectedly(self):
        root = tk.Tk()
        root.withdraw()
        connection = _RecordingConnection()
        module = object.__new__(tachograph.TachographModule)
        module.parent = root
        module.current_id = 7
        load_calls = []
        module.load_intervals = lambda: load_calls.append(True)

        try:
            with mock.patch.object(tachograph, "tdb", return_value=connection), \
                 mock.patch.object(tachograph.messagebox, "showerror") as showerror:
                # Cancel after editing: discard UI values, no DB write, release modal grab.
                module.interval_form()
                root.update_idletasks()
                root.update()
                dialog = toplevel_by_title(root, "Інтервал шайби")
                self.assertIsNotNone(dialog)
                self.assertEqual(root.grab_current(), dialog)
                entries = [w for w in walk(dialog) if str(w.winfo_class()) == "TEntry"]
                self.assertGreaterEqual(len(entries), 2)
                entries[0].delete(0, "end")
                entries[0].insert(0, "09:15")
                cancel = button_by_text(dialog, "Скасувати")
                self.assertIsNotNone(cancel)
                cancel.invoke()
                root.update()
                self.assertIsNone(toplevel_by_title(root, "Інтервал шайби"))
                self.assertIsNone(root.grab_current())
                self.assertEqual(connection.executed, [])
                self.assertEqual(connection.commits, 0)
                self.assertEqual(load_calls, [])

                # Reopen works. Default WM close destroys the dialog and still writes nothing.
                module.interval_form()
                root.update()
                dialog = toplevel_by_title(root, "Інтервал шайби")
                self.assertIsNotNone(dialog)
                self.assertEqual(root.grab_current(), dialog)
                self.assertEqual(dialog.protocol("WM_DELETE_WINDOW"), "")
                entries = [w for w in walk(dialog) if str(w.winfo_class()) == "TEntry"]
                entries[0].delete(0, "end")
                entries[0].insert(0, "10:30")
                dialog.destroy()
                root.update()
                self.assertIsNone(root.grab_current())
                self.assertEqual(connection.executed, [])
                self.assertEqual(connection.commits, 0)

                # Invalid time stays open and is rejected before any SQL.
                module.interval_form()
                root.update()
                dialog = toplevel_by_title(root, "Інтервал шайби")
                entries = [w for w in walk(dialog) if str(w.winfo_class()) == "TEntry"]
                entries[0].delete(0, "end")
                entries[0].insert(0, "99:99")
                save = button_by_text(dialog, "Зберегти")
                self.assertIsNotNone(save)
                save.invoke()
                root.update()
                self.assertIsNotNone(toplevel_by_title(root, "Інтервал шайби"))
                self.assertEqual(connection.executed, [])
                self.assertEqual(connection.commits, 0)
                showerror.assert_called()
                button_by_text(dialog, "Скасувати").invoke()
                root.update()

                # Explicit valid Save writes once, commits, refreshes, closes and releases grab.
                module.interval_form()
                root.update()
                dialog = toplevel_by_title(root, "Інтервал шайби")
                save = button_by_text(dialog, "Зберегти")
                save.invoke()
                root.update()
                self.assertTrue(any("INSERT INTO intervals" in sql for sql, _ in connection.executed))
                self.assertEqual(connection.commits, 1)
                self.assertEqual(len(load_calls), 1)
                self.assertIsNone(toplevel_by_title(root, "Інтервал шайби"))
                self.assertIsNone(root.grab_current())
        finally:
            root.destroy()

    def test_stats_window_closes_and_reopens_without_state_write(self):
        root = tk.Tk()
        root.withdraw()
        module = object.__new__(tachograph.TachographModule)
        module.parent = root
        module.update_stats = lambda: "Тестова статистика"

        try:
            module.show_stats_popup()
            root.update()
            first = toplevel_by_title(root, "Підсумкова статистика тахокарти")
            self.assertIsNotNone(first)
            close = button_by_text(first, "Закрити")
            self.assertIsNotNone(close)
            close.invoke()
            root.update()
            self.assertIsNone(toplevel_by_title(root, "Підсумкова статистика тахокарти"))

            module.show_stats_popup()
            root.update()
            second = toplevel_by_title(root, "Підсумкова статистика тахокарти")
            self.assertIsNotNone(second)
            second.destroy()
            root.update()
        finally:
            root.destroy()

    def test_other_tachograph_toplevels_already_have_close_actions(self):
        for method_name in (
            "show_stats_popup",
            "open_scan",
            "show_control_protocols",
        ):
            with self.subTest(method=method_name):
                source = inspect.getsource(
                    getattr(tachograph.TachographModule, method_name)
                )
                self.assertIn('text="Закрити"', source)
                self.assertIn("command=win.destroy", source)


if __name__ == "__main__":
    unittest.main()
