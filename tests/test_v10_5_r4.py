# -*- coding: utf-8 -*-
import re
import sqlite3
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

import personnel_registry as registry
import personnel_registry_lossless as lossless
import version_compat  # 10.10 stable-aware version parsing

ROOT = Path(__file__).resolve().parents[1]
lossless.install(registry)

SUMMARY_HEADERS = [
    "Прізвище", "Імʼя", "По батькові", "Стать", "Дата народження", "РНОКПП",
    "Серія паспорту", "Номер паспорту", "Номер ID-картки", "Статус", "Примітка",
]

DETAILED_HEADERS = [
    "Прізвище, ім’я, по батькові",
    "РНОКПП",
    "Серія та номер паспорту",
    "Номер ID картки",
    "Дата народження",
    "Адреса зареєстрованого місця проживання",
    "Адреса фактичного місця проживання",
    "Ідентифікатор військовозобов'язаного",
    "Вид обліку особи",
    "Статус обліку особи",
    "Належність до резервістів",
    "Бронювання",
    "Дата кінця бронювання",
    "Причина відстрочки",
    "Дата закінчення відстрочки",
    "Військове звання",
    "Військово-облікова спеціальність",
    "Найменування ТЦК, органу СБУ, відповідного підрозділу розвідувального органу, в якому перебуває на військовому обліку",
    "Військова служба",
]


def make_xlsx(path, headers, row, title="Інформація"):
    wb = Workbook()
    ws = wb.active
    ws.title = title
    ws.append(headers)
    ws.append(row)
    wb.save(path)
    wb.close()


def connect(path):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    return con


def init_db(path):
    con = connect(path)
    con.execute("""CREATE TABLE employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        last_name TEXT NOT NULL,
        first_name TEXT NOT NULL,
        middle_name TEXT DEFAULT '',
        personnel_no TEXT DEFAULT '',
        position TEXT DEFAULT '',
        employment_date TEXT DEFAULT '',
        dismissal_date TEXT DEFAULT '',
        active INTEGER NOT NULL DEFAULT 1
    )""")
    registry.ensure_schema_on_connection(con)
    con.commit()
    con.close()


class FakeCore:
    def __init__(self, db_path):
        self.db_path = db_path

    def db(self):
        return connect(self.db_path)


class LosslessParserR4Tests(unittest.TestCase):
    def test_summary_preserves_all_11_source_columns_and_rejected_document_placeholders(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "summary.xlsx"
            make_xlsx(path, SUMMARY_HEADERS, [
                "Тестовий", "Олег", "Один", "Чоловіча", "01.02.1990", "1234567890",
                "17", "17", "17", "Не заброньовано", "Має відстрочку до 31.12.2026",
            ])
            parsed = registry.parse_registry_xlsx(path)
            self.assertEqual(parsed["source_kind"], registry.SOURCE_SUMMARY)
            item = parsed["rows"][0]
            self.assertEqual(len(item["raw_fields"]), 11)
            self.assertEqual(item["military"]["registry_note"], "Має відстрочку до 31.12.2026")
            self.assertEqual(item["personal"]["passport_series"], "")
            self.assertEqual(item["personal"]["passport_number"], "")
            self.assertEqual(item["personal"]["id_card_number"], "")
            raw = {field["source_header"]: field for field in item["raw_fields"]}
            self.assertEqual(raw["Серія паспорту"]["raw_value"], "17")
            self.assertEqual(raw["Серія паспорту"]["transfer_status"], lossless.STATUS_REJECTED)
            self.assertEqual(raw["Номер паспорту"]["transfer_status"], lossless.STATUS_REJECTED)
            self.assertEqual(raw["Номер ID-картки"]["transfer_status"], lossless.STATUS_REJECTED)
            self.assertEqual(raw["Примітка"]["transfer_status"], lossless.STATUS_MAPPED)

    def test_detailed_preserves_all_19_official_columns(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "detailed.xlsx"
            make_xlsx(path, DETAILED_HEADERS, [
                "Тестовий Олег Один", "1234567890", "АА123456", "123456789", "01.02.1990",
                "м. Тест, вул. Перша, 1", "м. Тест, вул. Друга, 2", "REG-001",
                "військовозобов'язаний", "на обліку", "ні", "не заброньовано", "",
                "", "", "солдат", "123456", "Тестовий РТЦК та СП", "не проходить",
            ], title="Відомості персонального обліку")
            parsed = registry.parse_registry_xlsx(path)
            self.assertEqual(parsed["source_kind"], registry.SOURCE_DETAILED)
            item = parsed["rows"][0]
            self.assertEqual(len(item["raw_fields"]), 19)
            headers = [field["source_header"] for field in item["raw_fields"]]
            self.assertEqual(headers, DETAILED_HEADERS)
            self.assertEqual(item["personal"]["passport_series"], "АА")
            self.assertEqual(item["personal"]["passport_number"], "123456")
            self.assertEqual(item["military"]["registry_person_id"], "REG-001")
            raw = {field["source_header"]: field for field in item["raw_fields"]}
            self.assertEqual(raw["РНОКПП"]["transfer_status"], lossless.STATUS_MAPPED)
            self.assertEqual(raw["Прізвище, ім’я, по батькові"]["transfer_status"], lossless.STATUS_IDENTITY)


class LosslessApplyR4Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name) / "taxo.sqlite")
        init_db(self.db_path)
        self.core = FakeCore(self.db_path)
        con = self.core.db()
        con.execute(
            """INSERT INTO employees(last_name,first_name,middle_name,active,rnokpp)
               VALUES(?,?,?,?,?)""",
            ("Тестовий", "Олег", "Один", 1, "1234567890"),
        )
        con.commit()
        self.employee_id = con.execute("SELECT id FROM employees").fetchone()[0]
        con.close()

    def tearDown(self):
        self.tmp.cleanup()

    def _summary(self, filename, note, passport="17", id_card="17"):
        path = Path(self.tmp.name) / filename
        make_xlsx(path, SUMMARY_HEADERS, [
            "Тестовий", "Олег", "Один", "Чоловіча", "01.02.1990", "1234567890",
            passport, passport, id_card, "Не заброньовано", note,
        ])
        return path

    def test_apply_saves_raw_snapshot_but_keeps_invalid_passport_out_of_canonical_fields(self):
        path = self._summary("q3.xlsx", "Має відстрочку", passport="17", id_card="17")
        preview = registry.preview_registry_import(self.core, path)
        result = registry.apply_registry_import(self.core, preview, mode=registry.IMPORT_FILL_EMPTY)
        self.assertGreater(result["import_id"], 0)
        con = self.core.db()
        employee = con.execute("SELECT * FROM employees WHERE id=?", (self.employee_id,)).fetchone()
        military = con.execute("SELECT * FROM employee_military_profile WHERE employee_id=?", (self.employee_id,)).fetchone()
        raw = con.execute(
            "SELECT * FROM employee_registry_raw_fields WHERE employee_id=? ORDER BY field_order",
            (self.employee_id,),
        ).fetchall()
        con.close()
        self.assertEqual(employee["passport_series"], "")
        self.assertEqual(employee["passport_number"], "")
        self.assertEqual(employee["id_card_number"], "")
        self.assertEqual(military["registry_note"], "Має відстрочку")
        self.assertEqual(len(raw), 11)
        rejected = [row for row in raw if row["transfer_status"] == lossless.STATUS_REJECTED]
        self.assertEqual({row["source_header"] for row in rejected}, {"Серія паспорту", "Номер паспорту", "Номер ID-картки"})
        self.assertTrue(all(row["raw_value"] == "17" for row in rejected))

    def test_blank_newer_registry_note_never_clears_existing_note(self):
        first = self._summary("q3.xlsx", "Офіційна примітка")
        preview = registry.preview_registry_import(self.core, first)
        registry.apply_registry_import(self.core, preview, mode=registry.IMPORT_UPDATE)
        second = self._summary("q4.xlsx", "")
        preview2 = registry.preview_registry_import(self.core, second)
        registry.apply_registry_import(self.core, preview2, mode=registry.IMPORT_UPDATE)
        con = self.core.db()
        military = con.execute("SELECT * FROM employee_military_profile WHERE employee_id=?", (self.employee_id,)).fetchone()
        latest = lossless.latest_raw_snapshot(con, self.employee_id)
        con.close()
        self.assertEqual(military["registry_note"], "Офіційна примітка")
        note_row = next(row for row in latest if row["source_header"] == "Примітка")
        self.assertEqual(note_row["raw_value"], "")
        self.assertEqual(note_row["transfer_status"], lossless.STATUS_BLANK)

    def test_latest_raw_snapshot_uses_newest_import_only(self):
        first = self._summary("q3.xlsx", "Перша примітка")
        registry.apply_registry_import(self.core, registry.preview_registry_import(self.core, first), mode=registry.IMPORT_COMPARE)
        second = self._summary("q4.xlsx", "Друга примітка")
        registry.apply_registry_import(self.core, registry.preview_registry_import(self.core, second), mode=registry.IMPORT_COMPARE)
        con = self.core.db()
        rows = lossless.latest_raw_snapshot(con, self.employee_id)
        con.close()
        self.assertEqual(len(rows), 11)
        note_row = next(row for row in rows if row["source_header"] == "Примітка")
        self.assertEqual(note_row["raw_value"], "Друга примітка")


class R4IntegrationTests(unittest.TestCase):
    def test_r4_remains_in_install_chain_after_r3(self):
        entry = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1054_features import install as install_v1054", entry)
        self.assertIn("install_v1054(", entry)
        self.assertIn("install_v1053(", entry)

    def test_r4_module_keeps_historical_identity(self):
        feature = (ROOT / "v1054_features.py").read_text("utf-8")
        model = (ROOT / "personnel_registry_lossless.py").read_text("utf-8")
        self.assertIn('APP_VERSION = "10.5-r4"', feature)
        self.assertIn('APP_VERSION = "10.5-r4"', model)
        self.assertIn("Оригінал держреєстру", feature)

    def test_current_version_is_r4_or_later(self):
        version = (ROOT / "VERSION.txt").read_text("utf-8")
        match = version_compat.search_version_line(version)
        self.assertIsNotNone(match)
        major, minor, revision = map(int, match.groups())
        self.assertTrue((major, minor, revision) >= (10, 5, 4))

    def test_start_guard_requires_lossless_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("personnel_registry_lossless.py", workflow)
        self.assertIn("v1054_features.py", workflow)

    def test_r4_keeps_registry_note_as_first_class_military_field(self):
        lossless.install(registry)
        self.assertEqual(registry.MILITARY_FIELD_LABELS["registry_note"], "Примітка державного витягу")


if __name__ == "__main__":
    unittest.main()
