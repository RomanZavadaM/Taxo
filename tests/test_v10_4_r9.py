# -*- coding: utf-8 -*-
import sqlite3
import unittest
from pathlib import Path

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
        active INTEGER NOT NULL DEFAULT 1
    )""")
    registry.ensure_schema_on_connection(con)
    rec.ensure_schema_on_connection(con)
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
        self.assertEqual(
            rec.field_state("employee", "registered_address", "Локальна адреса", ""),
            rec.STATE_UNAVAILABLE,
        )

    def test_empty_local_value_is_safe_fill(self):
        self.assertEqual(
            rec.field_state("employee", "birth_date", "", "1990-01-02"),
            rec.STATE_FILL,
        )

    def test_matching_value_is_green(self):
        self.assertEqual(
            rec.field_state("military", "booking_status", "Заброньовано", "Заброньовано"),
            rec.STATE_MATCH,
        )

    def test_rnokpp_mismatch_is_critical(self):
        self.assertEqual(
            rec.field_state("employee", "rnokpp", "1234567890", "0987654321"),
            rec.STATE_CRITICAL,
        )

    def test_descriptive_mismatch_is_difference(self):
        self.assertEqual(
            rec.field_state("military", "booking_status", "Не заброньовано", "Заброньовано"),
            rec.STATE_DIFFERENCE,
        )


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
        rec.set_decision(
            self.con, self.employee_id, "military", "booking_status", rec.DECISION_FIX_REGISTRY
        )
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
        rec.set_decision(
            self.con, self.employee_id, "military", "booking_status", rec.DECISION_FIX_REGISTRY
        )
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
        rec.accept_registry_value(
            self.con, self.employee_id, "military", "booking_status"
        )
        self.con.commit()
        military = self.con.execute(
            "SELECT * FROM employee_military_profile WHERE employee_id=?", (self.employee_id,)
        ).fetchone()
        self.assertEqual(military["booking_status"], "Заброньовано")
        self.assertEqual(military["account_status"], "На обліку")

    def test_accept_registry_rejects_empty_source(self):
        preview = preview_for(self.employee_id)
        rec.sync_preview_state(self.con, preview)
        with self.assertRaises(ValueError):
            rec.accept_registry_value(
                self.con, self.employee_id, "employee", "registered_address"
            )

    def test_decision_history_is_append_only(self):
        preview = preview_for(self.employee_id, booking="Заброньовано")
        rec.sync_preview_state(self.con, preview)
        rec.set_decision(self.con, self.employee_id, "military", "booking_status", rec.DECISION_DEFER)
        rec.set_decision(self.con, self.employee_id, "military", "booking_status", rec.DECISION_KEEP_TAXO)
        rows = rec.history(self.con, self.employee_id, "military", "booking_status")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["decision"], rec.DECISION_KEEP_TAXO)
        self.assertEqual(rows[1]["decision"], rec.DECISION_DEFER)


class R9IntegrationMarkersTests(unittest.TestCase):
    def test_version_metadata_is_r9(self):
        version = (ROOT / "VERSION.txt").read_text("utf-8")
        self.assertIn("Version: 10.4-r9", version)
        self.assertIn("Порядок №1487, редакція 27.06.2026", version)

    def test_feature_layer_is_installed_after_r8(self):
        entry = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1049_features import install as install_v1049", entry)
        self.assertIn("App = install_v1049(", entry)
        ui = (ROOT / "v1049_features.py").read_text("utf-8")
        self.assertIn('APP_VERSION = "10.4-r9"', ui)
        self.assertIn("квартальна звірка — політика Taxo", ui)

    def test_current_module_declares_2026_legal_marker_without_quarterly_legal_claim(self):
        source = (ROOT / "personnel_reconciliation.py").read_text("utf-8")
        self.assertIn('LEGAL_BASIS = "Порядок №1487, редакція 27.06.2026"', source)
        self.assertNotIn("законодавчий квартальний", source.lower())


if __name__ == "__main__":
    unittest.main()
