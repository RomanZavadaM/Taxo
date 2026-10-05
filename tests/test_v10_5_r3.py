# -*- coding: utf-8 -*-
import re
import sqlite3
import unittest
from datetime import date
from pathlib import Path

import employee_document_register as docreg
import personnel_registry as personnel
import version_compat  # 10.10 stable-aware version parsing

ROOT = Path(__file__).resolve().parents[1]


def make_db():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
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
    personnel.ensure_schema_on_connection(con)
    return con


def add_employee(con, last_name="Тестовий", first_name="Працівник", personnel_no="001"):
    cur = con.execute(
        "INSERT INTO employees(last_name,first_name,middle_name,personnel_no,active) VALUES(?,?,?,?,1)",
        (last_name, first_name, "Один", personnel_no),
    )
    return cur.lastrowid


def add_doc(con, employee_id, doc_type, number, expiry="", source_kind="manual", source_name="", active=True):
    document_id = personnel.save_employee_document(con, employee_id, {
        "doc_type": doc_type,
        "series": "AA",
        "number": number,
        "issue_date": "01.01.2025",
        "expiry_date": expiry,
        "issuer": "Тестовий орган",
        "source_kind": source_kind,
        "source_name": source_name,
        "notes": "synthetic",
    })
    if not active:
        personnel.archive_employee_document(con, employee_id, document_id)
    con.commit()
    return document_id


class DocumentStateR3Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()
        self.employee_id = add_employee(self.con)
        self.today = date(2026, 9, 28)

    def tearDown(self):
        self.con.close()

    def _row(self, document_id):
        return self.con.execute("SELECT * FROM employee_documents WHERE id=?", (document_id,)).fetchone()

    def test_expired_document_is_red_state(self):
        doc_id = add_doc(self.con, self.employee_id, "Посвідчення водія", "EXPIRED", "27.09.2026")
        self.assertEqual(docreg.document_state(self._row(doc_id), today=self.today), docreg.STATE_EXPIRED)

    def test_expiring_within_30_days_is_attention_state(self):
        doc_id = add_doc(self.con, self.employee_id, "Медичний документ", "SOON", "20.10.2026")
        self.assertEqual(docreg.document_state(self._row(doc_id), today=self.today), docreg.STATE_EXPIRING)

    def test_future_document_is_valid(self):
        doc_id = add_doc(self.con, self.employee_id, "Посвідчення водія", "VALID", "01.01.2027")
        self.assertEqual(docreg.document_state(self._row(doc_id), today=self.today), docreg.STATE_VALID)

    def test_empty_expiry_is_not_invented_as_expired(self):
        doc_id = add_doc(self.con, self.employee_id, "РНОКПП", "NOEXP", "")
        self.assertEqual(docreg.document_state(self._row(doc_id), today=self.today), docreg.STATE_NO_EXPIRY)

    def test_unparseable_expiry_requires_review_not_expired(self):
        doc_id = add_doc(self.con, self.employee_id, "Інше", "BADDATE", "колись")
        self.assertEqual(docreg.document_state(self._row(doc_id), today=self.today), docreg.STATE_DATE_REVIEW)

    def test_archived_state_has_priority_over_expiry(self):
        doc_id = add_doc(self.con, self.employee_id, "Інше", "ARCH", "01.01.2020", active=False)
        self.assertEqual(docreg.document_state(self._row(doc_id), today=self.today), docreg.STATE_ARCHIVED)


class UnifiedRegisterR3Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()
        self.first = add_employee(self.con, "Альфа", "Олег", "101")
        self.second = add_employee(self.con, "Бета", "Ірина", "102")
        add_doc(self.con, self.first, "Паспорт громадянина України", "111111", "", "manual", "")
        add_doc(self.con, self.first, "ID-картка", "222222222", "", personnel.SOURCE_DETAILED, "registry-q3.xlsx")
        add_doc(self.con, self.second, "Посвідчення водія", "DRV-77", "01.01.2027", "manual", "")
        add_doc(self.con, self.second, "Медичний документ", "OLD", "01.01.2020", "manual", "", active=False)

    def tearDown(self):
        self.con.close()

    def test_register_reads_existing_employee_documents_without_duplicate_table(self):
        rows = docreg.list_documents(self.con, today=date(2026, 9, 28))
        self.assertEqual(len(rows), 3)
        tables = {row[0] for row in self.con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertIn("employee_documents", tables)
        self.assertNotIn("employee_document_register", tables)

    def test_registry_and_manual_documents_share_one_list_with_provenance(self):
        rows = docreg.list_documents(self.con, include_archived=True, today=date(2026, 9, 28))
        source_by_number = {row["number"]: row["source_class"] for row in rows}
        self.assertEqual(source_by_number["111111"], docreg.SOURCE_MANUAL)
        self.assertEqual(source_by_number["222222222"], docreg.SOURCE_REGISTRY)

    def test_search_covers_employee_and_document_requisites(self):
        by_name = docreg.list_documents(self.con, query="Альфа", today=date(2026, 9, 28))
        self.assertEqual({row["employee_id"] for row in by_name}, {self.first})
        by_number = docreg.list_documents(self.con, query="DRV-77", today=date(2026, 9, 28))
        self.assertEqual(len(by_number), 1)
        self.assertEqual(by_number[0]["employee_id"], self.second)

    def test_filters_by_type_source_state_and_archive(self):
        registry_rows = docreg.list_documents(self.con, source=docreg.SOURCE_REGISTRY, today=date(2026, 9, 28))
        self.assertEqual([row["number"] for row in registry_rows], ["222222222"])
        driver_rows = docreg.list_documents(self.con, doc_type="Посвідчення водія", state=docreg.STATE_VALID, today=date(2026, 9, 28))
        self.assertEqual([row["number"] for row in driver_rows], ["DRV-77"])
        archived = docreg.list_documents(self.con, state=docreg.STATE_ARCHIVED, include_archived=True, today=date(2026, 9, 28))
        self.assertEqual([row["number"] for row in archived], ["OLD"])

    def test_summary_counts_only_current_filtered_rows(self):
        rows = docreg.list_documents(self.con, include_archived=True, today=date(2026, 9, 28))
        counts = docreg.summary(rows)
        self.assertEqual(counts["total"], 4)
        self.assertEqual(counts[docreg.STATE_ARCHIVED], 1)
        self.assertEqual(counts[docreg.STATE_VALID], 1)
        self.assertEqual(counts[docreg.STATE_NO_EXPIRY], 2)


class R3IntegrationTests(unittest.TestCase):
    def test_feature_layer_remains_in_install_chain_after_later_revisions(self):
        entry = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1053_features import install as install_v1053", entry)
        self.assertIn("install_v1053(", entry)
        self.assertIn("install_v1052(", entry)
        self.assertLess(entry.index("install_v1053("), entry.index("install_v1052("))

    def test_r3_module_keeps_its_historical_identity(self):
        source = (ROOT / "v1053_features.py").read_text("utf-8")
        self.assertIn('APP_VERSION = "10.5-r3"', source)
        self.assertIn("Реєстр документів", source)

    def test_current_version_is_r3_or_later_not_frozen_to_r3_forever(self):
        version = (ROOT / "VERSION.txt").read_text("utf-8")
        match = version_compat.search_version_line(version)
        self.assertIsNotNone(match)
        major, minor, revision = map(int, match.groups())
        self.assertTrue((major, minor, revision) >= (10, 5, 3))

    def test_start_guard_requires_r3_runtime_files(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("employee_document_register.py", workflow)
        self.assertIn("v1053_features.py", workflow)


if __name__ == "__main__":
    unittest.main()
