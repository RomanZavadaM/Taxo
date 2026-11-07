# -*- coding: utf-8 -*-
"""10.13-r3: paper-first instruction preparation, no real user data."""
import csv
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace
import unittest
from unittest import mock

import main
import operations_orders_ui
import safety_instructions_ui as brief


def walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from walk(child)


class _DummyCursor(list):
    def fetchone(self):
        return self[0] if self else None

    def fetchall(self):
        return list(self)


class _DummyConnection:
    def execute(self, _sql, _args=()):
        return _DummyCursor()

    def close(self):
        pass


class _AppHarness(tk.Tk):
    def __init__(self):
        super().__init__()
        self._operations_center_window = None

    def _company_name_value(self):
        return "Ізольований тест"


class InstructionJournalsR3Tests(unittest.TestCase):
    def test_r3_identity_is_historical_anchor(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION), (10, 13, 3))
        self.assertIn("Version:", Path("VERSION.txt").read_text(encoding="utf-8"))
        self.assertIn("Taxo 10.13-", Path("START.bat").read_text(encoding="utf-8"))

    def test_calendar_quarter_is_only_an_organizational_period(self):
        self.assertEqual(brief.quarter_for(date(2026, 12, 31)), (2026, 4))
        self.assertEqual(brief.shift_quarter(2026, 4, 1), (2027, 1))
        self.assertEqual(brief.shift_quarter(2027, 1, -1), (2026, 4))
        self.assertEqual(brief.quarter_caption(2027, 1), "1 квартал 2027 року")

    def test_no_auto_attendance_and_unplanned_requires_reason(self):
        with self.assertRaisesRegex(ValueError, "підстава"):
            brief.prepare_list(
                "БДР", "Позаплановий (спеціальний)", "07.11.2026",
                "Безпечний маршрут", ["Перший Працівник"]
            )
        prepared = brief.prepare_list(
            "БДР", "Позаплановий (спеціальний)", "07.11.2026",
            "Зміна дорожніх умов", ["Перший Працівник", "Перший Працівник"],
            reason="Небезпечна ділянка маршруту",
        )
        self.assertEqual(prepared["reason"], "Небезпечна ділянка маршруту")
        self.assertEqual(prepared["people"], ("Перший Працівник",))
        self.assertNotIn("conducted", prepared)
        self.assertNotIn("signed", prepared)

    def test_required_fields_and_separate_types(self):
        self.assertNotEqual(brief.BRIEFING_KINDS["БДР"], brief.BRIEFING_KINDS["Охорона праці"])
        with self.assertRaises(ValueError):
            brief.prepare_list("Охорона праці", "Повторний", "32.11.2026", "Тема", ["Один"])
        with self.assertRaisesRegex(ValueError, "працівника"):
            brief.prepare_list("Охорона праці", "Повторний", "07.11.2026", "Тема", [])
        with self.assertRaisesRegex(ValueError, "тему"):
            brief.prepare_list("Охорона праці", "Повторний", "07.11.2026", "", ["Один"])

    def test_export_is_draft_list_and_does_not_overwrite(self):
        prepared = brief.prepare_list(
            "Охорона праці", "Повторний", "07.11.2026",
            "Інструкція з ОП №2", ["Працівник один", "Працівник два"]
        )
        self.assertIn("ОП", brief.preparation_filename(prepared))
        self.assertIn("повторний", brief.preparation_filename(prepared))
        with TemporaryDirectory() as directory:
            target = Path(directory) / brief.preparation_filename(prepared)
            brief.write_preparation_csv(target, prepared)
            with target.open("r", encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.reader(stream, delimiter=";"))
            self.assertIn("НЕ Є ЖУРНАЛОМ", rows[0][0])
            self.assertEqual(rows[2], ["Вид", "Повторний"])
            self.assertEqual(rows[-2:], [["1", "Працівник один"], ["2", "Працівник два"]])
            with self.assertRaises(FileExistsError):
                brief.write_preparation_csv(target, prepared)
            self.assertEqual(len(list(Path(directory).iterdir())), 1)

    def test_live_operations_tab_is_visible_and_button_callable(self):
        errors = []
        core = SimpleNamespace(
            tk=tk, ttk=ttk,
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: None,
                showerror=lambda *a, **k: errors.append((a, k)),
                askyesno=lambda *a, **k: False,
            ),
            filedialog=SimpleNamespace(
                asksaveasfilename=lambda *a, **k: self.fail("Invalid input must not open save dialog")
            ),
            db=lambda: _DummyConnection(),
            configure_toplevel=lambda *a, **k: None,
            fit_window_to_screen=lambda *a, **k: None,
        )
        app = _AppHarness()
        app.withdraw()
        try:
            with mock.patch.object(operations_orders_ui.ops, "ensure_schema"), \
                 mock.patch.object(operations_orders_ui.ops, "settings", return_value={
                     "operations_responsible_employee_id": None,
                     "military_transport_responsible_employee_id": None,
                     "order_place": "",
                 }), \
                 mock.patch.object(operations_orders_ui.ops, "list_employee_choices", return_value=[
                     {"id": 1, "label": "Працівник один"},
                 ]), \
                 mock.patch.object(operations_orders_ui.ops, "list_orders", return_value=[]):
                win = operations_orders_ui.open_operations_center(app, core)
                win.geometry("940x600")
                app.update_idletasks()
                app.update()
                book = next(w for w in walk(win) if isinstance(w, ttk.Notebook))
                labels = [book.tab(tab, "text") for tab in book.tabs()]
                self.assertIn("Інструктажі та журнали", labels)
                self.assertIn("Накази", labels)
                self.assertIn("Каталог наказів", labels)
                instruction_tab = next(t for t in book.tabs() if book.tab(t, "text") == "Інструктажі та журнали")
                book.select(instruction_tab)
                app.update_idletasks()
                app.update()
                button = next(
                    w for w in walk(win)
                    if w.winfo_class() in ("TButton", "Button")
                    and str(w.cget("text")) == "Зберегти підготовчий список…"
                )
                self.assertTrue(button.winfo_ismapped())
                button.invoke()  # no topic and no selected employees: show an error without file write
                self.assertTrue(errors)
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
