# -*- coding: utf-8 -*-
import sqlite3
import unittest
from datetime import date, datetime
from pathlib import Path

import military_accounting_2026 as military
import personnel_registry as registry
import personnel_reconciliation as rec

ROOT = Path(__file__).resolve().parents[1]


def make_db():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        last_name TEXT NOT NULL,
        first_name TEXT NOT NULL,
        middle_name TEXT DEFAULT '',
        employment_date TEXT DEFAULT '',
        dismissal_date TEXT DEFAULT '',
        active INTEGER NOT NULL DEFAULT 1
    )""")
    registry.ensure_schema_on_connection(con)
    rec.ensure_schema_on_connection(con)
    military.ensure_schema_on_connection(con)
    return con


def preview_for(employee_id, rnokpp="1234567890", booking="Заброньовано", account_status="На обліку"):
    item = {
        "last_name": "Тестовий",
        "first_name": "Працівник",
        "middle_name": "Один",
        "full_name": "Тестовий Працівник Один",
        "personal": {
            "rnokpp": rnokpp,
            "birth_date": "1990-01-02",
            "registered_address": "",
        },
        "military": {
            "booking_status": booking,
            "account_status": account_status,
            "registry_person_id": "REG-001",
        },
        "documents": [],
        "warnings": [],
        "source_row": 2,
    }
    return {
        "file_sha256": "abc123",
        "parsed": {
            "source_kind": registry.SOURCE_DETAILED,
            "source_name": "synthetic.xlsx",
            "rows": [item],
        },
        "plan": [{
            "item": item,
            "employee_id": employee_id,
            "employee_name": item["full_name"],
            "match_quality": "rnokpp",
            "status": "update",
            "changes": [],
            "notes": [],
        }],
        "local_only": [],
    }


class FieldStateR9Tests(unittest.TestCase):
    def test_empty_registry_value_never_means_clear(self):
        self.assertEqual(rec.field_state("employee", "registered_address", "Локальна адреса", ""), rec.STATE_UNAVAILABLE)

    def test_empty_local_value_is_safe_fill(self):
        self.assertEqual(rec.field_state("employee", "birth_date", "", "1990-01-02"), rec.STATE_FILL)

    def test_matching_value_is_green(self):
        self.assertEqual(rec.field_state("military", "booking_status", "Заброньовано", "Заброньовано"), rec.STATE_MATCH)

    def test_rnokpp_mismatch_is_critical(self):
        self.assertEqual(rec.field_state("employee", "rnokpp", "1234567890", "0987654321"), rec.STATE_CRITICAL)

    def test_descriptive_mismatch_is_difference(self):
        self.assertEqual(rec.field_state("military", "booking_status", "Не заброньовано", "Заброньовано"), rec.STATE_DIFFERENCE)


class DecisionPersistenceR9Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()
        cur = self.con.execute(
            "INSERT INTO employees(last_name,first_name,middle_name,active,rnokpp,birth_date) VALUES(?,?,?,?,?,?)",
            ("Тестовий", "Працівник", "Один", 1, "1234567890", "1990-01-02"),
        )
        self.employee_id = cur.lastrowid
        self.con.execute(
            "INSERT INTO employee_military_profile(employee_id,booking_status,account_status,registry_person_id) VALUES(?,?,?,?)",
            (self.employee_id, "Не заброньовано", "На обліку", "REG-001"),
        )
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def test_fix_registry_decision_survives_next_mismatching_extract(self):
        preview = preview_for(self.employee_id, booking="Заброньовано")
        rec.sync_preview_state(self.con, preview)
        rec.set_decision(self.con, self.employee_id, "military", "booking_status", rec.DECISION_FIX_REGISTRY)
        self.con.commit()
        rec.sync_preview_state(self.con, preview)
        row = self.con.execute(
            "SELECT * FROM employee_registry_field_state WHERE employee_id=? AND scope='military' AND field_name='booking_status'",
            (self.employee_id,),
        ).fetchone()
        self.assertEqual(row["decision"], rec.DECISION_FIX_REGISTRY)
        self.assertEqual(row["decision_active"], 1)
        self.assertEqual(row["state"], rec.STATE_DIFFERENCE)

    def test_fix_registry_auto_resolves_when_new_extract_matches_taxo(self):
        preview = preview_for(self.employee_id, booking="Заброньовано")
        rec.sync_preview_state(self.con, preview)
        rec.set_decision(self.con, self.employee_id, "military", "booking_status", rec.DECISION_FIX_REGISTRY)
        self.con.commit()
        corrected = preview_for(self.employee_id, booking="Не заброньовано")
        rec.sync_preview_state(self.con, corrected)
        row = self.con.execute(
            "SELECT * FROM employee_registry_field_state WHERE employee_id=? AND scope='military' AND field_name='booking_status'",
            (self.employee_id,),
        ).fetchone()
        self.assertEqual(row["state"], rec.STATE_MATCH)
        self.assertEqual(row["decision"], rec.DECISION_RESOLVED)
        self.assertEqual(row["decision_active"], 0)
        self.assertTrue(row["resolved_at"])

    def test_accept_registry_changes_only_selected_field(self):
        preview = preview_for(self.employee_id, booking="Заброньовано")
        rec.sync_preview_state(self.con, preview)
        rec.accept_registry_value(self.con, self.employee_id, "military", "booking_status")
        self.con.commit()
        row = self.con.execute("SELECT * FROM employee_military_profile WHERE employee_id=?", (self.employee_id,)).fetchone()
        self.assertEqual(row["booking_status"], "Заброньовано")
        self.assertEqual(row["account_status"], "На обліку")

    def test_accept_registry_rejects_empty_source(self):
        preview = preview_for(self.employee_id)
        rec.sync_preview_state(self.con, preview)
        with self.assertRaises(ValueError):
            rec.accept_registry_value(self.con, self.employee_id, "employee", "registered_address")

    def test_decision_history_is_append_only(self):
        preview = preview_for(self.employee_id, booking="Заброньовано")
        rec.sync_preview_state(self.con, preview)
        rec.set_decision(self.con, self.employee_id, "military", "booking_status", rec.DECISION_DEFER)
        rec.set_decision(self.con, self.employee_id, "military", "booking_status", rec.DECISION_KEEP_TAXO)
        rows = rec.history(self.con, self.employee_id, "military", "booking_status")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["decision"], rec.DECISION_KEEP_TAXO)
        self.assertEqual(rows[1]["decision"], rec.DECISION_DEFER)


class MilitaryAccountingJournalR9Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()

    def tearDown(self):
        self.con.close()

    def add_employee(self, employment_date="", dismissal_date=""):
        cur = self.con.execute(
            "INSERT INTO employees(last_name,first_name,middle_name,employment_date,dismissal_date,active) VALUES(?,?,?,?,?,?)",
            ("Тест", "Військовий", "Облік", employment_date, dismissal_date, 1),
        )
        return cur.lastrowid

    def test_historical_hire_does_not_create_false_overdue_task(self):
        self.add_employee("2020-01-15", "")
        military.sync_recent_employment_actions(self.con)
        self.assertEqual(len(military.list_actions(self.con)), 0)

    def test_new_hire_waits_for_order_date_before_calculating_deadline(self):
        employee_id = self.add_employee("2026-09-27", "")
        military.sync_recent_employment_actions(self.con)
        row = military.list_actions(self.con, employee_id=employee_id)[0]
        self.assertEqual(row["action_type"], military.ACTION_HIRE_NOTICE)
        self.assertEqual(row["basis_date"], "")
        self.assertEqual(row["due_date"], "")
        self.assertIn("дату наказу", row["note"])

    def test_order_date_calculates_seven_day_notice_deadline(self):
        employee_id = self.add_employee("2026-09-27", "")
        military.sync_recent_employment_actions(self.con)
        row = military.list_actions(self.con, employee_id=employee_id)[0]
        military.set_notice_order_date(self.con, row["id"], "2026-09-26")
        updated = military.list_actions(self.con, employee_id=employee_id)[0]
        self.assertEqual(updated["basis_date"], "2026-09-26")
        self.assertEqual(updated["due_date"], "2026-10-03")

    def test_new_dismissal_also_waits_for_order_date(self):
        employee_id = self.add_employee("2020-01-15", "2026-09-28")
        military.sync_recent_employment_actions(self.con)
        row = military.list_actions(self.con, employee_id=employee_id)[0]
        self.assertEqual(row["action_type"], military.ACTION_DISMISSAL_NOTICE)
        self.assertEqual(row["due_date"], "")

    def test_personal_data_change_uses_five_day_action_from_documents_date(self):
        employee_id = self.add_employee()
        military.add_personal_data_update_action(self.con, employee_id, date(2026, 9, 27))
        row = military.list_actions(self.con, employee_id=employee_id)[0]
        self.assertEqual(row["action_type"], military.ACTION_PERSONAL_DATA_UPDATE)
        self.assertEqual(row["basis_date"], "2026-09-27")
        self.assertEqual(row["due_date"], "2026-10-02")

    def test_completion_persists(self):
        employee_id = self.add_employee("2026-09-27", "")
        military.sync_recent_employment_actions(self.con)
        row = military.list_actions(self.con, employee_id=employee_id)[0]
        military.complete_action(self.con, row["id"], channel="Дія", reference="TEST-REF")
        done = military.list_actions(self.con, employee_id=employee_id)[0]
        self.assertEqual(done["status"], military.STATUS_DONE)
        self.assertEqual(done["channel"], "Дія")
        self.assertEqual(done["reference"], "TEST-REF")

    def test_hire_document_two_calendar_days_before_is_safely_within_window(self):
        self.assertEqual(
            military.hire_document_window_status("2026-09-30", datetime(2026, 9, 28, 12, 0)),
            "ok",
        )

    def test_hire_document_exactly_three_calendar_days_before_needs_exact_time(self):
        self.assertEqual(
            military.hire_document_window_status("2026-09-30", datetime(2026, 9, 27, 12, 0)),
            "needs_exact_time",
        )

    def test_hire_document_four_days_before_is_outside(self):
        self.assertEqual(
            military.hire_document_window_status("2026-09-30", datetime(2026, 9, 26, 12, 0)),
            "outside",
        )

    def test_hire_document_check_rejects_definitely_outside_window(self):
        employee_id = self.add_employee("2026-09-30", "")
        with self.assertRaises(ValueError):
            military.record_hire_document_check(
                self.con, employee_id, "2026-09-30", datetime(2026, 9, 30, 9, 0),
                datetime(2026, 9, 26, 12, 0), method="Дія",
            )

    def test_official_reconciliation_is_independent_of_registry_import(self):
        employee_id = self.add_employee()
        self.con.execute(
            "INSERT INTO employee_registry_imports(source_kind,source_name,file_sha256,imported_at,total_rows,mode) VALUES(?,?,?,?,?,?)",
            (registry.SOURCE_DETAILED, "quarter.xlsx", "sha", "2026-09-27T10:00:00", 1, registry.IMPORT_COMPARE),
        )
        status = military.annual_reconciliation_status(self.con, today=date(2026, 9, 27))
        self.assertEqual(status["count"], 0)
        self.assertFalse(status["has_document_reconciliation"])
        self.assertFalse(status["has_authority_reconciliation"])
        self.assertIsNotNone(employee_id)

    def test_official_reconciliation_log_sets_annual_status_only_after_record(self):
        military.record_official_reconciliation(
            self.con, "2026-09-27", military.RECONCILIATION_DIIA,
            method="Дія", authority="ТЦК", reference="SYNTHETIC",
        )
        status = military.annual_reconciliation_status(self.con, today=date(2026, 9, 27))
        self.assertEqual(status["count"], 1)
        self.assertTrue(status["has_authority_reconciliation"])
        self.assertFalse(status["has_document_reconciliation"])


class R9IntegrationMarkersTests(unittest.TestCase):
    def test_r9_historical_metadata_remains_immutable(self):
        notes = (ROOT / "docs/releases/RELEASE_NOTES_v10_4_r9.md").read_text("utf-8")
        self.assertIn("Taxo 10.4-r9", notes)
        self.assertIn("Порядок №1487, редакція 27.06.2026", notes)
        ui = (ROOT / "v1049_features.py").read_text("utf-8")
        self.assertIn('APP_VERSION = "10.4-r9"', ui)

    def test_r9_feature_layer_remains_in_install_chain_after_later_revisions(self):
        entry = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1049_features import install as install_v1049", entry)
        self.assertIn("from military_accounting_ui import install as install_military_accounting_ui", entry)
        self.assertIn("install_military_accounting_ui(", entry)
        self.assertIn("install_v1049(", entry)
        ui = (ROOT / "v1049_features.py").read_text("utf-8")
        self.assertIn('APP_VERSION = "10.4-r9"', ui)
        self.assertIn("квартальна звірка — політика Taxo", ui)

    def test_current_module_declares_2026_legal_marker_without_quarterly_legal_claim(self):
        source = (ROOT / "personnel_reconciliation.py").read_text("utf-8")
        legal = (ROOT / "military_accounting_2026.py").read_text("utf-8")
        self.assertIn('LEGAL_BASIS = "Порядок №1487, редакція 27.06.2026"', source)
        self.assertIn("HIRE_DOCUMENT_MAX_AGE_HOURS = 72", legal)
        self.assertIn("EMPLOYMENT_NOTICE_DAYS = 7", legal)
        self.assertIn("PERSONAL_LIST_UPDATE_DAYS = 5", legal)
        self.assertIn("ANNUAL_RECONCILIATION_MINIMUM = 1", legal)
        self.assertIn("семиденний строк обчислюється від дня видання наказу", legal)
        self.assertNotIn("законодавчий квартальний", (source + legal).lower())

    def test_quarterly_registry_and_official_journal_are_separate_in_ui(self):
        ui = (ROOT / "military_accounting_ui.py").read_text("utf-8")
        self.assertIn("Державний XLSX — внутрішня політика Taxo", ui)
        self.assertIn("Офіційне військове звіряння — Порядок №1487", ui)
        self.assertIn("не заповнюється автоматично з квартального XLSX", ui)


if __name__ == "__main__":
    unittest.main()
