import sqlite3
import tempfile
import unittest
from pathlib import Path

import backup_migration
import main
import output_files


ROOT = Path(__file__).resolve().parents[1]


def make_taxo_db(path: Path, marker: str):
    con = sqlite3.connect(path)
    try:
        con.execute("CREATE TABLE drivers(id INTEGER PRIMARY KEY, name TEXT)")
        con.execute("CREATE TABLE worklog(id INTEGER PRIMARY KEY, note TEXT)")
        con.execute("CREATE TABLE company(id INTEGER PRIMARY KEY, name TEXT)")
        con.execute("CREATE TABLE marker(value TEXT)")
        con.execute("INSERT INTO marker(value) VALUES (?)", (marker,))
        con.commit()
    finally:
        con.close()


class OutputAtomicR6Tests(unittest.TestCase):
    def test_failed_writer_does_not_damage_existing_output(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "report.pdf"
            target.write_bytes(b"OLD-CORRECT")
            shown = []
            original_showerror = output_files.messagebox.showerror
            output_files.messagebox.showerror = lambda *args, **kwargs: shown.append(args)
            try:
                def broken_writer(path):
                    Path(path).write_bytes(b"PARTIAL")
                    raise RuntimeError("writer failed")

                actual = output_files.write_output_file(
                    broken_writer, target, kind="PDF", error_title="test"
                )
            finally:
                output_files.messagebox.showerror = original_showerror

            self.assertIsNone(actual)
            self.assertEqual(target.read_bytes(), b"OLD-CORRECT")
            self.assertTrue(shown)
            self.assertFalse(any(target.parent.glob(".*.tmp.pdf")))

    def test_successful_writer_atomically_replaces_target_and_keeps_suffix(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "report.xlsx"
            target.write_bytes(b"OLD")
            seen = []

            def writer(path):
                path = Path(path)
                seen.append(path)
                self.assertEqual(path.suffix, ".xlsx")
                path.write_bytes(b"NEW")

            actual = output_files.write_output_file(writer, target, kind="Excel")
            self.assertEqual(actual, target)
            self.assertEqual(target.read_bytes(), b"NEW")
            self.assertEqual(len(seen), 1)
            self.assertNotEqual(seen[0], target)
            self.assertFalse(seen[0].exists())


class RestoreFailureR6Tests(unittest.TestCase):
    def test_double_failure_reports_safety_backup_instead_of_hiding_rollback_error(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_path = root / "driver_worktime.sqlite3"
            source = root / "restore.sqlite3"
            backups = root / "Backups"
            backups.mkdir()
            make_taxo_db(db_path, "before")
            make_taxo_db(source, "new")

            calls = []

            def failing_init():
                calls.append("init")
                raise RuntimeError("init failed")

            with self.assertRaises(RuntimeError) as caught:
                backup_migration.restore_database_from_file(
                    source, db_path, backups, failing_init
                )

            message = str(caught.exception)
            self.assertIn("аварійне повернення", message)
            self.assertIn("Страхова копія збережена тут:", message)
            self.assertIn("init failed", message)
            self.assertEqual(calls, ["init", "init"])

            con = sqlite3.connect(db_path)
            try:
                self.assertEqual(
                    con.execute("SELECT value FROM marker").fetchone()[0], "before"
                )
            finally:
                con.close()


class BackupDisclosureR6Tests(unittest.TestCase):
    def test_backup_ui_discloses_always_included_employee_documents(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        start = source.index("    def manual_backup(self):")
        end = source.index("    def open_data_folder", start)
        section = source[start:end]

        self.assertIn(
            "✓ Копії документів працівників (Data/EmployeeDocuments)", section
        )
        self.assertIn("документи працівників — завжди", section)
        self.assertIn('label="full" if extras else "core_with_employee_documents"', section)
        self.assertNotIn('label="full" if extras else "db"', section)

    def test_r6_version_identity_is_synchronized(self):
        self.assertEqual(main.APP_VERSION, "10.11-r6")
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text(encoding="utf-8").strip(),
            "Version: 10.11-r6",
        )


if __name__ == "__main__":
    unittest.main()
