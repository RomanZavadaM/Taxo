# -*- coding: utf-8 -*-
"""10.25-r5 prep: one synthetic end-to-end acceptance of Instructions r1-r4."""
from __future__ import annotations

import hashlib
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

import briefing_event_ui as event_ui
import briefing_planner as planner
import briefing_prepared_output as prepared_output
import briefing_quarter_view as quarter_view
import paper_document_store as document_store
import workspace


class InstructionsEndToEndR5PrepTests(unittest.TestCase):
    def test_candidate_identity_and_stable_marker(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.25-r5\n")
        self.assertIn('APP_VERSION = "10.25-r5"', (root / "main.py").read_text("utf-8"))
        self.assertIn("Taxo 10.25-r5 - START", (root / "START.bat").read_text("utf-8"))
        self.assertEqual((root / ".release" / "full-current").read_text("utf-8"), "10.25-r5\n")
        self.assertEqual((root / ".release" / "stable-current").read_text("utf-8"), "10.24-r9\n")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="taxo_1025_r5_")
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

        self.people = (
            {
                "id": 81,
                "name": "Іваненко Іван",
                "personnel_no": "081",
                "position": "Водій",
            },
            {
                "id": 82,
                "name": "Петренко Петро",
                "personnel_no": "082",
                "position": "Водій",
            },
        )

    @staticmethod
    def _sha256(path):
        digest = hashlib.sha256()
        with Path(path).open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def test_full_instructions_cycle_survives_reopen_backup_and_restore(self):
        # r1: immutable program revision 1.
        revision1 = planner.create_program(
            self.root,
            direction="БДР",
            kind="Періодичний (повторний)",
            title="Сезонна програма БДР",
            program_text=(
                "Редакція 1. Зимовий період.\n"
                "1. Безпечна швидкість.\n"
                "2. Дистанція."
            ),
            source_note="Локальна програма підприємства",
            approved_by="Керівник підприємства",
            valid_from="2027-01-01",
        )

        # r2/r3: regular plan + exact prepared DOCX from revision 1.
        planned, planned_link, planned_docx = (
            prepared_output.ensure_planned_and_prepare(
                self.root,
                program_id=revision1.program_id,
                program_revision=revision1.revision,
                scheduled_for="2027-01-15",
                participants=self.people,
            )
        )
        self.assertEqual(planned.mode, planner.MODE_PLANNED)
        self.assertEqual(planned.status, planner.STATUS_PREPARED)
        self.assertEqual(planned.program_revision, 1)
        self.assertFalse(planned.conducted_on)
        planned_hash = self._sha256(planned_docx)
        self.assertEqual(planned_hash, planned_link.content_sha256)

        # New program revision must not rewrite the regular planned session.
        revision2 = planner.revise_program(
            self.root,
            revision1.program_id,
            program_text=(
                "Редакція 2. Весняний період.\n"
                "1. Зміна сезонних ризиків.\n"
                "2. Дії при небезпечній події."
            ),
            valid_from="2027-02-01",
            source_note="Оновлена локальна програма підприємства",
        )
        self.assertEqual(revision2.revision, 2)
        self.assertEqual(
            planner.program_for_session(self.root, planned).revision,
            1,
        )
        self.assertIn(
            "Зимовий період",
            planner.program_for_session(self.root, planned).program_text,
        )

        # Explicit reopen: all current facts are read again from disk stores.
        reopened_state = planner.read_state(self.root)
        reopened_links = prepared_output.read_links(self.root)
        self.assertEqual(len(reopened_state.programs), 2)
        self.assertEqual(len(reopened_state.sessions), 1)
        self.assertEqual(len(reopened_links), 1)
        reopened_plan = planner.get_session(self.root, planned.session_id)
        self.assertEqual(reopened_plan.status, planner.STATUS_PREPARED)
        self.assertEqual(
            self._sha256(
                prepared_output.resolve_output(
                    self.root,
                    prepared_output.get_link(
                        self.root, reopened_plan.session_id
                    ),
                )
            ),
            planned_hash,
        )

        # r4: event uses exact revision 2 and is independent of regular plan.
        event = event_ui.create_event(
            self.root,
            program_id=revision2.program_id,
            program_revision=revision2.revision,
            scheduled_for="2027-02-10",
            reason="Небезпечна подія на маршруті",
            participants=(self.people[1],),
        )
        event_prepared, event_link, event_docx = (
            prepared_output.prepare_session_document(
                self.root, event.session_id
            )
        )
        self.assertEqual(event_prepared.status, planner.STATUS_PREPARED)
        self.assertFalse(event_prepared.conducted_on)
        event_hash = self._sha256(event_docx)
        self.assertEqual(event_hash, event_link.content_sha256)

        conducted = event_ui.record_conducted(
            self.root,
            event.session_id,
            conducted_on="2027-02-10",
            evidence_note=(
                "Паперовий журнал БДР, запис 10.02.2027, стор. 40"
            ),
        )
        self.assertEqual(conducted.status, planner.STATUS_CONDUCTED)
        self.assertEqual(conducted.program_revision, 2)
        self.assertEqual(
            planner.get_session(self.root, planned.session_id).status,
            planner.STATUS_PREPARED,
        )

        # Quarter view: regular plan becomes derived overdue, event is conducted.
        rows = quarter_view.rows_for_quarter(
            self.root,
            2027,
            1,
            direction="БДР",
            as_of=date(2027, 2, 20),
        )
        by_id = {row.session_id: row for row in rows}
        self.assertEqual(by_id[planned.session_id].status, "overdue")
        self.assertEqual(
            by_id[event.session_id].status,
            planner.STATUS_CONDUCTED,
        )
        self.assertEqual(
            quarter_view.get_exact_program(
                self.root, by_id[planned.session_id]
            ).revision,
            1,
        )
        self.assertEqual(
            quarter_view.get_exact_program(
                self.root, by_id[event.session_id]
            ).revision,
            2,
        )

        # Capture complete persistent state before backup.
        state_before = planner.read_state(self.root)
        links_before = prepared_output.read_links(self.root)
        docs_before = tuple(document_store.list_documents(self.root))
        hashes_before = {
            row.session_id: self._sha256(
                prepared_output.resolve_output(self.root, row)
            )
            for row in links_before
        }
        self.assertEqual(len(state_before.sessions), 2)
        self.assertEqual(len(links_before), 2)
        self.assertEqual(len(docs_before), 2)

        # Full workspace backup/restore to a different clean root.
        archive = workspace.create_workspace_backup_archive(
            self.root,
            Path(self.temp.name) / "instructions-r5-full.zip",
            app_version="10.25-r5",
        )
        manifest = workspace.validate_workspace_backup_archive(archive)
        self.assertEqual(manifest["application"], "Taxo")
        self.assertEqual(manifest["app_version"], "10.25-r5-prep")
        self.assertGreaterEqual(int(manifest["format"]), 1)

        restored = Path(self.temp.name) / "restored"
        workspace.restore_workspace_backup_archive(archive, restored)

        state_after = planner.read_state(restored)
        links_after = prepared_output.read_links(restored)
        docs_after = tuple(document_store.list_documents(restored))
        self.assertEqual(state_after, state_before)
        self.assertEqual(links_after, links_before)
        self.assertEqual(docs_after, docs_before)

        for link in links_after:
            restored_path = prepared_output.resolve_output(restored, link)
            self.assertEqual(
                self._sha256(restored_path),
                hashes_before[link.session_id],
            )

        restored_plan = planner.get_session(
            restored, planned.session_id
        )
        restored_event = planner.get_session(
            restored, event.session_id
        )
        self.assertEqual(restored_plan.status, planner.STATUS_PREPARED)
        self.assertFalse(restored_plan.conducted_on)
        self.assertEqual(
            planner.status_at(restored_plan, date(2027, 2, 20)),
            "overdue",
        )
        self.assertEqual(
            restored_event.status, planner.STATUS_CONDUCTED
        )
        self.assertEqual(
            restored_event.evidence_note,
            "Паперовий журнал БДР, запис 10.02.2027, стор. 40",
        )
        self.assertEqual(
            planner.program_for_session(restored, restored_plan).revision,
            1,
        )
        self.assertEqual(
            planner.program_for_session(restored, restored_event).revision,
            2,
        )

        # Idempotency survives restore: same regular plan does not create
        # another session or another DOCX.
        again, again_link, again_path = (
            prepared_output.ensure_planned_and_prepare(
                restored,
                program_id=revision1.program_id,
                program_revision=revision1.revision,
                scheduled_for="2027-01-15",
                participants=reversed(self.people),
            )
        )
        self.assertEqual(again.session_id, planned.session_id)
        self.assertEqual(again_link, planned_link)
        self.assertEqual(self._sha256(again_path), planned_hash)
        self.assertEqual(len(planner.list_sessions(restored)), 2)
        self.assertEqual(
            len(document_store.list_documents(restored)), 2
        )

    def test_controlled_facts_never_follow_from_file_or_print_state(self):
        program = planner.create_program(
            self.root,
            direction="Охорона праці",
            kind="Повторний",
            title="Контроль чесного стану",
            program_text="Synthetic control.",
            valid_from="2027-01-01",
        )
        planned, link, path = prepared_output.ensure_planned_and_prepare(
            self.root,
            program_id=program.program_id,
            program_revision=1,
            scheduled_for="2027-03-01",
            participants=(self.people[0],),
        )
        self.assertTrue(path.is_file())
        self.assertIsNotNone(link)
        self.assertEqual(planned.status, planner.STATUS_PREPARED)
        self.assertFalse(planned.conducted_on)
        self.assertFalse(planned.evidence_note)

        record = next(
            row for row in document_store.list_documents(self.root)
            if row["id"] == link.document_id
        )
        # The generated/prepared document is not a paper-signature fact.
        self.assertFalse(record["paper_signed"])

        with self.assertRaisesRegex(ValueError, "паперового запису"):
            planner.mark_conducted(
                self.root,
                planned.session_id,
                conducted_on="2027-03-01",
                evidence_note="",
            )
        saved = planner.get_session(self.root, planned.session_id)
        self.assertEqual(saved.status, planner.STATUS_PREPARED)
        self.assertFalse(saved.conducted_on)


if __name__ == "__main__":
    unittest.main()
