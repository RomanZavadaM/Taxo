# -*- coding: utf-8 -*-
import calendar
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from personnel_v91 import (
    ABSENCE_TYPES,
    NONWORK_OVERRIDE_TYPES,
    P5_CODES,
    P5_LEGEND,
    collect_p5_data,
    export_p5_pdf,
    export_p5_xlsx,
    install,
    p5_code,
)


class FakeCore:
    def __init__(self, db_path):
        self.DB_PATH = Path(db_path)
        self.App = object
        self._TAXO_PERSONNEL_R3_INSTALLED = False

    def db(self):
        con = sqlite3.connect(self.DB_PATH)
        con.row_factory = sqlite3.Row
        return con

    @staticmethod
    def hours_value_to_minutes(value):
        if value is None:
            return 0
        return int(round(float(value) * 60))

    @staticmethod
    def minutes_hhmm(value):
        value = int(value or 0)
        return f"{value // 60}:{value % 60:02d}"

    @staticmethod
    def month_dates(year, month):
        last = calendar.monthrange(int(year), int(month))[1]
        return [date(int(year), int(month), day) for day in range(1, last + 1)]

    @staticmethod
    def employee_employed_on(employee, target_date):
        started = date.fromisoformat(employee["employment_date"]) if employee["employment_date"] else None
        finished = date.fromisoformat(employee["dismissal_date"]) if employee["dismissal_date"] else None
        return (started is None or target_date >= started) and (finished is None or target_date <= finished)

    @staticmethod
    def employee_name(employee):
        return " ".join(x for x in (employee["last_name"], employee["first_name"], employee["middle_name"]) if x)

    @staticmethod
    def month_name_ua(month):
        return ("Січень","Лютий","Березень","Квітень","Травень","Червень","Липень","Серпень","Вересень","Жовтень","Листопад","Грудень")[int(month)-1]

    @staticmethod
    def report_font_candidates():
        return []

    def employee_day_time(self, con, employee_id, target_date):
        entry = con.execute(
            "SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",
            (employee_id, target_date.isoformat()),
        ).fetchone()
        if entry:
            planned = self.hours_value_to_minutes(entry["planned_hours"]) if entry["planned_hours"] is not None else 0
            actual = self.hours_value_to_minutes(entry["actual_hours"]) if entry["actual_hours"] is not None else None
            return {
                "day_type": entry["day_type"],
                "planned_minutes": planned,
                "actual_minutes": actual,
                "source": "manual",
                "notes": entry["notes"] or "",
                "manual": True,
            }
        return {
            "day_type": "Вихідний",
            "planned_minutes": 0,
            "actual_minutes": None,
            "source": "—",
            "notes": "",
            "manual": False,
        }


def make_db(path):
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE company(id INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO company(id,name) VALUES(1,'Тестове АТП');
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY,
            personnel_no TEXT,
            last_name TEXT,
            first_name TEXT,
            middle_name TEXT,
            position TEXT,
            employment_date TEXT,
            dismissal_date TEXT,
            active INTEGER,
            driver_id INTEGER
        );
        CREATE TABLE employee_roles(employee_id INTEGER, role TEXT);
        CREATE TABLE employee_time_entries(
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            work_date TEXT,
            day_type TEXT,
            planned_hours REAL,
            actual_hours REAL,
            notes TEXT
        );
        CREATE TABLE worklog(
            id INTEGER PRIMARY KEY,
            driver_id INTEGER,
            work_date TEXT,
            overtime_hours REAL
        );
        INSERT INTO employees VALUES(1,'0001','Тестовий','Працівник','','механік','2026-01-01','',1,NULL);
        INSERT INTO employee_roles VALUES(1,'Механік');
        INSERT INTO employee_time_entries(employee_id,work_date,day_type,planned_hours,actual_hours,notes)
            VALUES(1,'2026-08-03','Робота',8,8,'');
        INSERT INTO employee_time_entries(employee_id,work_date,day_type,planned_hours,actual_hours,notes)
            VALUES(1,'2026-08-04','Основна щорічна відпустка',0,0,'наказ');
        INSERT INTO employee_time_entries(employee_id,work_date,day_type,planned_hours,actual_hours,notes)
            VALUES(1,'2026-08-05','Оплачувана тимчасова непрацездатність',0,0,'листок');
        """
    )
    con.commit()
    con.close()


class TestPersonnelR3(unittest.TestCase):
    def test_p5_codes_match_sample_categories(self):
        self.assertEqual(p5_code("Основна щорічна відпустка")[:2], ("В", "08"))
        self.assertEqual(p5_code("Оплачувана тимчасова непрацездатність")[:2], ("ТН", "26"))
        self.assertEqual(p5_code("Відпустка без збереження зарплати за згодою сторін")[:2], ("НА", "18"))
        self.assertIn("Основна щорічна відпустка", ABSENCE_TYPES)

    def test_p5_legend_contains_all_30_codes_from_supplied_sample(self):
        self.assertEqual(len(P5_LEGEND), 30)
        by_code = {code: (label, letter) for label, letter, code in P5_LEGEND}
        self.assertEqual(by_code["10"][1], "Ч")
        self.assertEqual(by_code["20"][1], "НД")
        self.assertEqual(by_code["21"][1], "НП")
        self.assertEqual(by_code["30"][1], "І")

    def test_p5_collector_keeps_weekend_blank_and_counts_absences(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "db.sqlite3"
            make_db(db_path)
            core = FakeCore(db_path)
            data = collect_p5_data(core, 2026, 8, active_only=True)
            emp = data["employees"][0]
            self.assertEqual(emp["cells"][2]["code"], "Р")   # 03.08
            self.assertEqual(emp["cells"][3]["code"], "В")   # 04.08
            self.assertEqual(emp["cells"][4]["code"], "ТН")  # 05.08
            self.assertEqual(emp["absence_counts"]["8-10"], 1)
            self.assertEqual(emp["absence_counts"]["26-27"], 1)

    def test_absence_override_sets_zero_plan_without_deleting_source_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "db.sqlite3"
            make_db(db_path)
            core = FakeCore(db_path)

            # Replace original day-time with one that would otherwise expose 8h plan.
            def automatic_day(con, employee_id, target_date):
                if target_date == date(2026, 8, 4):
                    return {
                        "day_type": "Робота",
                        "planned_minutes": 480,
                        "actual_minutes": None,
                        "source": "зміна персоналу",
                        "notes": "",
                        "manual": False,
                    }
                return core.employee_day_time(con, employee_id, target_date)

            core.employee_day_time = automatic_day
            # Minimal attributes needed only for class definition.
            core.tk = SimpleNamespace(TclError=Exception)
            core.ttk = SimpleNamespace()
            core.messagebox = SimpleNamespace()
            core.filedialog = SimpleNamespace()
            core.fmt_date = lambda value: value
            core.OUTPUT_DIR = Path(tmp)
            core.write_output_file = lambda *a, **k: None

            Base = type("Base", (), {})
            install(core, Base)
            con = core.db()
            row = core.employee_day_time(con, 1, date(2026, 8, 4))
            con.close()
            self.assertEqual(row["day_type"], "Основна щорічна відпустка")
            self.assertEqual(row["planned_minutes"], 0)
            self.assertEqual(row["actual_minutes"], 0)

    def test_p5_pdf_and_xlsx_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            from openpyxl import load_workbook
            import fitz

            db_path = Path(tmp) / "db.sqlite3"
            make_db(db_path)
            core = FakeCore(db_path)
            pdf = Path(tmp) / "p5.pdf"
            xlsx = Path(tmp) / "p5.xlsx"
            export_p5_pdf(
                core, 2026, 8, pdf, True,
                date(2026, 8, 31), "Експлуатаційний відділ", "12345678"
            )
            export_p5_xlsx(
                core, 2026, 8, xlsx, True,
                date(2026, 8, 31), "Експлуатаційний відділ", "12345678"
            )
            self.assertTrue(pdf.exists() and pdf.stat().st_size > 1000)
            self.assertTrue(xlsx.exists() and xlsx.stat().st_size > 1000)

            with fitz.open(pdf) as doc:
                text = "\n".join(page.get_text() for page in doc)
            self.assertIn("Типова форма № П-5", text)
            self.assertIn("31.08.2026", text)
            self.assertIn("12345678", text)

            wb = load_workbook(xlsx, data_only=False)
            self.assertIn("Табель П-5", wb.sheetnames)
            self.assertIn("Умовні позначення", wb.sheetnames)
            self.assertIn("12345678", str(wb["Табель П-5"]["A3"].value))
            self.assertEqual(wb["Умовні позначення"]["C36"].value, "30")


if __name__ == "__main__":
    unittest.main()
