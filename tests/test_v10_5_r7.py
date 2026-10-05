# -*- coding: utf-8 -*-
import re
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

import diia_reconciliation as diia
import military_accounting_2026 as military
import version_compat  # 10.10 stable-aware version parsing

ROOT = Path(__file__).resolve().parents[1]


def connect(path):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con


def init_db(path):
    con = connect(path)
    con.execute("""CREATE TABLE employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        last_name TEXT NOT NULL,
        first_name TEXT NOT NULL,
        middle_name TEXT DEFAULT '',
        rnokpp TEXT DEFAULT '',
        active INTEGER NOT NULL DEFAULT 1
    )""")
    con.execute("""CREATE TABLE employee_registry_imports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_kind TEXT NOT NULL,
        source_name TEXT NOT NULL,
        file_sha256 TEXT NOT NULL,
        imported_at TEXT NOT NULL,
        total_rows INTEGER NOT NULL DEFAULT 0,
        matched_rows INTEGER NOT NULL DEFAULT 0,
        updated_rows INTEGER NOT NULL DEFAULT 0,
        skipped_rows INTEGER NOT NULL DEFAULT 0,
        warning_count INTEGER NOT NULL DEFAULT 0,
        mode TEXT NOT NULL DEFAULT 'compare'
    )""")
    con.execute("""CREATE TABLE employee_military_profile(
        employee_id INTEGER PRIMARY KEY REFERENCES employees(id) ON DELETE CASCADE,
        registry_person_id TEXT DEFAULT ''
    )""")
    military.ensure_schema_on_connection(con)
    diia.ensure_schema_on_connection(con)
    con.commit()
    con.close()


class DiiaCycleR7Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name) / "taxo.sqlite")
        init_db(self.db_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_start_cycle_is_local_and_does_not_mark_official_reconciliation(self):
        con = connect(self.db_path)
        cycle = diia.start_cycle(con, edrpou="12345678", year=2026)
        con.commit()
        official = con.execute("SELECT COUNT(*) FROM military_official_reconciliations").fetchone()[0]
        con.close()
        self.assertEqual(cycle["status"], diia.STATUS_DRAFT)
        self.assertEqual(cycle["edrpou_snapshot"], "12345678")
        self.assertEqual(official, 0)

    def test_data_received_requires_real_registry_import(self):
        con = connect(self.db_path)
        cycle = diia.start_cycle(con, edrpou="12345678", year=2026)
        with self.assertRaisesRegex(ValueError, "імпортуйте/звірте XLSX"):
            diia.mark_data_received(con, cycle["id"])
        con.rollback()
        con.close()

    def test_local_preparation_stages_never_set_annual_official_status(self):
        con = connect(self.db_path)
        con.execute(
            """INSERT INTO employee_registry_imports(
                 source_kind,source_name,file_sha256,imported_at,total_rows,mode
               ) VALUES(?,?,?,?,?,?)""",
            ("military_registry_employees", "state.xlsx", "abc", "2026-09-28T10:00:00", 1, "compare"),
        )
        cycle = diia.start_cycle(con, edrpou="12345678", year=2026)
        diia.mark_data_received(con, cycle["id"])
        diia.mark_updates_completed(con, cycle["id"], note="розбіжностей немає")
        status = military.annual_reconciliation_status(con, today=date(2026, 9, 28))
        con.commit()
        con.close()
        self.assertFalse(status["has_authority_reconciliation"])

    def test_external_fixation_is_the_only_step_that_writes_diia_official_record(self):
        con = connect(self.db_path)
        con.execute(
            """INSERT INTO employee_registry_imports(
                 source_kind,source_name,file_sha256,imported_at,total_rows,mode
               ) VALUES(?,?,?,?,?,?)""",
            ("military_registry_employees", "state.xlsx", "abc", "2026-09-28T10:00:00", 1, "compare"),
        )
        cycle = diia.start_cycle(con, edrpou="12345678", year=2026)
        diia.mark_data_received(con, cycle["id"])
        diia.mark_updates_completed(con, cycle["id"], note="заяви опрацьовано")
        fixed = diia.record_external_fixation(
            con,
            cycle["id"],
            date(2026, 9, 28),
            reference="DIIA-TEST-001",
            result="успішно зафіксовано, PDF отримано",
        )
        official = con.execute(
            "SELECT * FROM military_official_reconciliations ORDER BY id DESC LIMIT 1"
        ).fetchone()
        status = military.annual_reconciliation_status(con, today=date(2026, 9, 28))
        con.commit()
        con.close()
        self.assertEqual(fixed["status"], diia.STATUS_FIXED)
        self.assertEqual(official["kind"], military.RECONCILIATION_DIIA)
        self.assertIn("Фіксація відомостей персонального обліку", official["method"])
        self.assertEqual(official["reference"], "DIIA-TEST-001")
        self.assertTrue(status["has_authority_reconciliation"])

    def test_fixation_requires_reference_or_result_and_completed_preparation(self):
        con = connect(self.db_path)
        con.execute(
            """INSERT INTO employee_registry_imports(
                 source_kind,source_name,file_sha256,imported_at,total_rows,mode
               ) VALUES(?,?,?,?,?,?)""",
            ("military_registry_employees", "state.xlsx", "abc", "2026-09-28T10:00:00", 1, "compare"),
        )
        cycle = diia.start_cycle(con, edrpou="12345678", year=2026)
        with self.assertRaisesRegex(ValueError, "отримано"):
            diia.record_external_fixation(con, cycle["id"], date(2026, 9, 28), result="ok")
        diia.mark_data_received(con, cycle["id"])
        with self.assertRaisesRegex(ValueError, "актуалізації"):
            diia.record_external_fixation(con, cycle["id"], date(2026, 9, 28), result="ok")
        diia.mark_updates_completed(con, cycle["id"])
        with self.assertRaisesRegex(ValueError, "реквізит"):
            diia.record_external_fixation(con, cycle["id"], date(2026, 9, 28))
        con.rollback()
        con.close()

    def test_readiness_reports_edrpou_import_and_personnel_coverage_without_changing_data(self):
        con = connect(self.db_path)
        employee_id = con.execute(
            "INSERT INTO employees(last_name,first_name,rnokpp,active) VALUES(?,?,?,1)",
            ("Тестовий", "Іван", "1234567890"),
        ).lastrowid
        con.execute(
            "INSERT INTO employee_military_profile(employee_id,registry_person_id) VALUES(?,?)",
            (employee_id, "REG-001"),
        )
        con.execute(
            """INSERT INTO employee_registry_imports(
                 source_kind,source_name,file_sha256,imported_at,total_rows,mode
               ) VALUES(?,?,?,?,?,?)""",
            ("military_registry_personal", "official.xlsx", "abc", "2026-09-28T10:00:00", 1, "compare"),
        )
        state = diia.readiness(con, edrpou="12345678", today=date(2026, 9, 28))
        con.close()
        self.assertTrue(state["has_edrpou"])
        self.assertTrue(state["has_registry_import"])
        self.assertEqual(state["active_employees"], 1)
        self.assertEqual(state["employees_with_rnokpp"], 1)
        self.assertEqual(state["employees_with_military_profile"], 1)

    def test_service_steps_point_only_to_official_diia_services(self):
        steps = diia.service_steps()
        self.assertEqual([row["key"] for row in steps], ["get", "update", "fix"])
        self.assertTrue(all(row["url"].startswith("https://diia.gov.ua/services/") for row in steps))
        self.assertIn("otrymannia-vidomostei-personalnoho-obliku", steps[0]["url"])
        self.assertIn("aktualizatsiia-vidomostei-personalnoho-obliku", steps[1]["url"])
        self.assertIn("fiksatsiia-vidomostei-personalnoho-obliku", steps[2]["url"])


class R7IntegrationTests(unittest.TestCase):
    def test_candidate_identity_is_r7_or_later(self):
        version = (ROOT / "VERSION.txt").read_text("utf-8")
        match = version_compat.search_version_line(version)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(tuple(map(int, match.groups())), (10, 5, 7))

    def test_r7_is_outermost_entrypoint_and_r6_remains_in_chain(self):
        entry = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1057_features import install as install_v1057", entry)
        self.assertIn("install_v1057(", entry)
        self.assertIn("install_v1056(", entry)

    def test_ui_explicitly_separates_local_preparation_from_external_fact(self):
        source = (ROOT / "v1057_features.py").read_text("utf-8")
        self.assertIn("Звіряння через Дію", source)
        self.assertIn("НЕ надсилає дані в Дію", source)
        self.assertIn("Відомості отримано й імпортовано", source)
        self.assertIn("Актуалізації завершено / не потрібні", source)
        self.assertIn("Записати результат фіксації", source)
        self.assertIn("Фіксації відомостей персонального обліку", source)
        self.assertIn("п. 46 Порядку №1487", source)

    def test_start_guard_requires_r7_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("diia_reconciliation.py", workflow)
        self.assertIn("v1057_features.py", workflow)


if __name__ == "__main__":
    unittest.main()
