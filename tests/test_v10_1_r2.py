# -*- coding: utf-8 -*-
import inspect
import unittest

import main
import personnel_v91
import v91_features


class TestTaxo101R2TimesheetUi(unittest.TestCase):
    def test_runtime_version_markers_are_r2(self):
        self.assertEqual(v91_features.APP_VERSION, "10.1-r2")
        self.assertEqual(personnel_v91.APP_VERSION, "10.1-r2")

    def test_timesheet_window_uses_new_office_header(self):
        source = inspect.getsource(main.App.show_employee_timesheet)
        self.assertIn('win.title("Taxo — Табель обліку робочого часу")', source)
        self.assertIn('text="▣  Табель обліку робочого часу"', source)
        self.assertIn("Підсумок місяця, щоденна деталізація та звіти", source)
        self.assertIn('bg="#EAF4FB"', source)

    def test_summary_tab_exposes_detail_and_reports(self):
        source = inspect.getsource(main.App.show_employee_timesheet)
        for marker in (
            "Відкрити деталізацію",
            "PDF працівника",
            "XLSX працівника",
            "Місячний звіт / баланс",
        ):
            self.assertIn(marker, source)
        self.assertIn("command=open_summary_employee", source)
        self.assertIn('command=lambda:export_summary_employee("pdf")', source)
        self.assertIn('command=lambda:export_summary_employee("xlsx")', source)
        self.assertIn("command=show_personnel_balance", source)

    def test_summary_selection_drives_employee_detail(self):
        source = inspect.getsource(main.App.show_employee_timesheet)
        self.assertIn("def select_summary_employee()", source)
        self.assertIn("employee_choice.set(label)", source)
        self.assertIn("notebook.select(daily_tab)", source)
        self.assertIn('summary_tree.bind("<Double-1>",open_summary_employee)', source)

    def test_month_status_surfaces_missing_fact(self):
        source = inspect.getsource(main.App.show_employee_timesheet)
        self.assertIn("summary_status", source)
        self.assertIn("днів із планом без факту", source)
        self.assertIn("missing_total", source)


if __name__ == "__main__":
    unittest.main()
