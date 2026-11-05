# -*- coding: utf-8 -*-
"""Taxo 10.10-r6 — unified personnel registry data center."""
import sqlite3
import unittest

import personnel_data_center_r6 as center
import registry_working_data as working


def make_db():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute(
        """CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            last_name TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            middle_name TEXT DEFAULT '',
            personnel_no TEXT DEFAULT '',
            position TEXT DEFAULT '',
            employment_date TEXT DEFAULT '',
            active INTEGER DEFAULT 1
        )"""
    )
    working.ensure_personnel_schema(con)
    return con


def add_raw(con, employee_id, import_id, scope, field, value, order_no):
    con.execute(
        """INSERT INTO employee_registry_raw_fields(
            import_id,employee_id,source_kind,source_name,file_sha256,source_row,
            field_order,field_key,source_header,raw_value,canonical_scope,
            canonical_field,canonical_value,transfer_status,transfer_note,imported_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            import_id, employee_id, "military_registry_personal", "registry.xlsx",
            "sha", 2, order_no, field, field, value, scope, field, value,
            "mapped", "", "2026-11-05T10:00:00",
        ),
    )


class PersonnelDataCenterR6Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()
        self.con.execute(
            """INSERT INTO employees(
                id,last_name,first_name,middle_name,personnel_no,position,employment_date,active,
                rnokpp,birth_date,registered_address
            ) VALUES(1,'Іваненко','Іван','','001','Водій','2026-01-01',1,'1111111111','','')"""
        )
        self.con.execute(
            """INSERT INTO employee_military_profile(
                employee_id,registry_person_id,military_rank
            ) VALUES(1,'REG-OLD','Солдат')"""
        )
        self.con.execute(
            """INSERT INTO employee_registry_imports(
                id,source_kind,source_name,file_sha256,imported_at,total_rows,matched_rows,
                updated_rows,skipped_rows,warning_count,mode
            ) VALUES(1,'military_registry_personal','registry.xlsx','sha',
                     '2026-11-05T10:00:00',1,1,0,0,0,'compare')"""
        )
        add_raw(self.con, 1, 1, "personal", "birth_date", "2000-01-02", 1)
        add_raw(self.con, 1, 1, "personal", "registered_address", "Львів", 2)
        add_raw(self.con, 1, 1, "personal", "rnokpp", "2222222222", 3)
        add_raw(self.con, 1, 1, "military", "registry_person_id", "REG-NEW", 4)
        add_raw(self.con, 1, 1, "military", "military_rank", "Сержант", 5)
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def test_preview_counts_fill_differences_and_critical_identity(self):
        rows = center.registry_bulk_preview(self.con)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["fill_count"], 2)
        self.assertEqual(row["difference_count"], 3)
        self.assertEqual(row["critical_count"], 2)

    def test_fill_empty_does_not_overwrite_existing_values(self):
        result = center.apply_registry_bulk(
            self.con, [1], center.MODE_FILL_EMPTY
        )
        self.con.commit()
        employee = self.con.execute("SELECT * FROM employees WHERE id=1").fetchone()
        military = self.con.execute(
            "SELECT * FROM employee_military_profile WHERE employee_id=1"
        ).fetchone()
        self.assertEqual(employee["birth_date"], "2000-01-02")
        self.assertEqual(employee["registered_address"], "Львів")
        self.assertEqual(employee["rnokpp"], "1111111111")
        self.assertEqual(military["registry_person_id"], "REG-OLD")
        self.assertEqual(military["military_rank"], "Солдат")
        self.assertEqual(result["changed_fields"], 2)

    def test_accept_noncritical_updates_bulk_but_keeps_identity_fields(self):
        result = center.apply_registry_bulk(
            self.con, [1], center.MODE_ACCEPT_NONCRITICAL
        )
        self.con.commit()
        employee = self.con.execute("SELECT * FROM employees WHERE id=1").fetchone()
        military = self.con.execute(
            "SELECT * FROM employee_military_profile WHERE employee_id=1"
        ).fetchone()
        self.assertEqual(employee["rnokpp"], "1111111111")
        self.assertEqual(military["registry_person_id"], "REG-OLD")
        self.assertEqual(military["military_rank"], "Сержант")
        self.assertEqual(employee["birth_date"], "2000-01-02")
        self.assertEqual(result["changed_fields"], 3)
        self.assertEqual(result["skipped_critical"], 2)

    def test_raw_registry_snapshot_remains_immutable_after_bulk_apply(self):
        before = [
            tuple(row)
            for row in self.con.execute(
                "SELECT * FROM employee_registry_raw_fields ORDER BY id"
            ).fetchall()
        ]
        center.apply_registry_bulk(
            self.con, [1], center.MODE_ACCEPT_NONCRITICAL
        )
        self.con.commit()
        after = [
            tuple(row)
            for row in self.con.execute(
                "SELECT * FROM employee_registry_raw_fields ORDER BY id"
            ).fetchall()
        ]
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
