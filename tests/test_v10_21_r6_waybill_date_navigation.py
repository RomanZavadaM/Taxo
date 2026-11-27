# -*- coding: utf-8 -*-
"""10.21-r7: independent date navigation in the waybill window."""
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

import feature_layers
import waybill_date_navigation as nav


class DummyVar:
    def __init__(self, value=""):
        self.value = value
    def get(self):
        return self.value
    def set(self, value):
        self.value = value


class DummyWindow:
    def __init__(self):
        self.last_title = ""
    def winfo_exists(self):
        return True
    def title(self, value):
        self.last_title = value


class DummyApp:
    def __init__(self, day=date(2026, 11, 17)):
        self.waybill_date = day
        self.waybill_date_label = DummyVar(day.strftime("%d.%m.%Y"))
        self.waybill_win = DummyWindow()
        self.refresh_count = 0
    def refresh_waybill_issue_list(self):
        self.refresh_count += 1


class WaybillDateNavigationR6Tests(unittest.TestCase):
    def test_r6_identity_and_feature_registration(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.25-r3\n")
        self.assertIn('APP_VERSION = "10.25-r3"', (root / "main.py").read_text("utf-8"))
        self.assertIn("Taxo 10.25-r3", (root / "START.bat").read_text("utf-8"))
        self.assertIn("v1021-r6-waybill-date-navigation", feature_layers.feature_layer_ids())

    def test_parse_exact_user_format(self):
        self.assertEqual(nav.parse_waybill_date_text("18.11.2026"), date(2026, 11, 18))
        with self.assertRaises(ValueError):
            nav.parse_waybill_date_text("2026-11-18")
        with self.assertRaises(ValueError):
            nav.parse_waybill_date_text("")

    def test_apply_and_shift_refresh_only_waybill_day(self):
        app = DummyApp()
        nav.apply_waybill_date(app, date(2026, 11, 20))
        self.assertEqual(app.waybill_date, date(2026, 11, 20))
        self.assertEqual(app.waybill_date_label.get(), "20.11.2026")
        self.assertEqual(app.waybill_win.last_title, "Шляхівки на 20.11.2026")
        self.assertEqual(app.refresh_count, 1)
        nav.shift_waybill_date(app, -1)
        self.assertEqual(app.waybill_date, date(2026, 11, 19))
        self.assertEqual(app.refresh_count, 2)

    def test_entered_date_and_invalid_value(self):
        app = DummyApp()
        app.waybill_date_label.set("21.11.2026")
        self.assertTrue(nav.go_to_entered_waybill_date(app))
        self.assertEqual(app.waybill_date, date(2026, 11, 21))
        app.waybill_date_label.set("bad")
        with mock.patch.object(nav.messagebox, "showerror") as showerror:
            self.assertFalse(nav.go_to_entered_waybill_date(app))
        self.assertEqual(app.waybill_date, date(2026, 11, 21))
        self.assertEqual(app.waybill_date_label.get(), "21.11.2026")
        showerror.assert_called_once()

    def test_ui_contract_is_navigation_only(self):
        source = Path(nav.__file__).read_text("utf-8")
        for label in ('text="День -"', 'text="Сьогодні"', 'text="День +"', 'text="Перейти"'):
            self.assertIn(label, source)
        self.assertIn('ttk.Entry(frame, textvariable=variable, width=12)', source)
        self.assertIn('"<Return>"', source)
        self.assertNotIn("sqlite3", source)
        self.assertNotIn("UPDATE waybills", source)


if __name__ == "__main__":
    unittest.main()
