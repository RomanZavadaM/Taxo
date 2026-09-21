# -*- coding: utf-8 -*-
import inspect
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

import main
from document_viewer import DOCX_EXTENSIONS, IMAGE_EXTENSIONS, PDF_EXTENSIONS, document_kind
import personnel_v91
import v91_features
from vehicle_documents import (
    DOCUMENT_TYPES,
    archive_current_document_slot,
    copy_document_file,
    document_status,
    ensure_vehicle_documents_schema,
    vehicle_document_summary,
    vehicle_document_warning_lines,
    vehicle_document_report_rows,
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
                "tachograph_inspection_protocol",
            },
        )

    def test_validity_statuses(self):
        today = date(2026, 9, 21)
        self.assertEqual(document_status("insurance", "2026-09-20", today=today), "Прострочений")
        self.assertTrue(document_status("insurance", "2026-10-01", today=today).startswith("Закінчується:"))
        self.assertEqual(document_status("insurance", "2027-01-01", today=today), "Актуальний")
        self.assertEqual(document_status("registration_certificate", "", today=today), "Актуальний")
        self.assertEqual(document_status("inspection", "", today=today), "Немає дати дії")
        self.assertEqual(
            document_status("tachograph_inspection_protocol", "", today=today),
            "Немає дати дії",
        )
        self.assertTrue(
            document_status(
                "tachograph_inspection_protocol", "2026-10-01", today=today
            ).startswith("Закінчується:")
        )

    def test_summary_always_requires_permanent_tech_passport(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute(
            """
            CREATE TABLE vehicles(
                id INTEGER PRIMARY KEY,
                name TEXT,
                plate TEXT,
                make_model TEXT,
                ownership_type TEXT DEFAULT '',
                temporary_registration_required INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1
            )
            """
        )
        con.execute("INSERT INTO vehicles(id,name,plate,make_model) VALUES(1,'Bus 1','AA0001AA','Test')")
        ensure_vehicle_documents_schema(con)
        overall, details = vehicle_document_summary(con, 1, today=date(2026, 9, 21))
        self.assertEqual(overall, "Проблема")
        self.assertEqual(sum(1 for item in details if item[3] == "Відсутній"), 4)

        now = "2026-09-21T10:00:00"
        docs = [
            ("insurance", "2027-09-21"),
            ("inspection", "2027-03-21"),
            ("temporary_registration", "2026-12-21"),
            ("registration_certificate", ""),
            ("tachograph_inspection_protocol", "2027-09-21"),
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
        self.assertEqual(len(details), 4)
        con.close()

    def test_temporary_registration_is_additional_when_vehicle_requires_it(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute(
            "CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT,ownership_type TEXT DEFAULT '',temporary_registration_required INTEGER DEFAULT 0,active INTEGER DEFAULT 1)"
        )
        con.execute(
            "INSERT INTO vehicles(id,name,ownership_type,temporary_registration_required) VALUES(1,'Bus','Оренда',1)"
        )
        ensure_vehicle_documents_schema(con)
        now = "2026-09-21T10:00:00"
        for dtype, until in (
            ("insurance", "2027-01-01"),
            ("inspection", "2027-01-01"),
            ("registration_certificate", ""),
            ("tachograph_inspection_protocol", "2027-01-01"),
        ):
            con.execute(
                """
                INSERT INTO vehicle_documents(
                    vehicle_id,doc_type,valid_until,created_at,updated_at
                ) VALUES(1,?,?,?,?)
                """,
                (dtype, until, now, now),
            )
        con.commit()

        overall, details = vehicle_document_summary(con, 1, today=date(2026, 9, 21))
        self.assertEqual(overall, "Проблема")
        self.assertEqual(len(details), 5)
        self.assertEqual(
            next(status for dtype, _label, _row, status in details if dtype == "temporary_registration"),
            "Відсутній",
        )

        con.execute(
            """
            INSERT INTO vehicle_documents(
                vehicle_id,doc_type,valid_until,created_at,updated_at
            ) VALUES(1,'temporary_registration','2026-12-21',?,?)
            """,
            (now, now),
        )
        con.commit()
        overall, details = vehicle_document_summary(con, 1, today=date(2026, 9, 21))
        self.assertEqual(overall, "Актуально")
        self.assertEqual(len(details), 5)
        con.close()

    def test_required_temporary_registration_must_have_valid_term(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute(
            "CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT,ownership_type TEXT DEFAULT '',temporary_registration_required INTEGER DEFAULT 0,active INTEGER DEFAULT 1)"
        )
        con.execute(
            "INSERT INTO vehicles(id,name,temporary_registration_required) VALUES(1,'Bus',1)"
        )
        ensure_vehicle_documents_schema(con)
        now = "2026-09-21T10:00:00"
        for dtype, until in (
            ("insurance", "2027-01-01"),
            ("inspection", "2027-01-01"),
            ("registration_certificate", ""),
            ("tachograph_inspection_protocol", "2027-01-01"),
            ("temporary_registration", ""),
        ):
            con.execute(
                """
                INSERT INTO vehicle_documents(
                    vehicle_id,doc_type,valid_until,created_at,updated_at
                ) VALUES(1,?,?,?,?)
                """,
                (dtype, until, now, now),
            )
        con.commit()

        overall, details = vehicle_document_summary(con, 1, today=date(2026, 9, 21))
        self.assertEqual(overall, "Проблема")
        self.assertEqual(
            next(status for dtype, _label, _row, status in details if dtype == "temporary_registration"),
            "Немає дати дії",
        )

        con.execute(
            "UPDATE vehicle_documents SET valid_until='2026-09-20' WHERE vehicle_id=1 AND doc_type='temporary_registration'"
        )
        con.commit()
        overall, details = vehicle_document_summary(con, 1, today=date(2026, 9, 21))
        self.assertEqual(overall, "Проблема")
        self.assertEqual(
            next(status for dtype, _label, _row, status in details if dtype == "temporary_registration"),
            "Прострочений",
        )

        con.execute(
            "UPDATE vehicle_documents SET valid_until='2026-10-01' WHERE vehicle_id=1 AND doc_type='temporary_registration'"
        )
        con.commit()
        overall, details = vehicle_document_summary(con, 1, today=date(2026, 9, 21))
        self.assertEqual(overall, "Увага")
        self.assertTrue(
            next(status for dtype, _label, _row, status in details if dtype == "temporary_registration").startswith(
                "Закінчується:"
            )
        )
        con.close()

    def test_waybill_warning_lists_document_term_problems_for_work_date(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute(
            "CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT,ownership_type TEXT DEFAULT '',temporary_registration_required INTEGER DEFAULT 0,active INTEGER DEFAULT 1)"
        )
        con.execute(
            "INSERT INTO vehicles(id,name,temporary_registration_required) VALUES(1,'Bus',1)"
        )
        ensure_vehicle_documents_schema(con)
        now = "2026-09-21T10:00:00"
        for dtype, number, until in (
            ("insurance", "INS-1", "2026-09-20"),
            ("inspection", "TECH-1", "2027-01-01"),
            ("registration_certificate", "REG-1", ""),
            ("tachograph_inspection_protocol", "TACHO-1", "2026-10-01"),
            ("temporary_registration", "TEMP-1", ""),
        ):
            con.execute(
                """
                INSERT INTO vehicle_documents(
                    vehicle_id,doc_type,document_no,valid_until,created_at,updated_at
                ) VALUES(1,?,?,?,?,?)
                """,
                (dtype, number, until, now, now),
            )
        con.commit()

        warnings = vehicle_document_warning_lines(con, 1, today=date(2026, 9, 21))
        self.assertTrue(any("Страховка: Прострочений" in item for item in warnings))
        self.assertTrue(any("Протокол перевірки тахографа: Закінчується:" in item for item in warnings))
        self.assertTrue(any("Тимчасовий реєстраційний документ: Немає дати дії" in item for item in warnings))
        self.assertFalse(any("Діагностика / техконтроль" in item for item in warnings))
        self.assertFalse(any("Постійний техпаспорт" in item for item in warnings))

        source = inspect.getsource(main.App.issue_selected_waybill)
        self.assertIn("vehicle_document_warning_lines", source)
        self.assertIn('today=row["date"]', source)
        self.assertIn("messagebox.askyesno", source)
        con.close()

    def test_temporary_and_permanent_registration_have_separate_history(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute(
            "CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT,ownership_type TEXT DEFAULT '',temporary_registration_required INTEGER DEFAULT 0,active INTEGER DEFAULT 1)"
        )
        con.execute("INSERT INTO vehicles(id,name) VALUES(1,'Bus')")
        ensure_vehicle_documents_schema(con)
        now = "2026-09-21T10:00:00"
        con.execute(
            """
            INSERT INTO vehicle_documents(
                vehicle_id,doc_type,document_no,created_at,updated_at
            ) VALUES(1,'temporary_registration','TEMP',?,?)
            """,
            (now, now),
        )
        con.execute(
            """
            INSERT INTO vehicle_documents(
                vehicle_id,doc_type,document_no,created_at,updated_at
            ) VALUES(1,'registration_certificate','PERM',?,?)
            """,
            (now, now),
        )
        con.commit()

        archive_current_document_slot(con, 1, "registration_certificate", now=now)
        con.commit()

        temp = con.execute(
            "SELECT archived FROM vehicle_documents WHERE document_no='TEMP'"
        ).fetchone()
        permanent = con.execute(
            "SELECT archived FROM vehicle_documents WHERE document_no='PERM'"
        ).fetchone()
        self.assertEqual(temp["archived"], 0)
        self.assertEqual(permanent["archived"], 1)
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

    def test_internal_document_viewer_supports_archive_formats(self):
        self.assertEqual(document_kind("sample.pdf"), "pdf")
        self.assertEqual(document_kind("scan.JPG"), "image")
        self.assertEqual(document_kind("form.docx"), "docx")
        self.assertEqual(document_kind("sheet.xlsx"), "other")
        self.assertIn(".pdf", PDF_EXTENSIONS)
        self.assertIn(".png", IMAGE_EXTENSIONS)
        self.assertIn(".docx", DOCX_EXTENSIONS)
        self.assertIn("open_document", inspect.getsource(main.App._open_path))

    def test_vehicle_document_report_uses_history_for_selected_date(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute(
            "CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT,ownership_type TEXT DEFAULT '',temporary_registration_required INTEGER DEFAULT 0,active INTEGER DEFAULT 1)"
        )
        con.execute(
            "INSERT INTO vehicles(id,name,plate) VALUES(1,'Bus','AA0001AA')"
        )
        ensure_vehicle_documents_schema(con)
        old = "2026-01-01T10:00:00"
        new = "2026-09-01T10:00:00"
        base_docs = (
            ("inspection", "TECH", "2026-01-01", "2027-01-01"),
            ("registration_certificate", "REG", "2026-01-01", ""),
            ("tachograph_inspection_protocol", "TACHO", "2026-01-01", "2027-01-01"),
        )
        for dtype, number, valid_from, valid_until in base_docs:
            con.execute(
                """
                INSERT INTO vehicle_documents(
                    vehicle_id,doc_type,document_no,valid_from,valid_until,created_at,updated_at
                ) VALUES(1,?,?,?,?,?,?)
                """,
                (dtype, number, valid_from, valid_until, old, old),
            )
        con.execute(
            """
            INSERT INTO vehicle_documents(
                vehicle_id,doc_type,document_no,valid_from,valid_until,archived,created_at,updated_at
            ) VALUES(1,'insurance','OLD-INS','2026-01-01','2026-08-31',1,?,?)
            """,
            (old, old),
        )
        con.execute(
            """
            INSERT INTO vehicle_documents(
                vehicle_id,doc_type,document_no,valid_from,valid_until,archived,created_at,updated_at
            ) VALUES(1,'insurance','NEW-INS','2026-09-01','2027-08-31',0,?,?)
            """,
            (new, new),
        )
        con.commit()

        august = vehicle_document_report_rows(
            con, date(2026, 8, 15), active_only=True
        )
        september = vehicle_document_report_rows(
            con, date(2026, 9, 15), active_only=True
        )
        august_insurance = next(
            row for row in august if row["doc_type"] == "insurance"
        )
        september_insurance = next(
            row for row in september if row["doc_type"] == "insurance"
        )
        self.assertEqual(august_insurance["document_no"], "OLD-INS")
        self.assertEqual(september_insurance["document_no"], "NEW-INS")
        self.assertNotEqual(august_insurance["status"], "Відсутній")
        con.close()

    def test_document_copy_rejects_unsupported_file_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.txt"
            source.write_text("not a supported document copy", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Непідтримуваний формат копії"):
                copy_document_file(root, 7, "insurance", source)
            target_dir = paths_for(root)["vehicle_documents"] / "7" / "insurance"
            self.assertFalse(target_dir.exists())


if __name__ == "__main__":
    unittest.main()
