# -*- coding: utf-8 -*-
import sqlite3
import unittest

from main import attestation_history_query


class TestAttestationArchiveFiltersR93(unittest.TestCase):
    def setUp(self):
        self.con=sqlite3.connect(":memory:")
        self.con.row_factory=sqlite3.Row
        self.con.executescript("""
        CREATE TABLE drivers(
            id INTEGER PRIMARY KEY,
            last_name TEXT,
            first_name TEXT
        );
        CREATE TABLE attestations(
            id INTEGER PRIMARY KEY,
            driver_id INTEGER NOT NULL,
            period_from TEXT NOT NULL,
            period_to TEXT NOT NULL,
            activity_no INTEGER NOT NULL,
            place TEXT DEFAULT '',
            form_date TEXT DEFAULT '',
            file_path TEXT DEFAULT '',
            pdf_path TEXT DEFAULT '',
            jpg_page1_path TEXT DEFAULT '',
            jpg_page2_path TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            revision INTEGER DEFAULT 1,
            updated_at TEXT DEFAULT '',
            deleted_at TEXT DEFAULT '',
            delete_reason TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        INSERT INTO drivers VALUES(1,'Дробот','Олег');
        INSERT INTO drivers VALUES(2,'Тестовий','Водій');

        INSERT INTO attestations(
            id,driver_id,period_from,period_to,activity_no,form_date,status,created_at
        ) VALUES
            (1,1,'2026-07-15T17:15','2026-07-22T05:15',16,'2026-07-22','active','2026-07-22T06:00:00'),
            (2,1,'2026-09-10T18:00','2026-09-17T06:00',16,'2026-09-17','active','2026-09-17T07:00:00'),
            (3,2,'2026-08-01T08:00','2026-08-05T08:00',15,'2026-08-05','active','2026-08-05T09:00:00'),
            (4,1,'2026-09-01T08:00','2026-09-03T08:00',14,'2026-09-03','deleted','2026-09-03T09:00:00');
        """)

    def tearDown(self):
        self.con.close()

    def query(self, **kwargs):
        sql,params=attestation_history_query(**kwargs)
        return self.con.execute(sql,params).fetchall()

    def test_selected_driver_is_filtered_and_newest_period_is_first(self):
        rows=self.query(mode="Активні",driver_id=1)
        self.assertEqual([r["id"] for r in rows],[2,1])

    def test_month_filter_uses_form_month(self):
        rows=self.query(mode="Активні",year=2026,month=8)
        self.assertEqual([r["id"] for r in rows],[3])

    def test_status_driver_and_month_filters_combine(self):
        rows=self.query(mode="Вилучені",driver_id=1,year=2026,month=9)
        self.assertEqual([r["id"] for r in rows],[4])

    def test_all_has_no_hidden_limit(self):
        rows=self.query(mode="Усі")
        self.assertEqual([r["id"] for r in rows],[2,4,3,1])


if __name__ == "__main__":
    unittest.main()
