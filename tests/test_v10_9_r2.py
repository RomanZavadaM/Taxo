# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

import waybill_integrity as wi


def make_schema(con):
    con.executescript(
        """
        PRAGMA foreign_keys=ON;
        CREATE TABLE drivers(
            id INTEGER PRIMARY KEY,
            last_name TEXT DEFAULT '', first_name TEXT DEFAULT ''
        );
        CREATE TABLE worklog(
            id INTEGER PRIMARY KEY,
            driver_id INTEGER NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
            work_date TEXT NOT NULL
        );
        CREATE TABLE employee_time_entries(
            id INTEGER PRIMARY KEY,
            work_date TEXT NOT NULL
        );
        CREATE TABLE waybills(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worklog_id INTEGER NOT NULL REFERENCES worklog(id) ON DELETE CASCADE,
            driver_id INTEGER NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
            document_series TEXT DEFAULT '',
            document_number TEXT DEFAULT '',
            issued_at TEXT DEFAULT '',
            updated_at TEXT DEFAULT ''
        );
        CREATE TABLE waybill_events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            waybill_id INTEGER NOT NULL REFERENCES waybills(id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            document_series TEXT DEFAULT '',
            document_number TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        """
    )


class FileCore:
    def __init__(self, path):
        self.path = path

    def db(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con


class WaybillIntegrityTests(unittest.TestCase):
    def test_retention_keeps_worklog_referenced_by_waybill(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "taxo.sqlite3"
            con = sqlite3.connect(path)
            make_schema(con)
            con.execute("INSERT INTO drivers(id,last_name) VALUES(1,'Тест')")
            con.execute("INSERT INTO worklog(id,driver_id,work_date) VALUES(1,1,'2020-01-01')")
            con.execute("INSERT INTO worklog(id,driver_id,work_date) VALUES(2,1,'2020-01-02')")
            con.execute("INSERT INTO employee_time_entries(id,work_date) VALUES(1,'2020-01-01')")
            con.execute(
                "INSERT INTO waybills(worklog_id,driver_id,document_series,document_number,issued_at) "
                "VALUES(1,1,'AA','000001','2020-01-01T08:00:00')"
            )
            con.commit(); con.close()

            wi.purge_old_preserving_issued_waybills(FileCore(path), today=date(2026, 10, 1))

            check = sqlite3.connect(path)
            self.assertEqual(check.execute("SELECT id FROM worklog ORDER BY id").fetchall(), [(1,)])
            self.assertEqual(check.execute("SELECT COUNT(*) FROM waybills").fetchone()[0], 1)
            self.assertEqual(check.execute("SELECT COUNT(*) FROM employee_time_entries").fetchone()[0], 0)
            check.close()

    def test_voided_number_cannot_be_reused_after_reissue(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        make_schema(con)
        con.execute("INSERT INTO drivers(id,last_name) VALUES(1,'Тест')")
        con.execute("INSERT INTO worklog(id,driver_id,work_date) VALUES(1,1,'2026-09-01')")
        con.execute("INSERT INTO worklog(id,driver_id,work_date) VALUES(2,1,'2026-09-02')")
        con.execute(
            "INSERT INTO waybills(id,worklog_id,driver_id,document_series,document_number,issued_at,updated_at) "
            "VALUES(10,1,1,'AA','000777','2026-09-01T08:00:00','2026-09-01T08:00:00')"
        )
        con.execute(
            "INSERT INTO waybill_events(waybill_id,event_type,document_series,document_number,created_at) "
            "VALUES(10,'void','AA','000777','2026-09-01T12:00:00')"
        )
        wi.ensure_schema_on_connection(con)
        con.commit()

        self.assertTrue(wi.number_was_issued(con, 'AA', '000777'))
        con.execute(
            "UPDATE waybills SET document_number='000778',updated_at='2026-09-02T08:00:00' WHERE id=10"
        )
        self.assertTrue(wi.number_was_issued(con, 'AA', '000778'))

        with self.assertRaises(sqlite3.IntegrityError):
            con.execute(
                "INSERT INTO waybills(worklog_id,driver_id,document_series,document_number,issued_at) "
                "VALUES(2,1,'AA','000777','2026-09-02T09:00:00')"
            )
        con.close()

    def test_driver_and_worklog_with_issued_waybill_are_not_deletable(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        make_schema(con)
        con.execute("INSERT INTO drivers(id,last_name) VALUES(1,'Тест')")
        con.execute("INSERT INTO worklog(id,driver_id,work_date) VALUES(1,1,'2026-09-01')")
        con.execute(
            "INSERT INTO waybills(worklog_id,driver_id,document_series,document_number,issued_at) "
            "VALUES(1,1,'AA','000901','2026-09-01T08:00:00')"
        )
        wi.ensure_schema_on_connection(con)
        con.commit()

        with self.assertRaises(sqlite3.IntegrityError):
            con.execute("DELETE FROM worklog WHERE id=1")
        con.rollback()
        with self.assertRaises(sqlite3.IntegrityError):
            con.execute("DELETE FROM drivers WHERE id=1")
        con.close()

    def test_revision_identity(self):
        self.assertEqual(wi.APP_VERSION, "10.9-r2")


if __name__ == "__main__":
    unittest.main()
