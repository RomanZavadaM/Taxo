# -*- coding: utf-8 -*-
import inspect
import unittest
from pathlib import Path

import main
import personnel_v91

ROOT=Path(__file__).resolve().parents[1]

class TestTaxo101R4ApprovedUiPolish(unittest.TestCase):
    def test_r4_feature_line_survives_newer_candidates(self):
        self.assertRegex(main.APP_VERSION,r"^10\.\d+(?:-r\d+(?:\.\d+)*)?$")
        self.assertIn("Taxo 10.1-r4",(ROOT/"docs/releases/RELEASE_NOTES_v10_1_r4.md").read_text("utf-8"))

    def test_personnel_registry_has_visual_hierarchy_and_kpis(self):
        source=inspect.getsource(personnel_v91)
        for marker in (
            "personnel_stat_vars",'("all","Всього"','("active","Працюють"',
            '("drivers","Водії"','("inactive","Звільнені"',
            'text="＋  Новий працівник"','text="Пошук"',
        ):
            self.assertIn(marker,source)

    def test_personnel_registry_splits_primary_and_secondary_actions(self):
        source=inspect.getsource(personnel_v91)
        self.assertIn("hero_left",source)
        self.assertIn("tool_left",source)
        self.assertIn('text="Режим робочого часу…"',source)
        self.assertTrue(
            'text="Планування змін…"' in source
            or 'text="Планування…"' in source
        )

    def test_timesheet_separates_work_actions_from_reports(self):
        source=inspect.getsource(main.App.show_employee_timesheet)
        self.assertIn("toolbar_actions",source)
        self.assertIn("toolbar_reports",source)
        self.assertIn('text="Робота з табелем:"',source)
        self.assertIn('text="Звіти та друк:"',source)
        self.assertIn('text="PDF звіт — весь персонал"',source)
        self.assertIn('text="Excel звіт — весь персонал"',source)
        self.assertIn('text="Папка звітів"',source)

    def test_about_and_help_titles_use_enterprise_name(self):
        about=inspect.getsource(main.App.show_about)
        help_=inspect.getsource(main.App.show_help)
        self.assertIn('self._company_name_value()',about)
        self.assertIn('— Про програму',about)
        self.assertIn('self._company_name_value()',help_)
        self.assertIn('— Довідка',help_)

    def test_r4_release_notes_exist(self):
        notes=(ROOT/"docs/releases/RELEASE_NOTES_v10_1_r4.md").read_text("utf-8")
        self.assertIn("Taxo 10.1-r4",notes)
        self.assertIn("Звіти та друк",notes)
        self.assertIn("ручна Windows-перевірка",notes)

if __name__=="__main__":
    unittest.main()
