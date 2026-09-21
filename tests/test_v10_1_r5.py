# -*- coding: utf-8 -*-
import inspect
import unittest
from pathlib import Path

import main
import personnel_v91

ROOT=Path(__file__).resolve().parents[1]

class TestTaxo101R5NavigationLoopFix(unittest.TestCase):
    def test_r5_feature_line_survives_stable_promotion(self):
        self.assertRegex(main.APP_VERSION,r"^10\.\d+(?:-r\d+(?:\.\d+)*)?$")
        self.assertIn("Taxo 10.1-r5",(ROOT/"docs/releases/RELEASE_NOTES_v10_1_r5.md").read_text("utf-8"))

    def test_main_reports_nav_does_not_open_timesheet_window(self):
        source=inspect.getsource(main.App.build_ui)
        self.assertIn('add_nav("Звіти","chart",command=self.show_reports_home)',source)
        self.assertNotIn('add_nav("Звіти","chart",command=self.show_employee_timesheet)',source)

    def test_reports_home_prefers_main_workspace(self):
        source=inspect.getsource(main.App.show_reports_home)
        self.assertIn("personnel_book",source)
        self.assertIn("personnel_reports_page",source)
        self.assertIn('self._nav_active_override="Звіти"',source)

    def test_personnel_extension_routes_workers_and_reports_explicitly(self):
        source=inspect.getsource(personnel_v91)
        self.assertIn("def show_personnel_overview",source)
        self.assertIn("def show_reports_home",source)
        self.assertIn("personnel_reports_page",source)
        self.assertIn("command=self.show_personnel_overview",source)
        self.assertIn("sync_personnel_nav",source)

    def test_detailed_timesheet_is_single_instance(self):
        source=inspect.getsource(main.App.show_employee_timesheet)
        self.assertIn("_employee_timesheet_win",source)
        self.assertIn("existing.winfo_exists()",source)
        self.assertIn("existing.lift()",source)
        self.assertIn("return existing",source)

    def test_detailed_timesheet_is_not_a_second_full_app_shell(self):
        source=inspect.getsource(main.App.show_employee_timesheet)
        self.assertNotIn('sidebar=tk.Frame(shell,bg=PALETTE["sidebar"]',source)
        self.assertNotIn("def side_action",source)
        self.assertNotIn("draw_side_road",source)
        self.assertIn('text="Закрити"',source)

    def test_r5_release_notes_document_manual_gate(self):
        notes=(ROOT/"docs/releases/RELEASE_NOTES_v10_1_r5.md").read_text("utf-8")
        self.assertIn("Taxo 10.1-r5",notes)
        self.assertIn("не відкриває нову копію",notes)
        self.assertIn("ручна Windows-перевірка",notes)

if __name__=="__main__":
    unittest.main()
