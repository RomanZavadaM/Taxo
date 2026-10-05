import sqlite3
import unittest
from datetime import date
from pathlib import Path

import feature_layers
import vehicle_documents as docs

ROOT = Path(__file__).resolve().parents[1]


class VehicleDocumentValidityR3Tests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.execute("CREATE TABLE vehicles(id INTEGER PRIMARY KEY, temporary_registration_required INTEGER DEFAULT 0)")
        self.con.execute("INSERT INTO vehicles(id,temporary_registration_required) VALUES(1,0)")
        docs.ensure_vehicle_documents_schema(self.con)

    def tearDown(self):
        self.con.close()

    def add(self, dtype, valid_from="", valid_until="", archived=0, number="X"):
        self.con.execute(
            """INSERT INTO vehicle_documents(
                vehicle_id,doc_type,document_no,issuer,valid_from,valid_until,
                copy_path,notes,archived,created_at,updated_at
            ) VALUES(1,?,?,?,?,?,'','',?,'2026-01-01T00:00:00','2026-01-01T00:00:00')""",
            (dtype, number, "", valid_from, valid_until, archived),
        )
        self.con.commit()

    def test_valid_from_is_honoured_for_trip_start(self):
        self.add("insurance", "2026-10-03", "2027-10-03")
        covered, _row, status, _used = docs.document_coverage_for_period(
            self.con, 1, "insurance", date(2026, 10, 1), date(2026, 10, 2)
        )
        self.assertFalse(covered)
        self.assertEqual(status, "Не діє весь рейс")

    def test_expiry_before_trip_end_is_problem(self):
        self.add("inspection", "2026-01-01", "2026-10-01")
        covered, _row, status, _used = docs.document_coverage_for_period(
            self.con, 1, "inspection", date(2026, 10, 1), date(2026, 10, 2)
        )
        self.assertFalse(covered)
        self.assertEqual(status, "Не діє весь рейс")

    def test_multiple_active_same_type_documents_can_jointly_cover_trip(self):
        self.add("insurance", "2026-01-01", "2026-10-01", number="A")
        self.add("insurance", "2026-10-02", "2027-10-02", number="B")
        covered, row, _status, used = docs.document_coverage_for_period(
            self.con, 1, "insurance", date(2026, 10, 1), date(2026, 10, 3)
        )
        self.assertTrue(covered)
        self.assertEqual(row["document_no"], "B")
        self.assertEqual([r["document_no"] for r in used], ["A", "B"])

    def test_archived_document_does_not_cover_new_trip(self):
        self.add("insurance", "2026-01-01", "2027-01-01", archived=1)
        covered, row, _status, _used = docs.document_coverage_for_period(
            self.con, 1, "insurance", date(2026, 10, 1), date(2026, 10, 1)
        )
        self.assertFalse(covered)
        self.assertIsNone(row)

    def test_temporary_registration_is_required_only_when_marked(self):
        self.assertNotIn("temporary_registration", docs._required_document_types(self.con, 1))
        self.con.execute("UPDATE vehicles SET temporary_registration_required=1 WHERE id=1")
        self.con.commit()
        self.assertIn("temporary_registration", docs._required_document_types(self.con, 1))

    def test_waybill_checks_complete_trip_range(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn("vehicle_document_warning_lines_for_period", source)
        self.assertIn('con,row["vehicle_id"],row["date"],row["end_date"]', source)

    def test_r3_layer_is_preserved_before_later_revisions(self):
        ids = feature_layers.feature_layer_ids()
        self.assertIn("v1092-waybill-integrity", ids)
        self.assertIn("v1093-vehicle-document-validity", ids)
        self.assertLess(ids.index("v1092-waybill-integrity"), ids.index("v1093-vehicle-document-validity"))
        if "v1094-work-rest-compliance" in ids:
            self.assertLess(ids.index("v1093-vehicle-document-validity"), ids.index("v1094-work-rest-compliance"))
        version = (ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()
        self.assertRegex(version, r"^Version: 10\.(?:9-r(?:[3-9]|10)|1\d-r\d+)$")


if __name__ == "__main__":
    unittest.main()
