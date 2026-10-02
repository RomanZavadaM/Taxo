# -*- coding: utf-8 -*-
import inspect
import re
import sqlite3
import tempfile
import unittest
from pathlib import Path

import database_runtime
import main


ROOT = Path(__file__).resolve().parents[1]


def version_key(value: str):
    match = re.fullmatch(r"(\d+)\.(\d+)-r(\d+)(?:\.(\d+))?", value)
    if not match:
        raise AssertionError(f"unexpected version format: {value}")
    major, minor, revision, subrevision = match.groups()
    return int(major), int(minor), int(revision), int(subrevision or 0)


class DatabaseRuntimeR10Tests(unittest.TestCase):
    def test_r10_identity_is_historical_anchor(self):
        notes = (ROOT / "docs/releases/RELEASE_NOTES_v10.8-r10.md").read_text(encoding="utf-8")
        self.assertIn("10.8-r10", notes)
        self.assertGreaterEqual(version_key(main.APP_VERSION), (10, 8, 10, 0))

    def test_infrastructure_module_has_no_tk_dependency(self):
        source = Path("database_runtime.py").read_text(encoding="utf-8")
        self.assertNotIn("import tkinter", source)
        self.assertNotIn("from tkinter", source)

    def test_connection_preserves_historical_sqlite_policy(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "runtime.db"
            con = database_runtime.connect_database(db_path)
            try:
                self.assertIs(con.row_factory, sqlite3.Row)
                self.assertEqual(con.execute("PRAGMA foreign_keys").fetchone()[0], 1)
                self.assertEqual(con.execute("PRAGMA busy_timeout").fetchone()[0], 30000)
                self.assertEqual(con.execute("PRAGMA journal_mode").fetchone()[0].lower(), "delete")
                self.assertEqual(con.execute("PRAGMA synchronous").fetchone()[0], 2)
                con.execute("CREATE TABLE smoke(id INTEGER PRIMARY KEY, value TEXT)")
                con.execute("INSERT INTO smoke(value) VALUES ('ok')")
                row = con.execute("SELECT id, value FROM smoke").fetchone()
                self.assertEqual(row["value"], "ok")
            finally:
                con.close()

    def test_main_keeps_db_compatibility_wrapper_only(self):
        source = inspect.getsource(main.db)
        self.assertIn("_connect_database(DB_PATH)", source)
        self.assertNotIn("PRAGMA", source)
        self.assertNotIn("sqlite3.connect", source)

    def test_start_guard_requires_runtime_module(self):
        start = Path("START.bat").read_text(encoding="utf-8")
        self.assertIn('if not exist "src\\taxo\\database_runtime.py" goto :package_incomplete', start)


if __name__ == "__main__":
    unittest.main()
