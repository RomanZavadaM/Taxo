# -*- coding: utf-8 -*-
"""10.14-r5 — order appendices follow paper-first free-editing policy."""
import json
import sqlite3
from pathlib import Path
import unittest

import main
import operations_orders as ops
import v1073_features as appendices
from order_edit_actions import delete_order


class AppendixFreeEditingR5Tests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys=ON")
        self.con.executescript("""
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY,last_name TEXT,first_name TEXT,middle_name TEXT,
            position TEXT,birth_date TEXT,actual_address TEXT,registered_address TEXT
        );
        CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT);
        CREATE TABLE employee_military_profile(
            employee_id INTEGER PRIMARY KEY,military_specialty TEXT,military_rank TEXT
        );
        """)
        ops.ensure_schema_on_connection(self.con)
        appendices.ensure_appendix_schema_on_connection(self.con)
        self.order_id = ops.create_order(
            self.con,
            order_type=ops.TYPE_GENERIC,
            order_no="31",
            order_date="2026-11-09",
            place="Львів",
            subject="Робочий наказ",
            preamble="",
            body_text="1. Виконати.",
        )
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def test_version_and_start_identity(self):
        self.assertIn(main.APP_VERSION, ("10.14-r5", "10.14-r6", "10.14-r7", "10.14-r8", "10.14-r9", "10.14-r10", "10.15-r1", "10.15-r2", "10.15-r3", "10.15-r4", "10.15-r5", "10.15-r7", "10.15-r8", "10.15-r9", "10.15-r10", "10.16-r1", "10.16-r2", "10.16-r3", "10.16-r4", "10.16-r5", "10.16-r6", "10.16-r7", "10.16-r8", "10.16-r9", "10.16-r10", "10.17-r1", "10.17-r2", "10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6", "10.17-r7", "10.17-r8", "10.17-r9", "10.17-r10"))
        self.assertIn("Version: " + main.APP_VERSION, Path("VERSION.txt").read_text(encoding="utf-8"))
        self.assertIn("Taxo " + main.APP_VERSION, Path("START.bat").read_text(encoding="utf-8"))

    def test_approved_and_cancelled_order_appendix_can_be_edited_and_deleted(self):
        aid = appendices.save_appendix(
            self.con, self.order_id, title="Початковий", content="Текст"
        )
        ops.approve_order(self.con, self.order_id)
        appendices.save_appendix(
            self.con, self.order_id, title="Виправлений", content="Новий текст",
            appendix_id=aid,
        )
        self.assertEqual(
            appendices.list_appendices(self.con, self.order_id)[0]["title"],
            "Виправлений",
        )
        ops.cancel_order(self.con, self.order_id)
        appendices.delete_appendix(self.con, self.order_id, aid)
        self.assertEqual(appendices.list_appendices(self.con, self.order_id), [])

    def test_order_delete_audit_snapshot_keeps_appendices(self):
        aid = appendices.save_appendix(
            self.con, self.order_id, title="Додаток А", content="Рядок 1\nРядок 2"
        )
        self.con.commit()
        before = delete_order(self.con, self.order_id)
        self.assertEqual([row["id"] for row in before["appendices"]], [aid])
        self.assertEqual(
            self.con.execute(
                "SELECT count(*) FROM operations_order_appendices WHERE order_id=?",
                (self.order_id,),
            ).fetchone()[0],
            0,
        )
        log = self.con.execute(
            "SELECT before_json FROM operations_change_log "
            "WHERE entity_type='order' AND entity_id=? AND action='delete'",
            (self.order_id,),
        ).fetchone()
        snapshot = json.loads(log["before_json"])
        self.assertEqual(snapshot["appendices"][0]["title"], "Додаток А")

    def test_ui_has_no_draft_only_appendix_lock(self):
        source = Path("src/taxo/v1073_features.py").read_text(encoding="utf-8")
        self.assertNotIn("Додатки затвердженого або скасованого наказу не редагуються", source)
        self.assertNotIn("Редагувати додатки можна лише у чернетці наказу", source)
        self.assertIn("Статус наказу або паперовий підпис не блокують їх редагування", source)


if __name__ == "__main__":
    unittest.main()
