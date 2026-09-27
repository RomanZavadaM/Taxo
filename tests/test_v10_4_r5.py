# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from openpyxl import Workbook

import personnel_registry as pr

ROOT=Path(__file__).resolve().parents[1]


DETAILED_HEADERS=[
    "Прізвище, ім’я, по батькові","РНОКПП","Серія та номер паспорту","Номер ID картки",
    "Дата народження","Адреса зареєстрованого місця проживання","Адреса фактичного місця проживання",
    "Ідентифікатор військовозобов'язаного","Вид обліку особи","Статус обліку особи",
    "Належність до резервістів","Бронювання","Дата кінця бронювання","Причина відстрочки",
    "Дата закінчення відстрочки","Військове звання","Військово-облікова спеціальність",
    "Найменування ТЦК, органу СБУ, відповідного підрозділу розвідувального органу, в якому перебуває на військовому обліку",
    "Військова служба",
]
SUMMARY_HEADERS=[
    "Прізвище","Імʼя","По батькові","Стать","Дата народження","РНОКПП",
    "Серія паспорту","Номер паспорту","Номер ID-картки","Статус","Примітка",
]


def write_xlsx(path, headers, rows, title="Дані"):
    wb=Workbook(); ws=wb.active; ws.title=title
    ws.append(headers)
    for row in rows: ws.append(row)
    wb.save(path)


class TestTaxo104R5PersonnelRegistry(unittest.TestCase):
    def _db_core(self, path):
        def db():
            con=sqlite3.connect(path)
            con.row_factory=sqlite3.Row
            return con
        return SimpleNamespace(db=db)

    def _base_db(self, path, rnokpp=""):
        con=sqlite3.connect(path)
        con.row_factory=sqlite3.Row
        con.executescript("""
            CREATE TABLE employees(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                personnel_no TEXT DEFAULT '',
                last_name TEXT NOT NULL,
                first_name TEXT NOT NULL,
                middle_name TEXT DEFAULT '',
                position TEXT DEFAULT '',
                employment_date TEXT DEFAULT '',
                dismissal_date TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                active INTEGER NOT NULL DEFAULT 1,
                driver_id INTEGER,
                created_at TEXT NOT NULL
            );
        """)
        pr.ensure_schema_on_connection(con)
        con.execute(
            """INSERT INTO employees(
                personnel_no,last_name,first_name,middle_name,position,employment_date,active,created_at,rnokpp
            ) VALUES(?,?,?,?,?,?,?,?,?)""",
            ("T-01","Тестовий","Петро","Іванович","Механік","2026-01-01",1,"2026-01-01T08:00:00",rnokpp),
        )
        con.commit(); con.close()

    def test_detailed_registry_form_is_detected_and_normalized(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"detail.xlsx"
            write_xlsx(path,DETAILED_HEADERS,[
                ["Тестовий Петро Іванович","1234567890","КА123456","","15.04.1985",
                 "м. Тест, вул. Перша, 1","м. Тест, вул. Друга, 2",
                 "11111111-2222-3333-4444-555555555555","Військовозобовʼязаний","На обліку",
                 "Особа не є резервістом","Заброньовано до певної дати","01.07.2027","","",
                 "Солдат","123456","Тестовий РТЦК та СП","Не на службі"]
            ],"Відомості персонального обліку")
            data=pr.parse_registry_xlsx(path)
            self.assertEqual(data["source_kind"],pr.SOURCE_DETAILED)
            self.assertEqual(len(data["rows"]),1)
            row=data["rows"][0]
            self.assertEqual(row["personal"]["rnokpp"],"1234567890")
            self.assertEqual(row["personal"]["passport_series"],"КА")
            self.assertEqual(row["personal"]["passport_number"],"123456")
            self.assertEqual(row["military"]["booking_until"],"2027-07-01")
            self.assertEqual(row["military"]["military_specialty"],"123456")

    def test_summary_form_uses_booking_note_but_rejects_placeholder_documents(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"summary.xlsx"
            write_xlsx(path,SUMMARY_HEADERS,[
                ["Тестовий","Петро","Іванович","Ч","15.04.1985","1234567890","17","17","17","Заброньовано","До 01.07.2027"]
            ],"Інформація про працівників")
            data=pr.parse_registry_xlsx(path)
            row=data["rows"][0]
            self.assertEqual(data["source_kind"],pr.SOURCE_SUMMARY)
            self.assertEqual(row["military"]["booking_status"],"Заброньовано до певної дати")
            self.assertEqual(row["military"]["booking_until"],"2027-07-01")
            self.assertEqual(row["personal"]["passport_number"],"")
            self.assertEqual(row["personal"]["id_card_number"],"")
            self.assertGreaterEqual(len(row["warnings"]),2)

    def test_preview_matches_by_name_then_apply_fills_rnokpp_military_history_and_documents(self):
        with tempfile.TemporaryDirectory() as td:
            db_path=Path(td)/"taxo.sqlite3"; self._base_db(db_path)
            xlsx=Path(td)/"detail.xlsx"
            write_xlsx(xlsx,DETAILED_HEADERS,[
                ["Тестовий Петро Іванович","1234567890","КА123456","","15.04.1985",
                 "м. Тест, 1","м. Тест, 2","11111111-2222-3333-4444-555555555555",
                 "Військовозобовʼязаний","На обліку","Особа не є резервістом",
                 "Заброньовано до певної дати","01.07.2027","","","Солдат","123456",
                 "Тестовий РТЦК та СП","Не на службі"]
            ])
            core=self._db_core(db_path)
            preview=pr.preview_registry_import(core,xlsx)
            self.assertEqual(preview["plan"][0]["match_quality"],"name")
            self.assertEqual(preview["plan"][0]["status"],"update")
            result=pr.apply_registry_import(core,preview)
            self.assertEqual(result["matched"],1)
            self.assertEqual(result["updated"],1)

            con=core.db()
            employee=con.execute("SELECT * FROM employees WHERE id=1").fetchone()
            military=con.execute("SELECT * FROM employee_military_profile WHERE employee_id=1").fetchone()
            self.assertEqual(employee["rnokpp"],"1234567890")
            self.assertEqual(employee["birth_date"],"1985-04-15")
            self.assertEqual(employee["registered_address"],"м. Тест, 1")
            self.assertEqual(military["account_status"],"На обліку")
            self.assertEqual(military["booking_until"],"2027-07-01")
            self.assertEqual(con.execute("SELECT COUNT(*) FROM employee_registry_imports").fetchone()[0],1)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM employee_military_history").fetchone()[0],1)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM employee_documents").fetchone()[0],1)
            con.close()

            second=pr.preview_registry_import(core,xlsx)
            self.assertEqual(second["plan"][0]["match_quality"],"rnokpp")
            self.assertEqual(second["plan"][0]["status"],"no_changes")
            pr.apply_registry_import(core,second)
            con=core.db()
            self.assertEqual(con.execute("SELECT COUNT(*) FROM employee_registry_imports").fetchone()[0],2)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM employee_military_history").fetchone()[0],1)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM employee_documents").fetchone()[0],1)
            con.close()

    def test_name_match_never_overwrites_conflicting_rnokpp(self):
        with tempfile.TemporaryDirectory() as td:
            db_path=Path(td)/"taxo.sqlite3"; self._base_db(db_path,"9999999999")
            xlsx=Path(td)/"summary.xlsx"
            write_xlsx(xlsx,SUMMARY_HEADERS,[
                ["Тестовий","Петро","Іванович","Ч","15.04.1985","1234567890","","","","Не заброньовано","---"]
            ])
            core=self._db_core(db_path)
            preview=pr.preview_registry_import(core,xlsx)
            self.assertEqual(preview["plan"][0]["status"],"conflict")
            result=pr.apply_registry_import(core,preview)
            self.assertEqual(result["updated"],0)
            self.assertEqual(result["skipped"],1)
            con=core.db()
            self.assertEqual(con.execute("SELECT rnokpp FROM employees WHERE id=1").fetchone()[0],"9999999999")
            con.close()

    def test_unmatched_registry_person_is_not_auto_created(self):
        with tempfile.TemporaryDirectory() as td:
            db_path=Path(td)/"taxo.sqlite3"; self._base_db(db_path)
            xlsx=Path(td)/"summary.xlsx"
            write_xlsx(xlsx,SUMMARY_HEADERS,[
                ["Інший","Працівник","Новий","Ч","01.01.1990","1111111111","","","","Не заброньовано","---"]
            ])
            core=self._db_core(db_path)
            preview=pr.preview_registry_import(core,xlsx)
            self.assertEqual(preview["plan"][0]["status"],"unmatched")
            pr.apply_registry_import(core,preview)
            con=core.db()
            self.assertEqual(con.execute("SELECT COUNT(*) FROM employees").fetchone()[0],1)
            con.close()

    def test_document_register_archives_without_deleting_history(self):
        with tempfile.TemporaryDirectory() as td:
            db_path=Path(td)/"taxo.sqlite3"; self._base_db(db_path)
            con=sqlite3.connect(db_path); con.row_factory=sqlite3.Row
            doc_id=pr.save_employee_document(con,1,{"doc_type":"Посвідчення водія","number":"TEST123","expiry_date":"31.12.2027"})
            con.commit()
            self.assertEqual(len(pr.list_employee_documents(con,1)),1)
            pr.archive_employee_document(con,1,doc_id); con.commit()
            self.assertEqual(len(pr.list_employee_documents(con,1)),0)
            archived=pr.list_employee_documents(con,1,include_archived=True)
            self.assertEqual(len(archived),1)
            self.assertEqual(archived[0]["active"],0)
            con.close()

    def test_appendix5_gap_model_keeps_fields_not_present_in_extract(self):
        required=set(pr.APPENDIX5_PROFILE_FIELDS)
        self.assertIn("education_specialty",required)
        self.assertIn("fitness",required)
        self.assertIn("family_info",required)
        self.assertIn("appointment_act",required)
        self.assertIn("notification_requisites",required)

    def test_r5_checkpoint_identity_remains_historical(self):
        entry=(ROOT/"taxo_app.py").read_text("utf-8")
        feature=(ROOT/"v1045_features.py").read_text("utf-8")
        self.assertIn("install_v1045",entry)
        self.assertIn('APP_VERSION = "10.4-r5"',feature)
        self.assertNotIn("Тестовий Петро Іванович",(ROOT/"personnel_registry.py").read_text("utf-8"))


if __name__=="__main__":
    unittest.main()
