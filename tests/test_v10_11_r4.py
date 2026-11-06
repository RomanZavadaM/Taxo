# -*- coding: utf-8 -*-
"""Regression: Taxo 10.11-r4 tachograph control-history protection."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

import tachograph


class TachographControlHistoryR4Tests(unittest.TestCase):
    def setUp(self):
        self.old_root = Path(tachograph.DATA_ROOT)
        self.temp = tempfile.TemporaryDirectory()
        tachograph.configure_workspace(self.temp.name)
        tachograph.init_tacho_db()

    def tearDown(self):
        tachograph.configure_workspace(self.old_root)
        self.temp.cleanup()

    def _disc(self, con, name="disc.png"):
        cur = con.execute(
            """INSERT INTO discs(
                   source_path,scan_name,disc_no,created_at
               ) VALUES(?,?,1,'2026-11-06T12:00:00')""",
            (f"workspace://Data/TachographScans/{name}", name),
        )
        return int(cur.lastrowid)

    def test_saved_protocol_blocks_helper_delete_and_preserves_snapshot(self):
        con = tachograph.tdb()
        disc_id = self._disc(con)
        con.execute(
            """INSERT INTO control_protocols(
                   disc_id,snapshot_text,created_at
               ) VALUES(?,?,?)""",
            (disc_id, "Історичний контрольний знімок", "2026-11-06T12:01:00"),
        )
        con.commit()

        with self.assertRaisesRegex(ValueError, "збережено контрольний протокол"):
            tachograph.delete_disc_preserving_control_history(con, disc_id)

        disc = con.execute("SELECT id FROM discs WHERE id=?", (disc_id,)).fetchone()
        protocol = con.execute(
            "SELECT snapshot_text FROM control_protocols WHERE disc_id=?",
            (disc_id,),
        ).fetchone()
        self.assertIsNotNone(disc)
        self.assertEqual(protocol["snapshot_text"], "Історичний контрольний знімок")
        con.close()

    def test_database_trigger_blocks_direct_cascade_delete(self):
        con = tachograph.tdb()
        disc_id = self._disc(con, "direct.png")
        con.execute(
            """INSERT INTO control_protocols(
                   disc_id,snapshot_text,created_at
               ) VALUES(?,?,?)""",
            (disc_id, "Не видаляти", "2026-11-06T12:02:00"),
        )
        con.commit()

        with self.assertRaisesRegex(
            sqlite3.IntegrityError,
            "Збережений протокол контролю тахокарти",
        ):
            con.execute("DELETE FROM discs WHERE id=?", (disc_id,))
        con.rollback()

        self.assertEqual(
            con.execute("SELECT COUNT(*) FROM discs WHERE id=?", (disc_id,)).fetchone()[0],
            1,
        )
        self.assertEqual(
            con.execute(
                "SELECT COUNT(*) FROM control_protocols WHERE disc_id=?",
                (disc_id,),
            ).fetchone()[0],
            1,
        )
        con.close()

    def test_unprotected_disc_still_deletes_normally_with_intervals(self):
        con = tachograph.tdb()
        disc_id = self._disc(con, "draft.png")
        con.execute(
            """INSERT INTO intervals(
                   disc_id,start_min,end_min,activity,confidence,source
               ) VALUES(?,?,?,?,?,?)""",
            (disc_id, 480, 540, "Керування", 1.0, "manual"),
        )
        con.commit()

        self.assertTrue(tachograph.delete_disc_preserving_control_history(con, disc_id))
        con.commit()

        self.assertEqual(
            con.execute("SELECT COUNT(*) FROM discs WHERE id=?", (disc_id,)).fetchone()[0],
            0,
        )
        self.assertEqual(
            con.execute("SELECT COUNT(*) FROM intervals WHERE disc_id=?", (disc_id,)).fetchone()[0],
            0,
        )
        con.close()

    def test_init_installs_database_level_history_guard(self):
        con = tachograph.tdb()
        row = con.execute(
            """SELECT sql FROM sqlite_master
                 WHERE type='trigger'
                   AND name='trg_tachograph_control_protocol_history'"""
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertIn("BEFORE DELETE ON discs", row["sql"])
        self.assertIn("control_protocols", row["sql"])
        con.close()


if __name__ == "__main__":
    unittest.main()
