# -*- coding: utf-8 -*-
import re
import sqlite3
import tempfile
import unittest
from pathlib import Path

import personnel_registry as personnel
import personnel_registry_lossless as lossless
import registry_working_data as working
import vehicle_reconciliation as reconciliation

ROOT = Path(__file__).resolve().parents[1]


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
        active INTEGER NOT NULL DEFAULT 1
    )""")
    con.execute("""CREATE TABLE vehicles(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        plate TEXT DEFAULT '',
        year TEXT DEFAULT '',
        active INTEGER NOT NULL DEFAULT 1
    )""")
    lossless.install(personnel)
    working.ensure_personnel_schema(con)
    working.ensure_vehicle_schema(con)
    con.commit()
    con.close()


class RegistryWorkingDataR6Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name) / "taxo.sqlite")
        init_db(self.db_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_employee_working_edit_does_not_rewrite_raw_state_snapshot(self):
        con = connect(self.db_path)
        cur = con.execute(
            "INSERT INTO employees(last_name,first_name,middle_name,active) VALUES(?,?,?,1)",
            ("Тестовий", "Олег", "Один"),
        )
        employee_id = cur.lastrowid
        con.execute("INSERT OR IGNORE INTO employee_military_profile(employee_id,registry_person_id,military_rank) VALUES(?,?,?)",
                    (employee_id, "REG-001", "солдат"))
        import_id = con.execute(
            """INSERT INTO employee_registry_imports(source_kind,source_name,file_sha256,imported_at,total_rows,mode)
               VALUES(?,?,?,?,?,?)""",
            (personnel.SOURCE_DETAILED, "state.xlsx", "abc", "2026-09-28T08:00:00", 1, personnel.IMPORT_FILL_EMPTY),
        ).lastrowid
        con.execute(
            """INSERT INTO employee_registry_raw_fields(
                 import_id,employee_id,source_kind,source_name,file_sha256,source_row,field_order,field_key,
                 source_header,raw_value,canonical_scope,canonical_field,canonical_value,transfer_status,transfer_note,imported_at
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (import_id, employee_id, personnel.SOURCE_DETAILED, "state.xlsx", "abc", 2, 0,
             "військове звання", "Військове звання", "солдат", "military", "military_rank",
             "солдат", lossless.STATUS_MAPPED, "", "2026-09-28T08:00:00"),
        )
        con.commit()

        before = lossless.latest_raw_snapshot(con, employee_id)
        self.assertEqual(before[0]["raw_value"], "солдат")
        working.save_employee_working_data(
            con, employee_id,
            personal_values={"actual_address": "м. Тест, вул. Нова, 1"},
            military_values={"military_rank": "старший солдат", "registry_note": "робоча примітка"},
        )
        con.commit()
        data = working.employee_working_data(con, employee_id)
        after = lossless.latest_raw_snapshot(con, employee_id)
        con.close()

        self.assertEqual(data["personal"]["actual_address"], "м. Тест, вул. Нова, 1")
        self.assertEqual(data["military"]["military_rank"], "старший солдат")
        self.assertEqual(data["military"]["registry_note"], "робоча примітка")
        self.assertEqual(after[0]["raw_value"], "солдат")
        self.assertEqual(after[0]["canonical_value"], "солдат")

    def test_vehicle_working_edit_keeps_last_registry_value_for_next_reconciliation(self):
        con = connect(self.db_path)
        vehicle_id = con.execute(
            "INSERT INTO vehicles(name,plate,year,active) VALUES(?,?,?,1)",
            ("Автобус", "BC1234AA", "2015"),
        ).lastrowid
        working.ensure_vehicle_schema(con)
        reconciliation._upsert_current_state(
            con,
            {
                "vehicle_id": vehicle_id,
                "field": "make",
                "local": "BAZ",
                "registry": "Еталон",
                "state": reconciliation.STATE_DIFFERENCE,
                "source_kind": "shlyakh_vehicle_registry",
                "source_name": "shlyakh.xlsx",
                "file_sha256": "abc",
                "source_row": 2,
            },
            "2026-09-28T08:00:00",
        )
        con.execute("UPDATE vehicles SET make='BAZ',registry_last_source_name='shlyakh.xlsx' WHERE id=?", (vehicle_id,))
        con.commit()

        working.save_vehicle_working_value(con, vehicle_id, "make", "БАЗ А079")
        con.commit()
        data = working.vehicle_working_data(con, vehicle_id)
        row = next(item for item in data["fields"] if item["field"] == "make")
        self.assertEqual(row["working_value"], "БАЗ А079")
        self.assertEqual(row["registry_value"], "Еталон")
        self.assertEqual(row["state"], reconciliation.STATE_DIFFERENCE)

        reconciliation.accept_registry_value(con, vehicle_id, "make")
        con.commit()
        data2 = working.vehicle_working_data(con, vehicle_id)
        row2 = next(item for item in data2["fields"] if item["field"] == "make")
        con.close()
        self.assertEqual(row2["working_value"], "Еталон")
        self.assertEqual(row2["registry_value"], "Еталон")
        self.assertEqual(row2["state"], reconciliation.STATE_MATCH)

    def test_copy_text_is_ready_for_document_copy_paste(self):
        con = connect(self.db_path)
        employee_id = con.execute(
            "INSERT INTO employees(last_name,first_name,middle_name,active) VALUES(?,?,?,1)",
            ("Тестовий", "Олег", "Один"),
        ).lastrowid
        working.ensure_personnel_schema(con)
        working.save_employee_working_data(
            con, employee_id,
            personal_values={"rnokpp": "1234567890"},
            military_values={"military_rank": "солдат", "military_specialty": "123456"},
        )
        con.commit()
        text = working.employee_copy_text(con, employee_id)
        con.close()
        self.assertIn("Тестовий Олег Один", text)
        self.assertIn("РНОКПП: 1234567890", text)
        self.assertIn("Військове звання: солдат", text)
        self.assertIn("Військово-облікова спеціальність: 123456", text)


class R6IntegrationTests(unittest.TestCase):
    def test_candidate_identity_is_r6_or_later(self):
        version = (ROOT / "VERSION.txt").read_text("utf-8")
        match = re.search(r"Version:\s+(\d+)\.(\d+)-r(\d+)", version)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(tuple(map(int, match.groups())), (10, 5, 6))

    def test_r6_is_outermost_entrypoint(self):
        entry = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1056_features import install as install_v1056", entry)
        self.assertIn("App = install_v1056(", entry)
        self.assertIn("install_v1055(", entry)

    def test_ui_exposes_edit_and_copy_for_both_registry_domains(self):
        source = (ROOT / "v1056_features.py").read_text("utf-8")
        self.assertIn("Військові дані / Дія", source)
        self.assertIn("Редагувати поле", source)
        self.assertIn("Копіювати всю картку", source)
        self.assertIn("Редагувати робоче поле", source)
        self.assertIn("Копіювати всі дані", source)
        self.assertIn("Оригінальний державний витяг лишається окремим незмінним знімком", source)
        self.assertIn("Останній витяг", source)

    def test_2026_reconciliation_ui_uses_diia_as_normal_electronic_path(self):
        source = (ROOT / "v1056_features.py").read_text("utf-8")
        self.assertIn("постанови КМУ №812 від 10.06.2026", source)
        self.assertIn("Порталу Дія або через кабінет персонального обліку", source)
        self.assertIn("DIIA_METHOD = \"Портал Дія\"", source)
        self.assertIn("імпорт XLSX", source)
        self.assertIn("не ставить відмітку «звірено»", source)

    def test_enterprise_transport_primary_ui_is_statement_not_military_unit_accounting(self):
        source = (ROOT / "v1056_features.py").read_text("utf-8")
        self.assertIn("Відомість ТЦК 20.06 / 20.12", source)
        self.assertIn("Це звіт підприємства, а не облік військової частини", source)
        self.assertIn("до 20 червня та 20 грудня", source)

    def test_start_guard_requires_r6_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("registry_working_data.py", workflow)
        self.assertIn("v1056_features.py", workflow)


if __name__ == "__main__":
    unittest.main()
