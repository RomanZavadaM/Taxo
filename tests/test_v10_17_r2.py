# -*- coding: utf-8 -*-
"""10.17-r2: hidden personnel pages must have an explicit return route."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import main
import personnel_v91

ROOT = Path(__file__).resolve().parents[1]


class PersonnelNavigationR2Tests(unittest.TestCase):
    def test_revision_markers(self):
        self.assertEqual(main.APP_VERSION, "10.17-r2")
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"), "Version: 10.17-r2\n"
        )
        self.assertIn("Taxo 10.17-r2", (ROOT / "START.bat").read_text("utf-8"))

    def test_planning_timesheet_and_reports_have_back_to_registry(self):
        source = inspect.getsource(personnel_v91)
        planning = source.split("# Планування — внутрішні вкладки приховані", 1)[1].split("# Табель — явна", 1)[0]
        timesheet = source.split("# Табель — явна", 1)[1].split("# Звіти —", 1)[0]
        reports = source.split('rpanel = core.ttk.Frame(reports_body, padding=16)', 1)[1]
        for page in (planning, timesheet, reports):
            self.assertIn('text="← До реєстру працівників"', page)
            self.assertIn("command=self.show_personnel_overview", page)

    def test_return_targets_existing_page_and_does_not_create_window(self):
        source = inspect.getsource(personnel_v91)
        self.assertIn("def show_personnel_overview(self):", source)
        self.assertIn("self._select_personnel_page(", source)
        self.assertIn('getattr(self,"personnel_overview_page",None)', source)
        self.assertNotIn('text="← До реєстру працівників",\n                command=lambda: core.tk.Toplevel', source)

    def test_planning_actions_stay_available(self):
        source = inspect.getsource(personnel_v91)
        for label in (
            "Графік водіїв…",
            "Робочі зміни персоналу — масово…",
            "Простий місячний графік…",
            "Оперативний день випуску…",
            "Режими робочого часу працівників…",
            "Відпустки / лікарняні / інші відсутності…",
        ):
            self.assertIn(label, source)


if __name__ == "__main__":
    unittest.main()
