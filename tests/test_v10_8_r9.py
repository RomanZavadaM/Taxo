import re
import sqlite3
import tempfile
import unittest
from pathlib import Path

import backup_migration
import main


ROOT = Path(__file__).resolve().parents[1]


def version_key(value: str):
    match = re.fullmatch(r"(\d+)\.(\d+)-r(\d+)(?:\.(\d+))?", value)
    if not match:
        raise AssertionError(f"unexpected version format: {value}")
    major, minor, revision, subrevision = match.groups()
    return int(major), int(minor), int(revision), int(subrevision or 0)


def make_taxo_db(path: Path, marker="original"):
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


class BackupMigrationR9Tests(unittest.TestCase):
    def test_r9_identity_is_historical_anchor(self):
        notes = (ROOT / "docs/releases/RELEASE_NOTES_v10.8-r9.md").read_text(encoding="utf-8")
        self.assertIn("10.8-r9", notes)
        self.assertGreaterEqual(version_key(main.APP_VERSION), (10, 8, 9, 0))

    def test_main_keeps_compatibility_wrappers_only(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn("import backup_migration as backup_store", source)
        self.assertIn("return backup_store.find_legacy_database(APP_DIR, DB_PATH)", source)
        self.assertIn("return backup_store.backup_database(DB_PATH, BACKUP_DIR, label)", source)
        self.assertIn("return backup_store.auto_backup_database(DB_PATH, BACKUP_DIR)", source)
        self.assertIn("return backup_store.validate_database_file(path)", source)
        self.assertIn("backup_store.restore_database_from_file(", source)
        start = source.index("def find_legacy_database():")
        end = source.index("ACTIVITIES = {", start)
        section = source[start:end]
        self.assertNotIn("src_con = sqlite3.connect", section)
        self.assertNotIn("shutil.copy2(old, tmp)", section)

    def test_backup_is_consistent_and_valid(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_path = root / "driver_worktime.sqlite3"
            backups = root / "Backups"
            backups.mkdir()
            make_taxo_db(db_path)
            created = backup_migration.backup_database(db_path, backups, "manual")
            self.assertTrue(created.exists())
            ok, details = backup_migration.validate_database_file(created)
            self.assertTrue(ok, details)
            con = sqlite3.connect(created)
            try:
                self.assertEqual(con.execute("SELECT value FROM marker").fetchone()[0], "original")
            finally:
                con.close()

    def test_restore_creates_safety_backup_before_replacing_current_db(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_path = root / "driver_worktime.sqlite3"
            source = root / "restore.sqlite3"
            backups = root / "Backups"
            backups.mkdir()
            make_taxo_db(db_path, "before")
            make_taxo_db(source, "restored")
            init_calls = []

            safety, details = backup_migration.restore_database_from_file(
                source, db_path, backups, lambda: init_calls.append("init")
            )
            self.assertTrue(Path(safety).exists())
            self.assertIn("База справна", details)
            self.assertEqual(init_calls, ["init"])

            con = sqlite3.connect(db_path)
            try:
                self.assertEqual(con.execute("SELECT value FROM marker").fetchone()[0], "restored")
            finally:
                con.close()
            con = sqlite3.connect(safety)
            try:
                self.assertEqual(con.execute("SELECT value FROM marker").fetchone()[0], "before")
            finally:
                con.close()

    def test_legacy_migration_does_not_overwrite_existing_workspace_database(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            app_dir = root / "current" / "app"
            app_dir.mkdir(parents=True)
            db_path = root / "workspace" / "Data" / "driver_worktime.sqlite3"
            db_path.parent.mkdir(parents=True)
            make_taxo_db(db_path, "current")
            legacy = app_dir.parent / "driver_worktime.sqlite3"
            make_taxo_db(legacy, "legacy")

            migrated, old = backup_migration.migrate_legacy_database(app_dir, db_path)
            self.assertFalse(migrated)
            self.assertIsNone(old)
            con = sqlite3.connect(db_path)
            try:
                self.assertEqual(con.execute("SELECT value FROM marker").fetchone()[0], "current")
            finally:
                con.close()

    def test_infrastructure_module_contains_no_tk_ui_dependency(self):
        source = (ROOT / "backup_migration.py").read_text(encoding="utf-8")
        self.assertNotIn("import tkinter", source)
        self.assertNotIn("messagebox", source)
        self.assertNotIn("filedialog", source)


if __name__ == "__main__":
    unittest.main()
