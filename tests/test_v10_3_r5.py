# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file

ROOT=Path(__file__).resolve().parents[1]


class TestTaxo103R5AttestationArchive(unittest.TestCase):
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
            fact_from_confirmed INTEGER DEFAULT 0,
            fact_to_confirmed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );

        INSERT INTO drivers VALUES(1,'Гавц','Богдан');
        INSERT INTO drivers VALUES(2,'Інший','Водій');

        INSERT INTO attestations(
            id,driver_id,period_from,period_to,activity_no,form_date,status,revision,updated_at,created_at
        ) VALUES
            (77,1,'19:40 09.09.2026','19:45 09.09.2026',16,'2026-09-09','active',1,'2026-09-09T20:00:00','2026-09-09T20:00:00'),
            (69,1,'19:25 15.09.2026','08:15 18.09.2026',16,'2026-09-18','active',1,'2026-09-18T08:20:00','2026-09-18T08:20:00'),
            (63,1,'19:25 12.09.2026','08:15 15.09.2026',16,'2026-09-15','active',1,'2026-09-15T08:20:00','2026-09-15T08:20:00'),
            (92,1,'20:25 21.09.2026','07:45 24.09.2026',16,'2026-09-24','active',2,'2026-09-22T10:30:00','2026-09-21T20:30:00'),
            (74,1,'19:40 18.09.2026','07:45 21.09.2026',16,'2026-09-21','active',2,'2026-09-22T10:20:00','2026-09-18T19:50:00'),
            (101,2,'20:00 20.09.2026','08:00 22.09.2026',16,'2026-09-22','active',1,'2026-09-22T08:00:00','2026-09-22T08:00:00'),
            (102,2,'20:00 18.09.2026','08:00 20.09.2026',16,'2026-09-20','deleted',2,'2026-09-21T09:00:00','2026-09-20T08:00:00');
        """)

    def tearDown(self):
        self.con.close()

    def query(self, **kwargs):
        sql,params=main.attestation_history_query(**kwargs)
        return self.con.execute(sql,params).fetchall()

    def test_version_is_r5(self):
        self.assertEqual(main.APP_VERSION,"10.3-r5")
        self.assertEqual(version_from_file(ROOT/"VERSION.txt"),"10.3-r5")
        self.assertEqual(
            start_archive_stem("10.3-r5"),
            "Taxo_v10_3_candidate_r5_START",
        )

    def test_period_newest_sorts_real_display_dates_not_clock_prefix(self):
        rows=self.query(
            mode="Активні",driver_id=1,
            sort_mode="Період — новіші"
        )
        self.assertEqual([r["id"] for r in rows],[92,74,69,63,77])

    def test_period_oldest_is_reverse_chronological_direction(self):
        rows=self.query(
            mode="Активні",driver_id=1,
            sort_mode="Період — старіші"
        )
        self.assertEqual([r["id"] for r in rows],[77,63,69,74,92])

    def test_latest_changes_puts_just_edited_form_first(self):
        rows=self.query(
            mode="Активні",driver_id=1,
            sort_mode="Останні створені/змінені"
        )
        self.assertEqual([r["id"] for r in rows][:2],[92,74])

    def test_filtered_counts_can_be_derived_from_same_filter_scope(self):
        visible=self.query(
            mode="Активні",driver_id=2,
            sort_mode="Останні створені/змінені"
        )
        all_filtered=self.query(
            mode="Усі",driver_id=2,
            sort_mode="Останні створені/змінені"
        )
        active=sum(1 for r in all_filtered if (r["status"] or "active")=="active")
        deleted=len(all_filtered)-active
        self.assertEqual(len(visible),1)
        self.assertEqual(len(all_filtered),2)
        self.assertEqual((active,deleted),(1,1))

    def test_gap_button_is_context_sensitive(self):
        src=(ROOT/"main.py").read_text("utf-8")
        self.assertIn('text="Уточнити фактичні межі"',src)
        self.assertIn('text="Підставити у форму"',src)
        self.assertIn("self._edit_attestation_fact_boundaries(",src)

    def test_archive_has_visible_sort_selector_and_changed_column(self):
        src=(ROOT/"main.py").read_text("utf-8")
        self.assertIn('text="Сортування:"',src)
        self.assertIn('"changed":"Змінено"',src)
        self.assertIn("усього в архіві",src)


if __name__=="__main__":
    unittest.main()
