# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import unittest
from pathlib import Path

from database_runtime import (
    SUPPORTED_SCHEMA_VERSION,
    SchemaTooNewError,
    connect_database,
    mark_schema_version,
    schema_version,
)
from v1099_schema_compatibility import FEATURE_VERSION, install


class SchemaCompatibilityR9Tests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(FEATURE_VERSION, "10.9-r9")
        self.assertEqual(SUPPORTED_SCHEMA_VERSION, 1)

    def test_opening_legacy_database_does_not_stamp_it_implicitly(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "legacy.db"
            sqlite3.connect(path).close()
            con = connect_database(path)
            try:
                self.assertEqual(schema_version(con), 0)
            finally:
                con.close()
            raw = sqlite3.connect(path)
            try:
                self.assertEqual(raw.execute("PRAGMA user_version").fetchone()[0], 0)
            finally:
                raw.close()

    def test_successful_baseline_stamp_is_explicit_and_persistent(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "baseline.db"
            con = connect_database(path)
            try:
                con.execute("CREATE TABLE sample(id INTEGER PRIMARY KEY)")
                self.assertEqual(mark_schema_version(con), 1)
                con.commit()
            finally:
                con.close()
            reopened = connect_database(path)
            try:
                self.assertEqual(schema_version(reopened), 1)
            finally:
                reopened.close()

    def test_future_schema_is_rejected_before_use(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "future.db"
            raw = sqlite3.connect(path)
            raw.execute("PRAGMA user_version=2")
            raw.execute("CREATE TABLE future_only(id INTEGER PRIMARY KEY)")
            raw.commit()
            raw.close()
            with self.assertRaisesRegex(SchemaTooNewError, "новішою версією Taxo"):
                connect_database(path)

    def test_schema_version_cannot_be_downgraded(self):
        con = sqlite3.connect(":memory:")
        try:
            con.execute("PRAGMA user_version=2")
            with self.assertRaises(SchemaTooNewError):
                mark_schema_version(con, 1)
            self.assertEqual(con.execute("PRAGMA user_version").fetchone()[0], 2)
        finally:
            con.close()

    def test_layer_stamps_only_after_successful_original_init(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "wrapped.db"

            class Core:
                APP_VERSION = "old"
                def __init__(self):
                    self.calls = 0
                def db(self):
                    return connect_database(path)
                def init_db(self):
                    self.calls += 1
                    con = self.db()
                    try:
                        con.execute("CREATE TABLE IF NOT EXISTS ready(id INTEGER PRIMARY KEY)")
                        con.commit()
                    finally:
                        con.close()
                    return "ok"

            core = Core()
            App = type("App", (), {})
            install(core, App)
            self.assertEqual(core.init_db(), "ok")
            self.assertEqual(core.calls, 1)
            con = connect_database(path)
            try:
                self.assertEqual(schema_version(con), 1)
                self.assertIsNotNone(con.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='ready'"
                ).fetchone())
            finally:
                con.close()

    def test_failed_original_init_never_marks_schema(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "failed.db"

            class Core:
                APP_VERSION = "old"
                def db(self):
                    return connect_database(path)
                def init_db(self):
                    con = self.db()
                    try:
                        con.execute("CREATE TABLE partial(id INTEGER PRIMARY KEY)")
                        con.commit()
                    finally:
                        con.close()
                    raise RuntimeError("boom")

            core = Core()
            install(core, type("App", (), {}))
            with self.assertRaisesRegex(RuntimeError, "boom"):
                core.init_db()
            raw = sqlite3.connect(path)
            try:
                self.assertEqual(raw.execute("PRAGMA user_version").fetchone()[0], 0)
            finally:
                raw.close()


if __name__ == "__main__":
    unittest.main()
