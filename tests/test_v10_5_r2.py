# -*- coding: utf-8 -*-
import sqlite3
import unittest
from pathlib import Path

import vehicle_reconciliation as rec
import vehicle_registry as registry

ROOT = Path(__file__).resolve().parents[1]


def make_db():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE vehicles(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        plate TEXT DEFAULT '',
        make_model TEXT DEFAULT '',
        active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT DEFAULT ''
    )""")
    rec.ensure_schema_on_connection(con)
    return con


def add_vehicle(con, *, plate="AA1234BB", vin="VIN00000000000001", make="MAN", model="Lion's City"):
    cur = con.execute(
        "INSERT INTO vehicles(name,plate,make_model,active,created_at,vin,make,model) VALUES(?,?,?,?,?,?,?,?)",
        ("Автобус", plate, "%s %s" % (make, model), 1, "2026-09-28T00:00:00", vin, make, model),
    )
    return int(cur.lastrowid)


def preview_for(vehicle_id, **overrides):
    item = {
        "registry_vehicle_type": "Автобус",
        "plate": "AA1234BB",
        "registry_carrier": "12345678 Тестовий перевізник",
        "registry_carrier_edrpou": "12345678",
        "registry_status": "На обліку",
        "vin": "VIN00000000000001",
        "make": "MAN",
        "model": "Lion's City",
        "gross_mass_kg": "18000",
        "euro_class": "EURO-5",
        "ecmt_euro_class": "",
        "ecmt_valid_from": "",
        "ecmt_certificate_no": "",
        "source_row": 2,
    }
    item.update(overrides)
    return {
        "file_sha256": "synthetic-sha",
        "parsed": {
            "source_kind": registry.SOURCE_KIND,
            "source_name": "synthetic-shlyakh.xlsx",
            "rows": [item],
        },
        "plan": [{
            "item": item,
            "vehicle_id": vehicle_id,
            "vehicle_name": "Автобус — AA1234BB",
            "match_quality": "vin",
            "status": "difference",
            "changes": [],
            "notes": [],
        }],
        "local_only": [],
    }


class VehicleFieldStateR2Tests(unittest.TestCase):
    def test_empty_registry_never_means_clear(self):
        self.assertEqual(rec.field_state("euro_class", "EURO-5", ""), rec.STATE_UNAVAILABLE)

    def test_empty_local_value_is_safe_fill(self):
        self.assertEqual(rec.field_state("gross_mass_kg", "", "18000"), rec.STATE_FILL)

    def test_normalized_plate_match_is_green(self):
        self.assertEqual(rec.field_state("plate", "АА 1234 ВВ", "AA1234BB"), rec.STATE_MATCH)

    def test_gross_mass_normalization_matches(self):
        self.assertEqual(rec.field_state("gross_mass_kg", "18 000", "18000.0"), rec.STATE_MATCH)

    def test_vin_mismatch_is_critical(self):
        self.assertEqual(rec.field_state("vin", "VIN00000000000001", "VIN00000000000002"), rec.STATE_CRITICAL)

    def test_plate_mismatch_is_critical(self):
        self.assertEqual(rec.field_state("plate", "AA1234BB", "BC5678AA"), rec.STATE_CRITICAL)

    def test_descriptive_mismatch_is_yellow_difference(self):
        self.assertEqual(rec.field_state("model", "Lion's City", "A21"), rec.STATE_DIFFERENCE)


class VehicleDecisionPersistenceR2Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()
        self.vehicle_id = add_vehicle(self.con)
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def _sync(self, **overrides):
        preview = preview_for(self.vehicle_id, **overrides)
        rec.sync_preview_state(self.con, preview)
        self.con.commit()
        return preview

    def test_sync_persists_every_official_field_including_blank(self):
        self._sync()
        rows = rec.current_fields(self.con, vehicle_id=self.vehicle_id)
        self.assertEqual(len(rows), len(registry.FIELD_LABELS))
        ecmt = next(row for row in rows if row["field_name"] == "ecmt_certificate_no")
        self.assertEqual(ecmt["state"], rec.STATE_UNAVAILABLE)

    def test_fix_registry_survives_next_mismatching_extract(self):
        self._sync(model="A21")
        rec.set_decision(self.con, self.vehicle_id, "model", rec.DECISION_FIX_REGISTRY)
        self.con.commit()
        self._sync(model="A23")
        row = self.con.execute(
            "SELECT * FROM vehicle_registry_field_state WHERE vehicle_id=? AND field_name='model'",
            (self.vehicle_id,),
        ).fetchone()
        self.assertEqual(row["decision"], rec.DECISION_FIX_REGISTRY)
        self.assertEqual(row["decision_active"], 1)
        self.assertEqual(row["state"], rec.STATE_DIFFERENCE)

    def test_fix_registry_auto_resolves_when_new_extract_matches_taxo(self):
        self._sync(model="A21")
        rec.set_decision(self.con, self.vehicle_id, "model", rec.DECISION_FIX_REGISTRY)
        self.con.commit()
        self._sync(model="Lion's City")
        row = self.con.execute(
            "SELECT * FROM vehicle_registry_field_state WHERE vehicle_id=? AND field_name='model'",
            (self.vehicle_id,),
        ).fetchone()
        self.assertEqual(row["state"], rec.STATE_MATCH)
        self.assertEqual(row["decision"], rec.DECISION_RESOLVED)
        self.assertEqual(row["decision_active"], 0)
        self.assertTrue(row["resolved_at"])
        history = rec.history(self.con, self.vehicle_id, "model")
        self.assertEqual(history[0]["decision"], rec.DECISION_RESOLVED)

    def test_accept_registry_updates_only_selected_field(self):
        self._sync(model="A21", euro_class="EURO-6")
        rec.accept_registry_value(self.con, self.vehicle_id, "model")
        self.con.commit()
        vehicle = self.con.execute("SELECT * FROM vehicles WHERE id=?", (self.vehicle_id,)).fetchone()
        self.assertEqual(vehicle["model"], "A21")
        self.assertEqual(vehicle["euro_class"], "")
        row = self.con.execute(
            "SELECT * FROM vehicle_registry_field_state WHERE vehicle_id=? AND field_name='model'",
            (self.vehicle_id,),
        ).fetchone()
        self.assertEqual(row["state"], rec.STATE_MATCH)
        self.assertEqual(row["decision"], rec.DECISION_ACCEPT_REGISTRY)

    def test_accept_registry_rejects_empty_source(self):
        self._sync(ecmt_certificate_no="")
        with self.assertRaises(ValueError):
            rec.accept_registry_value(self.con, self.vehicle_id, "ecmt_certificate_no")

    def test_decision_history_is_append_only(self):
        self._sync(model="A21")
        rec.set_decision(self.con, self.vehicle_id, "model", rec.DECISION_DEFER)
        rec.set_decision(self.con, self.vehicle_id, "model", rec.DECISION_KEEP_TAXO)
        self.con.commit()
        rows = rec.history(self.con, self.vehicle_id, "model")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["decision"], rec.DECISION_KEEP_TAXO)
        self.assertEqual(rows[1]["decision"], rec.DECISION_DEFER)

    def test_state_counts_are_per_field(self):
        self._sync(model="A21", gross_mass_kg="18000")
        counts = rec.state_counts(self.con, vehicle_id=self.vehicle_id)
        self.assertGreaterEqual(counts[rec.STATE_MATCH], 1)
        self.assertGreaterEqual(counts[rec.STATE_DIFFERENCE], 1)
        self.assertGreaterEqual(counts[rec.STATE_UNAVAILABLE], 1)


class VehicleReconciliationBoundaryR2Tests(unittest.TestCase):
    def test_module_does_not_depend_on_operational_documents_or_military_transport(self):
        source = (ROOT / "vehicle_reconciliation.py").read_text("utf-8")
        self.assertNotIn("vehicle_documents", source)
        self.assertNotIn("military_transport", source)
        self.assertIn("import vehicle_registry as registry", source)

    def test_r2_declares_own_identity(self):
        source = (ROOT / "vehicle_reconciliation.py").read_text("utf-8")
        self.assertIn('APP_VERSION = "10.5-r2"', source)
        self.assertIn("Empty/absent incoming values never clear local data", source)


if __name__ == "__main__":
    unittest.main()
