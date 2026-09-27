# -*- coding: utf-8 -*-
import sqlite3
import unittest
from datetime import date, datetime
from pathlib import Path

import military_transport_2026 as mt

ROOT = Path(__file__).resolve().parents[1]


def make_db():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript("""
        PRAGMA foreign_keys=ON;
        CREATE TABLE vehicles(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            plate TEXT DEFAULT '',
            make_model TEXT DEFAULT '',
            active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        );
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT DEFAULT '',
            active INTEGER DEFAULT 1
        );
    """)
    mt.ensure_schema_on_connection(con)
    return con


def add_vehicle(con, name="Автобус тестовий", plate="AA0001AA"):
    cur = con.execute(
        "INSERT INTO vehicles(name,plate,make_model,active,created_at) VALUES(?,?,?,?,?)",
        (name, plate, "TEST MODEL", 1, "2026-09-27T00:00:00"),
    )
    return int(cur.lastrowid)


class MilitaryTransportProfileR10Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()
        self.vehicle_id = add_vehicle(self.con)

    def tearDown(self):
        self.con.close()

    def test_unknown_profile_is_clarification_not_violation(self):
        state = mt.profile_state(self.con, self.vehicle_id)
        self.assertEqual(state["status"], mt.STATUS_UNKNOWN)
        self.assertTrue(state["needs_clarification"])
        self.assertFalse(state["violation"])

    def test_profile_history_is_append_only(self):
        mt.set_profile(
            self.con, self.vehicle_id, status=mt.STATUS_DESIGNATED,
            accounting_authority="Тестовий орган", basis_document_no="A-1",
        )
        mt.set_profile(
            self.con, self.vehicle_id, status=mt.STATUS_ORDERED,
            accounting_authority="Тестовий орган", basis_document_no="B-2",
        )
        rows = mt.profile_history(self.con, self.vehicle_id)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["status"], mt.STATUS_ORDERED)
        self.assertEqual(rows[1]["status"], mt.STATUS_DESIGNATED)

    def test_operational_active_is_not_changed_by_military_transfer(self):
        order_id = mt.record_order(
            self.con, self.vehicle_id, mt.ORDER_PARTIAL, "2026-09-27",
            document_no="P-1", transfer_due_date="2026-09-30",
        )
        mt.set_order_status(self.con, order_id, mt.ORDER_TRANSFERRED, actual_at="2026-09-29T10:00")
        vehicle = self.con.execute("SELECT active FROM vehicles WHERE id=?", (self.vehicle_id,)).fetchone()
        self.assertEqual(vehicle["active"], 1)
        self.assertEqual(mt.profile_state(self.con, self.vehicle_id)["status"], mt.STATUS_TRANSFERRED)

    def test_transfer_and_return_are_military_facts(self):
        order_id = mt.record_order(
            self.con, self.vehicle_id, mt.ORDER_CONSOLIDATED, "2026-09-27",
            document_no="Z-1",
        )
        mt.set_order_status(self.con, order_id, mt.ORDER_TRANSFERRED, actual_at="2026-09-28T08:00")
        mt.set_order_status(
            self.con, order_id, mt.ORDER_RETURNED,
            actual_at="2026-10-05T12:30", return_reference="ACT-RETURN",
        )
        row = mt.list_orders(self.con, self.vehicle_id)[0]
        self.assertEqual(row["status"], mt.ORDER_RETURNED)
        self.assertEqual(row["actual_transfer_at"], "2026-09-28T08:00")
        self.assertEqual(row["returned_at"], "2026-10-05T12:30")
        self.assertEqual(row["return_reference"], "ACT-RETURN")
        self.assertEqual(mt.profile_state(self.con, self.vehicle_id)["status"], mt.STATUS_RETURNED)


class MilitaryTransportDeadlineR10Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()
        self.vehicle_id = add_vehicle(self.con)

    def tearDown(self):
        self.con.close()

    def test_feature_activation_in_september_does_not_backfill_june(self):
        created, deadline = mt.ensure_next_reporting_action(
            self.con, today=date(2026, 9, 27), feature_start=date(2026, 9, 27)
        )
        self.assertEqual(created, 1)
        self.assertEqual(deadline, date(2026, 12, 20))
        rows = mt.list_actions(self.con)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["due_date"], "2026-12-20")
        self.assertNotEqual(rows[0]["due_date"], "2026-06-20")

    def test_next_deadline_after_december_20_is_next_year_june(self):
        self.assertEqual(mt.next_reporting_deadline(date(2026, 12, 21)), date(2027, 6, 20))

    def test_deadline_on_control_date_is_same_day(self):
        self.assertEqual(mt.next_reporting_deadline(date(2026, 12, 20)), date(2026, 12, 20))

    def test_repeated_schedule_check_does_not_duplicate_same_report_task(self):
        mt.ensure_next_reporting_action(self.con, today=date(2026, 9, 27))
        mt.ensure_next_reporting_action(self.con, today=date(2026, 10, 1))
        rows = [r for r in mt.list_actions(self.con) if r["action_type"] == mt.ACTION_REPORT]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["due_date"], "2026-12-20")

    def test_no_explicit_event_means_no_seven_day_task(self):
        mt.ensure_next_reporting_action(self.con, today=date(2026, 9, 27))
        notices = [r for r in mt.list_actions(self.con) if r["action_type"] == mt.ACTION_NOTICE]
        self.assertEqual(notices, [])

    def test_explicit_qualifying_event_creates_seven_day_task(self):
        event_id, due = mt.record_notice_event(
            self.con, self.vehicle_id, mt.EVENT_OWNERSHIP, "2026-09-27", "synthetic event"
        )
        self.assertEqual(due, date(2026, 10, 4))
        notices = [r for r in mt.list_actions(self.con) if r["action_type"] == mt.ACTION_NOTICE]
        self.assertEqual(len(notices), 1)
        self.assertEqual(notices[0]["event_id"], event_id)
        self.assertEqual(notices[0]["due_date"], "2026-10-04")

    def test_submission_closes_matching_report_task(self):
        mt.ensure_next_reporting_action(self.con, today=date(2026, 9, 27))
        mt.record_submission(
            self.con, "2026-12-20", submitted_at="2026-12-18T11:00",
            authority="synthetic", reference="TEST",
        )
        row = mt.list_actions(self.con)[0]
        self.assertEqual(row["status"], mt.ACTION_DONE)
        self.assertEqual(row["reference"], "TEST")


class MilitaryTransportOrdersR10Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()
        self.vehicle_id = add_vehicle(self.con)

    def tearDown(self):
        self.con.close()

    def test_consolidated_and_partial_orders_remain_separate(self):
        mt.record_order(self.con, self.vehicle_id, mt.ORDER_CONSOLIDATED, "2026-09-20", document_no="Z-1")
        mt.record_order(self.con, self.vehicle_id, mt.ORDER_PARTIAL, "2026-09-21", document_no="P-1")
        rows = mt.list_orders(self.con, self.vehicle_id)
        self.assertEqual({r["order_kind"] for r in rows}, {mt.ORDER_CONSOLIDATED, mt.ORDER_PARTIAL})
        self.assertEqual({r["document_no"] for r in rows}, {"Z-1", "P-1"})

    def test_order_does_not_silently_create_seven_day_notice(self):
        mt.record_order(self.con, self.vehicle_id, mt.ORDER_PARTIAL, "2026-09-27")
        self.assertEqual(mt.list_actions(self.con), [])

    def test_worker_link_is_explicit_not_inferred_from_waybill_history(self):
        cur = self.con.execute(
            "INSERT INTO employees(last_name,first_name,middle_name,active) VALUES('Тест','Працівник','Один',1)"
        )
        employee_id = int(cur.lastrowid)
        self.assertEqual(mt.workers_for_vehicle(self.con, self.vehicle_id, date(2026, 9, 27)), [])
        mt.add_worker_link(
            self.con, self.vehicle_id, employee_id=employee_id,
            relation_note="synthetic explicit link", valid_from="2026-09-01",
        )
        rows = mt.workers_for_vehicle(self.con, self.vehicle_id, date(2026, 9, 27))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["employee_id"], employee_id)


class MilitaryTransportIntegrationR10Tests(unittest.TestCase):
    def test_module_is_independent_from_shlyakh_and_operational_documents(self):
        source = (ROOT / "military_transport_2026.py").read_text("utf-8")
        self.assertNotIn("import vehicle_registry", source)
        self.assertNotIn("import vehicle_documents", source)
        self.assertIn("vehicle_id", source)
        self.assertIn("LEGAL_BASIS", source)

    def test_legal_marker_and_dates_are_explicit(self):
        source = (ROOT / "military_transport_2026.py").read_text("utf-8")
        self.assertIn("№1921", source)
        self.assertIn("25.12.2025", source)
        self.assertIn("NOTICE_DAYS = 7", source)
        self.assertIn("REPORT_DATES = ((6, 20), (12, 20))", source)

    def test_r10_scope_declares_rollover_to_10_5_r1(self):
        scope = (ROOT / "docs/maintenance/R10_MILITARY_TRANSPORT_SCOPE.md").read_text("utf-8")
        self.assertIn("Taxo_v10_4_candidate_r10_START", scope)
        self.assertIn("10.5-r1", scope)


if __name__ == "__main__":
    unittest.main()
