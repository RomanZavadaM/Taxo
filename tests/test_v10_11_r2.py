# -*- coding: utf-8 -*-
"""Taxo 10.11-r2 — simple personnel report naming and PDF layout."""
import inspect
import tempfile
import unittest
from datetime import date
from pathlib import Path

from openpyxl import load_workbook
from pypdf import PdfReader

import personnel_month_schedule_r8 as schedule


def sample_data(year, month, count, *, all_selected=False):
    days = [date(year, month, day) for day in range(1, count + 1)]
    employees = [
        {"employee_id": 7, "personnel_no": "0007", "name": "Галань Михайло Степанович-Дуже-Довге-Прізвище", "roles": "Водій, Механік", "cells": ["Р" if day.day % 2 else "Вих" for day in days]},
        {"employee_id": 12, "personnel_no": "0012", "name": "Дробот Олег Іванович", "roles": "Контролер", "cells": ["Р" for _ in days]},
        {"employee_id": 18, "personnel_no": "0018", "name": "Палій Петро Андрійович", "roles": "Механік", "cells": ["Вих" for _ in days]},
    ]
    return {"year": year, "month": month, "days": days, "employees": employees, "view": schedule.VIEW_EMPLOYEE, "all_selected": all_selected, "internal_notes": []}


class PersonnelFilenameTests(unittest.TestCase):
    def test_all_selected_name_identifies_document_month_and_scope(self):
        data = sample_data(2026, 11, 30, all_selected=True)
        self.assertEqual(schedule.employee_schedule_filename(data, "pdf"), "Простий_графік_роботи_2026-11_усі-працівники.pdf")

    def test_one_employee_name_is_human_readable(self):
        data = sample_data(2026, 11, 30)
        data["employees"] = data["employees"][:1]
        self.assertEqual(schedule.employee_schedule_filename(data, "pdf"), "Простий_графік_роботи_2026-11_Галань-Михайло.pdf")

    def test_different_groups_have_different_stable_names(self):
        data = sample_data(2026, 11, 30)
        first = dict(data); first["employees"] = data["employees"][:2]
        second = dict(data); second["employees"] = [data["employees"][0], data["employees"][2]]
        a = schedule.employee_schedule_filename(first, "pdf")
        b = schedule.employee_schedule_filename(second, "pdf")
        self.assertNotEqual(a, b)
        self.assertIn("Галань-Дробот-", a)
        self.assertIn("Галань-Палій-", b)
        self.assertEqual(a, schedule.employee_schedule_filename(first, "pdf"))

    def test_pdf_and_xlsx_names_are_distinguishable(self):
        data = sample_data(2026, 11, 30)
        self.assertTrue(schedule.employee_schedule_filename(data, "pdf").endswith(".pdf"))
        self.assertTrue(schedule.employee_schedule_filename(data, "xlsx").endswith(".xlsx"))


class PersonnelPdfLayoutTests(unittest.TestCase):
    def test_pdf_source_has_no_role_column_but_xlsx_keeps_it(self):
        pdf_source = inspect.getsource(schedule.export_employee_schedule_pdf)
        self.assertNotIn('employee["roles"]', pdf_source)
        self.assertNotIn("<b>Роль</b>", pdf_source)
        data = sample_data(2026, 11, 30)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "schedule.xlsx"
            schedule.export_employee_schedule_xlsx(data, path)
            wb = load_workbook(path, read_only=True, data_only=True)
            try:
                self.assertEqual(wb.active["C4"].value, "Роль")
                self.assertEqual(wb.active["C6"].value, "Водій, Механік")
            finally:
                wb.close()

    def test_pdf_builds_for_30_and_31_days_with_long_names(self):
        for year, month, count in ((2026, 11, 30), (2026, 12, 31)):
            with self.subTest(month=month), tempfile.TemporaryDirectory() as tmp:
                data = sample_data(year, month, count)
                path = Path(tmp) / "schedule.pdf"
                schedule.export_employee_schedule_pdf(data, path)
                self.assertTrue(path.exists())
                self.assertGreater(path.stat().st_size, 1000)
                reader = PdfReader(str(path))
                self.assertGreaterEqual(len(reader.pages), 1)
                page = reader.pages[0]
                self.assertGreater(float(page.mediabox.width), float(page.mediabox.height))


if __name__ == "__main__":
    unittest.main()
