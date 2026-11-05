# -*- coding: utf-8 -*-
"""Taxo 10.11-r1 — зрозумілий вихід із графіка змінності."""
import inspect
import unittest
from unittest.mock import Mock

import main


class ReportFilenameTests(unittest.TestCase):
    def test_all_drivers_has_meaningful_name(self):
        self.assertEqual(
            main.monthly_shift_report_filename(2026,11,"graph"),
            "Графік_змінності_2026-11_усі-водії.pdf",
        )

    def test_selected_sets_have_distinct_stable_names(self):
        a=main.monthly_shift_report_filename(2026,11,"graph",[3,2],"pdf")
        b=main.monthly_shift_report_filename(2026,11,"graph",[2,3],"pdf")
        c=main.monthly_shift_report_filename(2026,11,"graph",[2,4],"pdf")
        self.assertEqual(a,b)
        self.assertNotEqual(a,c)
        self.assertIn("обрані-2-",a)

    def test_selected_driver_filename_uses_person_name(self):
        label=main.monthly_shift_report_filename(
            2026,11,"graph",[18],"pdf",driver_names={18:"Галань Михайло Степанович"}
        )
        self.assertEqual(label,"Графік_змінності_2026-11_Галань-Михайло.pdf")

    def test_selected_group_filename_shows_names_and_differs_by_group(self):
        people={2:"Галань Михайло",3:"Дробот Олег",4:"Палій Петро"}
        label=main.monthly_shift_report_filename(2026,11,"graph",[2,3,4],"pdf",people)
        self.assertIn("Галань-Дробот-та-ще-1-",label)

    def test_detail_and_excel_are_distinguishable(self):
        detail=main.monthly_shift_report_filename(2026,11,"detail",[3],"pdf")
        excel=main.monthly_shift_report_filename(2026,11,"graph",[3],"xlsx")
        self.assertIn("Деталізація_змін_",detail)
        self.assertTrue(excel.endswith(".xlsx"))
        self.assertNotEqual(detail,excel)


class SimpleReportWindowTests(unittest.TestCase):
    def test_window_has_one_format_choice_and_two_actions(self):
        src=inspect.getsource(main.App.show_monthly_shift_schedule)
        self.assertIn('text="Документ:"',src)
        self.assertIn('text="Переглянути"',src)
        self.assertIn('text="Зберегти…"',src)
        self.assertNotIn('text="PDF — графік"',src)
        self.assertNotIn('text="PDF — деталізація"',src)

    def test_preview_dispatches_to_chosen_document(self):
        class V:
            def __init__(self, v): self.v=v
            def get(self): return self.v
        class Fake:
            monthly_shift_document_kind=V("Деталізація змін (PDF)")
            open_monthly_shift_schedule_pdf=Mock()
            open_monthly_shift_detail_pdf=Mock()
            open_monthly_shift_schedule_xlsx=Mock()
        main.App.preview_monthly_shift_document(Fake)
        Fake.open_monthly_shift_detail_pdf.assert_called_once_with()
        Fake.open_monthly_shift_schedule_pdf.assert_not_called()
        Fake.open_monthly_shift_schedule_xlsx.assert_not_called()


if __name__=="__main__":
    unittest.main()
