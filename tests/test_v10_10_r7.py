# -*- coding: utf-8 -*-
"""Taxo 10.10-r7 — employee document requirements and workspace backup."""
import sqlite3
import tempfile
import unittest
import zipfile
from datetime import date
from pathlib import Path

import employee_document_control_r7 as control
import personnel_registry as personnel
import workspace


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
    control.ensure_schema_on_connection(con)
    con.execute(
        "INSERT INTO employees(id,last_name,first_name,personnel_no,active) VALUES(1,'Тестовий','Працівник','001',1)"
    )
    con.commit()
    return con


class EmployeeDocumentRequirementR7Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()

    def tearDown(self):
        self.con.close()

    def test_required_rule_survives_document_archive(self):
        control.save_requirement(
            self.con, 1, "Посвідчення водія",
            required=True, expiry_control=True,
        )
        doc_id = personnel.save_employee_document(
            self.con, 1, {
                "doc_type": "Посвідчення водія",
                "number": "DRV",
                "expiry_date": "01.01.2028",
            }
        )
        self.con.commit()
        row = control.document_control_rows(
            self.con, today=date(2026, 11, 5)
        )[0]
        self.assertEqual(row["state"], control.STATE_OK)

        personnel.archive_employee_document(self.con, 1, doc_id)
        self.con.commit()
        row = control.document_control_rows(
            self.con, today=date(2026, 11, 5)
        )[0]
        self.assertTrue(row["required"])
        self.assertTrue(row["expiry_control"])
        self.assertEqual(row["state"], control.STATE_NO_DOCUMENT)

    def test_expiry_control_requires_date(self):
        control.save_requirement(
            self.con, 1, "Медичний документ",
            required=True, expiry_control=True,
        )
        personnel.save_employee_document(
            self.con, 1, {
                "doc_type": "Медичний документ",
                "number": "MED",
                "expiry_date": "",
            }
        )
        self.con.commit()
        row = control.document_control_rows(
            self.con, today=date(2026, 11, 5)
        )[0]
        self.assertEqual(row["state"], control.STATE_DATE_REQUIRED)


    def test_required_document_without_workspace_copy_is_visible_problem(self):
        control.save_requirement(
            self.con, 1, "Посвідчення водія",
            required=True, expiry_control=False,
        )
        personnel.save_employee_document(
            self.con, 1, {
                "doc_type": "Посвідчення водія",
                "number": "DRV-NO-FILE",
                "expiry_date": "",
                "file_path": "",
            }
        )
        self.con.commit()
        rows = control.document_control_rows(
            self.con, today=date(2026, 11, 5), problems_only=True
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["state"], control.STATE_COPY_REQUIRED)
        self.assertFalse(rows[0]["file_backed_up"])

    def test_optional_document_can_have_expiry_control(self):
        control.save_requirement(
            self.con, 1, "Інше",
            required=False, expiry_control=True,
        )
        personnel.save_employee_document(
            self.con, 1, {
                "doc_type": "Інше",
                "number": "OPT",
                "expiry_date": "20.11.2026",
            }
        )
        self.con.commit()
        row = control.document_control_rows(
            self.con, today=date(2026, 11, 5)
        )[0]
        self.assertFalse(row["required"])
        self.assertEqual(row["state"], control.STATE_EXPIRING)


class EmployeeDocumentStorageR7Tests(unittest.TestCase):
    def test_local_file_is_copied_into_workspace_and_full_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            workspace.ensure_workspace(root)
            source = Path(tmp) / "passport.pdf"
            source.write_bytes(b"employee-document")

            class Core:
                DATA_ROOT = root

                @staticmethod
                def real_data_path(value):
                    return workspace.resolved_path(value, root)

                @staticmethod
                def db_stored_path(value):
                    return workspace.stored_path(value, root)

            stored, backed_up = control.stored_document_path(Core, 7, source)
            self.assertTrue(backed_up)
            self.assertTrue(stored.startswith("workspace://Data/EmployeeDocuments/"))
            copied = workspace.resolved_path(stored, root)
            self.assertTrue(copied.is_file())
            self.assertEqual(copied.read_bytes(), b"employee-document")

            # Full backup always includes employee documents, without an extra checkbox.
            db_path = workspace.paths_for(root)["main_db"]
            con = sqlite3.connect(db_path)
            con.execute("CREATE TABLE sample(id INTEGER PRIMARY KEY)")
            con.commit()
            con.close()

            archive = Path(tmp) / "full-backup.zip"
            workspace.create_workspace_backup_archive(
                root, archive, app_version="10.10-r7",
                include_vehicle_documents=False,
                include_tacho_scans=False,
                include_output=False,
            )
            with zipfile.ZipFile(archive, "r") as zf:
                names = set(zf.namelist())
            relative = copied.relative_to(root).as_posix()
            self.assertIn(relative, names)
            self.assertIn(workspace.FULL_BACKUP_MANIFEST, names)


if __name__ == "__main__":
    unittest.main()
