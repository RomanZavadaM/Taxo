# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file


ROOT=Path(__file__).resolve().parents[1]


class TestTaxo102R8PersonnelPlanning(unittest.TestCase):
    def test_r8_checkpoint_is_not_reused_by_later_revisions(self):
        self.assertTrue(main.APP_VERSION.startswith("10.2-r"))
        self.assertGreaterEqual(int(main.APP_VERSION.rsplit("r",1)[1]),8)
        self.assertEqual(version_from_file(ROOT/"VERSION.txt"),main.APP_VERSION)
        self.assertEqual(
            start_archive_stem("10.2-r8"),
            "Taxo_v10_2_candidate_r8_START",
        )

    def test_personnel_page_is_the_single_non_driver_planning_hub(self):
        source=(ROOT/"personnel_v91.py").read_text("utf-8")
        self.assertIn("Єдине планування персоналу",source)
        self.assertIn('text="Графік водіїв…"',source)
        self.assertIn('text="Робочі зміни персоналу — масово…"',source)
        self.assertIn('text="Оперативний день випуску…"',source)
        self.assertIn("command=self.show_general_personnel_shift_planner",source)
        self.assertNotIn(
            'text="Лікар / механік для випуску на лінію…", command=self.show_dispatch_month_planner',
            source,
        )

    def test_legacy_dispatch_month_route_cannot_open_parallel_writer(self):
        source=(ROOT/"personnel_v91.py").read_text("utf-8")
        marker="def show_dispatch_month_planner(self):"
        start=source.index(marker)
        snippet=source[start:start+300]
        self.assertIn("return self.show_general_personnel_shift_planner()",snippet)

    def test_driver_role_still_routes_to_driver_schedule(self):
        source=(ROOT/"personnel_v91.py").read_text("utf-8")
        self.assertIn("Водій — планувати у «Графік водіїв»",source)
        self.assertIn("Щоб не дублювати маршрут/робочий час у employee_shifts",source)

    def test_dispatch_window_is_operational_view_not_separate_accounting(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn('win,"Оперативні зміни випуску"',source)
        self.assertIn('text="Планувати / перепланувати…"',source)
        self.assertIn('"show_general_personnel_shift_planner"',source)
        self.assertIn("Це не окремий облік",source)
        self.assertIn('ttk.Button(top,text="Редагувати / факт"',source)

    def test_dispatch_correction_preserves_paid_plan_semantics(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn('("break","Неоплачувана перерва, хв")',source)
        self.assertIn("planned=(span_minutes-break_minutes)/60.0",source)
        self.assertIn("unpaid_break_minutes=?,planned_hours=?",source)
        self.assertIn("location,unpaid_break_minutes,planned_hours,actual_hours",source)

    def test_old_v91_button_no_longer_exposes_specialized_month_planner(self):
        source=(ROOT/"v91_features.py").read_text("utf-8")
        self.assertNotIn(
            'text="План на місяць",\n                command=self.show_dispatch_month_planner',
            source,
        )
        self.assertIn("second «План на місяць» button",source)

    def test_service_menu_routes_to_personnel_planning(self):
        source=(ROOT/"personnel_v91.py").read_text("utf-8")
        self.assertIn('label="Планування персоналу"',source)
        self.assertIn("command=self.show_personnel_planning",source)
        self.assertIn('label="Реєстр працівників"',source)


if __name__=="__main__":
    unittest.main()
