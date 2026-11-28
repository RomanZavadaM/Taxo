# -*- coding: utf-8 -*-
"""10.25-r6 prep: synthetic immutable briefing planning and backup/restore."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

import briefing_planner as planner
import workspace


class BriefingPlanningR1PrepTests(unittest.TestCase):
    def test_candidate_identity_and_package_guard(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.25-r6\n")
        self.assertIn('APP_VERSION = "10.25-r6"', (root / "main.py").read_text("utf-8"))
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn("Taxo 10.25-r6 - START", start)
        self.assertIn("briefing_planner.py", start)
        self.assertEqual((root / ".release" / "full-current").read_text("utf-8"), "10.25-r6\n")
        self.assertEqual((root / ".release" / "stable-current").read_text("utf-8"), "10.24-r9\n")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="taxo_1025_r1_")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        paths = workspace.ensure_workspace(self.root)
        for db_path in (paths["main_db"], paths["tacho_db"]):
            con = sqlite3.connect(str(db_path))
            try:
                con.execute(
                    "CREATE TABLE synthetic_backup_guard("
                    "id INTEGER PRIMARY KEY, value TEXT)"
                )
                con.execute(
                    "INSERT INTO synthetic_backup_guard(value) VALUES('ok')"
                )
                con.commit()
            finally:
                con.close()

    @staticmethod
    def people():
        return (
            {
                "id": 11,
                "name": "Іваненко Іван",
                "personnel_no": "011",
                "position": "Водій",
            },
            {
                "id": 12,
                "name": "Петренко Петро",
                "personnel_no": "012",
                "position": "Водій",
            },
        )

    def test_revision_sessions_status_and_backup_restore_round_trip(self):
        first = planner.create_program(
            self.root,
            direction="БДР",
            kind="Повторний",
            title="Сезонна безпека руху",
            program_text="Редакція 1. Осінньо-зимовий період.",
            source_note="Локальна програма підприємства",
            approved_by="Керівник підприємства",
            valid_from="2026-10-01",
        )
        self.assertEqual(first.revision, 1)

        planned = planner.create_planned_session(
            self.root,
            planning_key="BDR:repeat:drivers:2027-Q1",
            program_id=first.program_id,
            program_revision=first.revision,
            scheduled_for="2027-01-15",
            participants=self.people(),
        )
        self.assertEqual(planned.status, planner.STATUS_PLANNED)
        self.assertEqual(planned.program_revision, 1)
        self.assertEqual(
            [row.employee_id for row in planned.participants],
            [11, 12],
        )

        second = planner.revise_program(
            self.root,
            first.program_id,
            program_text="Редакція 2. Весняно-літній період.",
            valid_from="2027-03-01",
            approved_by="Керівник підприємства",
        )
        self.assertEqual(second.revision, 2)
        self.assertEqual(
            planner.get_program_revision(
                self.root, first.program_id, 1
            ).program_text,
            "Редакція 1. Осінньо-зимовий період.",
        )
        self.assertEqual(
            planner.program_for_session(self.root, planned).revision,
            1,
        )

        with self.assertRaisesRegex(ValueError, "таким ключем"):
            planner.create_planned_session(
                self.root,
                planning_key="bdr:REPEAT:drivers:2027-q1",
                program_id=first.program_id,
                program_revision=second.revision,
                scheduled_for="2027-01-20",
                participants=self.people(),
            )

        event = planner.create_event_session(
            self.root,
            program_id=first.program_id,
            program_revision=second.revision,
            scheduled_for="2027-01-10",
            reason="Зміна локальної інструкції після небезпечної події",
            participants=(self.people()[1],),
        )
        self.assertEqual(event.mode, planner.MODE_EVENT)
        self.assertEqual(event.planning_key, "")

        prepared = planner.mark_prepared(self.root, planned.session_id)
        self.assertEqual(prepared.status, planner.STATUS_PREPARED)
        self.assertTrue(prepared.prepared_at)
        self.assertFalse(prepared.conducted_on)
        self.assertFalse(prepared.evidence_note)

        conducted_event = planner.mark_conducted(
            self.root,
            event.session_id,
            conducted_on="2027-01-10",
            evidence_note="Паперовий журнал БДР, запис 10.01.2027, стор. 12",
        )
        self.assertEqual(
            conducted_event.status, planner.STATUS_CONDUCTED
        )
        self.assertEqual(conducted_event.conducted_on, "2027-01-10")
        self.assertEqual(
            planner.get_session(self.root, planned.session_id).status,
            planner.STATUS_PREPARED,
        )
        with self.assertRaisesRegex(ValueError, "історію не переписувати"):
            planner.mark_conducted(
                self.root,
                event.session_id,
                conducted_on="2027-01-11",
                evidence_note="Інший запис",
            )

        current_plan = planner.get_session(self.root, planned.session_id)
        self.assertEqual(
            planner.status_at(current_plan, date(2027, 1, 16)),
            "overdue",
        )
        self.assertEqual(
            planner.status_at(conducted_event, date(2027, 2, 1)),
            planner.STATUS_CONDUCTED,
        )

        before = planner.read_state(self.root)
        self.assertEqual(len(before.programs), 2)
        self.assertEqual(len(before.sessions), 2)

        archive = workspace.create_workspace_backup_archive(
            self.root,
            Path(self.temp.name) / "briefing-r1-backup.zip",
            app_version="10.25-r6",
        )
        restored = Path(self.temp.name) / "restored"
        workspace.restore_workspace_backup_archive(archive, restored)
        after = planner.read_state(restored)
        self.assertEqual(after, before)

        restored_plan = planner.get_session(restored, planned.session_id)
        self.assertEqual(
            [row.name for row in restored_plan.participants],
            ["Іваненко Іван", "Петренко Петро"],
        )
        self.assertEqual(
            planner.program_for_session(restored, restored_plan).program_text,
            "Редакція 1. Осінньо-зимовий період.",
        )

    def test_fail_closed_store_and_explicit_conducted_evidence(self):
        program = planner.create_program(
            self.root,
            direction="Охорона праці",
            kind="Повторний",
            title="Повторний інструктаж",
            program_text="Тестова локальна програма.",
            valid_from="2026-11-01",
        )
        session = planner.create_planned_session(
            self.root,
            planning_key="OSH:repeat:test:2026-11",
            program_id=program.program_id,
            program_revision=1,
            scheduled_for="2026-11-30",
            participants=(self.people()[0],),
        )
        with self.assertRaisesRegex(ValueError, "паперового запису"):
            planner.mark_conducted(
                self.root,
                session.session_id,
                conducted_on="2026-11-30",
                evidence_note="",
            )

        root = planner.planning_root(self.root)
        (root / "unexpected.bin").write_bytes(b"not allowed")
        with self.assertRaisesRegex(ValueError, "невідомий об'єкт"):
            planner.read_state(self.root)

    def test_duplicate_json_keys_are_rejected(self):
        root = planner.planning_root(self.root)
        root.mkdir(parents=True, exist_ok=True)
        planner.planning_path(self.root).write_text(
            '{"format":"taxo.briefing-planning.v1",'
            '"format":"taxo.briefing-planning.v1",'
            '"programs":[],"sessions":[]}\n',
            "utf-8",
        )
        with self.assertRaisesRegex(ValueError, "дубльований ключ"):
            planner.read_state(self.root)


if __name__ == "__main__":
    unittest.main()
