# -*- coding: utf-8 -*-
"""10.21-r7: reuse the existing schedule date calendar for waybills."""
import unittest
from datetime import date
from pathlib import Path
from unittest import mock
import waybill_date_navigation as nav

class DateVar:
    def __init__(self, value): self.value=value
    def get(self): return self.value
    def set(self, value): self.value=value

class Window:
    def winfo_exists(self): return True
    def title(self, value): self.title_value=value

class App:
    def __init__(self):
        self.waybill_date=date(2026,11,17)
        self.waybill_date_label=DateVar("17.11.2026")
        self.waybill_win=Window()
        self.refresh_count=0
    def refresh_waybill_issue_list(self): self.refresh_count+=1

class WaybillCalendarR7Tests(unittest.TestCase):
    def test_shared_calendar_changes_waybill_day_immediately(self):
        app=App()
        def choose(parent, variable):
            self.assertIs(parent,app.waybill_win)
            variable.set("03.10.2026")
        self.assertTrue(nav.open_waybill_calendar(app,choose,app.waybill_win))
        self.assertEqual(app.waybill_date,date(2026,10,3))
        self.assertEqual(app.refresh_count,1)
        self.assertEqual(app.waybill_win.title_value,"Шляхівки на 03.10.2026")

    def test_cancel_does_not_refresh_or_change_day(self):
        app=App()
        app.waybill_date_label.set("wrong unsubmitted text")
        self.assertFalse(nav.open_waybill_calendar(app,lambda _p,_v: None,app.waybill_win))
        self.assertEqual(app.waybill_date,date(2026,11,17))
        self.assertEqual(app.refresh_count,0)
        self.assertEqual(app.waybill_date_label.get(),"17.11.2026")

    def test_choose_same_day_does_not_refresh(self):
        app=App()
        self.assertFalse(nav.open_waybill_calendar(app,lambda _p,v:v.set("17.11.2026"),app.waybill_win))
        self.assertEqual(app.refresh_count,0)

    def test_reuses_main_schedule_calendar_button_without_new_dependencies(self):
        src=Path(nav.__file__).read_text("utf-8")
        self.assertIn("calendar_button=_core.calendar_button",src)
        self.assertIn("calendar_picker=_core.show_calendar_picker",src)
        self.assertIn("calendar.configure(command=",src)
        self.assertNotIn("tkcalendar",src)
        self.assertNotIn("sqlite3",src)

    def test_version(self):
        root=Path(__file__).resolve().parents[1]
        self.assertEqual((root/"VERSION.txt").read_text("utf-8"),"Version: 10.21-r9\n")
        self.assertIn('APP_VERSION = "10.21-r9"',(root/"main.py").read_text("utf-8"))

if __name__ == "__main__": unittest.main()
