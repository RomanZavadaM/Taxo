# -*- coding: utf-8 -*-
import inspect
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

import main
import personnel_v91
import v91_features
from vehicle_documents import (
    DOCUMENT_TYPES,
    archive_current_document_slot,
    copy_document_file,
    document_status,
    ensure_vehicle_documents_schema,
    vehicle_document_summary,
)
from workspace import ensure_workspace, paths_for, resolved_path, workspace_has_data


class TestTaxo102R1VehicleDocuments(unittest.TestCase):
    def test_candidate_identity(self):
        self.assertEqual(main.APP_VERSION, "10.2-r1")

    def test_core_owns_current_shell_identity(self):
        core_source = inspect.getsource(main.App.__init__)
        v91_source = inspect.getsource(v91_features.install)
        personnel_source = inspect.getsource(personnel_v91.install)
        self.assertIn('self.title(f"Taxo {APP_VERSION} — Driver Worktime")', core_source)
        self.assertNotIn("_replace_about_command(core, self)", v91_source)
        self.assertNotIn("self.title(", v91_source)
        self.assertNotIn("self.title(", personnel_source)

    def test_supported_document_types(self):
        self.assertEqual(
            set(DOCUMENT_TYPES),
            {
                "insurance",
                "inspection",
                "temporary_registration",
                "registration_certificate",
            },
        )

    def test_validity_statuses(self):
        today = date(2026, 9, 21)
        self.assertEqual(document_status("insurance", "2026-09-20", today=today), "Прострочений")
        self.assertTrue(document_status("insurance", "2026-10-01", today=today).startswith("Закінчується:"))
        self.assertEqual(document_status("insurance", "2027-01-01", today=today), "Актуальний")
        self.assertEqual(document_status("registration_certificate", "", today=today), "Актуальний")
        self.assertEqual(document_status("inspection", "", today=today), "Немає дати дії")

    def test_summary_requires_all_four_document_types(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute(
            """
            CREATE TABLE vehicles(
                id INTEGER PRIMARY KEY,
                name TEXT,
                plate TEXT,
                make_model TEXT,
                active INTEGER DEFAULT 1
            )
            """
        )
        con.execute("INSERT INTO vehicles(id,name,plate,make_model) VALUES(1,'Bus 1','AA0001AA','Test')")
        ensure_vehicle_documents_schema(con)
        overall, details = vehicle_document_summary(con, 1, today=date(2026, 9, 21))
        self.assertEqual(overall, "Проблема")
        self.assertEqual(sum(1 for item in details if item[3] == "Відсутній"), 3)

        now = "2026-09-21T10:00:00"
        docs = [
            ("insurance", "2027-09-21"),
            ("inspection", "2027-03-21"),
            ("temporary_registration", "2026-12-21"),
            ("registration_certificate", ""),
        ]
        for dtype, until in docs:
            con.execute(
                """
                INSERT INTO vehicle_documents(
                    vehicle_id,doc_type,document_no,valid_until,created_at,updated_at
                ) VALUES(1,?,?,?, ?, ?)
                """,
                (dtype, dtype, until, now, now),
            )
        con.commit()
        overall, details = vehicle_document_summary(con, 1, today=date(2026, 9, 21))
        self.assertEqual(overall, "Актуально")
        self.assertEqual(len(details), 3)
        con.close()

    def test_registration_requirement_accepts_temporary_or_permanent_document(self):
        for dtype, until in (
            ("temporary_registration", "2026-12-21"),
            ("registration_certificate", ""),
        ):
            con = sqlite3.connect(":memory:")
            con.row_factory = sqlite3.Row
            con.execute(
                "CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT,active INTEGER DEFAULT 1)"
            )
            con.execute("INSERT INTO vehicles(id,name) VALUES(1,'Bus')")
            ensure_vehicle_documents_schema(con)
            now = "2026-09-21T10:00:00"
            for required_type, required_until in (
                ("insurance", "2027-01-01"),
                ("inspection", "2027-01-01"),
                (dtype, until),
            ):
                con.execute(
                    """
                    INSERT INTO vehicle_documents(
                        vehicle_id,doc_type,valid_until,created_at,updated_at
                    ) VALUES(1,?,?,?,?)
                    """,
                    (required_type, required_until, now, now),
                )
            con.commit()
            overall, details = vehicle_document_summary(con, 1, today=date(2026, 9, 21))
            self.assertEqual(overall, "Актуально")
            self.assertEqual(len(details), 3)
            con.close()

    def test_new_document_archives_previous_current_slot(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute(
            "CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT,active INTEGER DEFAULT 1)"
        )
        con.execute("INSERT INTO vehicles(id,name) VALUES(1,'Bus')")
        ensure_vehicle_documents_schema(con)
        now = "2026-09-21T10:00:00"
        con.execute(
            """
            INSERT INTO vehicle_documents(
                vehicle_id,doc_type,document_no,created_at,updated_at
            ) VALUES(1,'insurance','OLD',?,?)
            """,
            (now, now),
        )
        con.execute(
            """
            INSERT INTO vehicle_documents(
                vehicle_id,doc_type,document_no,created_at,updated_at
            ) VALUES(1,'temporary_registration','TEMP',?,?)
            """,
            (now, now),
        )
        con.commit()

        archive_current_document_slot(con, 1, "insurance", now=now)
        archive_current_document_slot(con, 1, "registration_certificate", now=now)
        con.commit()

        old_insurance = con.execute(
            "SELECT archived FROM vehicle_documents WHERE document_no='OLD'"
        ).fetchone()
        old_registration = con.execute(
            "SELECT archived FROM vehicle_documents WHERE document_no='TEMP'"
        ).fetchone()
        self.assertEqual(old_insurance["archived"], 1)
        self.assertEqual(old_registration["archived"], 1)
        con.close()

    def test_vehicle_document_copies_make_workspace_nonempty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_workspace(root)
            doc_dir = paths_for(root)["vehicle_documents"]
            (doc_dir / "copy.pdf").write_bytes(b"copy")
            self.assertTrue(workspace_has_data(root))

    def test_document_copy_is_kept_inside_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.pdf"
            source.write_bytes(b"sample")
            stored = copy_document_file(root, 7, "insurance", source)
            self.assertTrue(stored.startswith("workspace://"))
            target = resolved_path(stored, root)
            self.assertTrue(target.is_file())
            self.assertEqual(target.read_bytes(), b"sample")


if __name__ == "__main__":
    unittest.main()
