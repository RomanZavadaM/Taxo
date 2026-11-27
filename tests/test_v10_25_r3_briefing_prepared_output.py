# -*- coding: utf-8 -*-
"""10.25-r3 prep: planned briefing -> exact PaperDocuments DOCX link."""
from __future__ import annotations

import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

import briefing_planner as planner
import briefing_prepared_output as prepared_output
import paper_document_store as document_store
import workspace


class BriefingPreparedOutputR3PrepTests(unittest.TestCase):
    def test_candidate_identity_and_package_guard(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.25-r3\n",
        )
        self.assertIn(
            'APP_VERSION = "10.25-r3"',
            (root / "main.py").read_text("utf-8"),
        )
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn("Taxo 10.25-r3 - START", start)
        self.assertIn("briefing_prepared_output.py", start)
        self.assertIn("briefing_planning_ui.py", start)
        self.assertEqual(
            (root / ".release" / "full-current").read_text("utf-8"),
            "10.25-r3\n",
        )
        self.assertEqual(
            (root / ".release" / "stable-current").read_text("utf-8"),
            "10.24-r9\n",
        )

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="taxo_1025_r3_")
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
                "id": 41,
                "name": "Іваненко Іван",
                "personnel_no": "041",
                "position": "Водій",
            },
            {
                "id": 42,
                "name": "Петренко Петро",
                "personnel_no": "042",
                "position": "Водій",
            },
        )

    def _program(self):
        return planner.create_program(
            self.root,
            direction="БДР",
            kind="Періодичний (повторний)",
            title="Квартальна програма БДР",
            program_text=(
                "1. Безпечна швидкість.\n"
                "2. Дистанція.\n"
                "3. Дії при небезпечній події."
            ),
            source_note="Локальна програма підприємства",
            approved_by="Керівник підприємства",
            valid_from="2027-01-01",
        )

    def test_planned_session_gets_one_verified_docx_and_only_prepared_state(self):
        program = self._program()
        session, link, path = prepared_output.ensure_planned_and_prepare(
            self.root,
            program_id=program.program_id,
            program_revision=program.revision,
            scheduled_for="2027-02-15",
            participants=self.people(),
        )
        self.assertEqual(session.status, planner.STATUS_PREPARED)
        self.assertFalse(session.conducted_on)
        self.assertFalse(session.evidence_note)
        self.assertTrue(path.is_file())
        self.assertEqual(path.name, link.filename)
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            link.content_sha256,
        )

        records = document_store.list_documents(self.root)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], link.document_id)
        self.assertEqual(records[0]["file"], link.filename)
        self.assertFalse(records[0]["paper_signed"])

        same_session, same_link, same_path = (
            prepared_output.ensure_planned_and_prepare(
                self.root,
                program_id=program.program_id,
                program_revision=program.revision,
                scheduled_for="2027-02-15",
                participants=reversed(self.people()),
            )
        )
        # Selection order is not a new business event: key uses sorted IDs.
        self.assertEqual(same_session.session_id, session.session_id)
        self.assertEqual(same_link, link)
        self.assertEqual(same_path, path)
        self.assertEqual(len(document_store.list_documents(self.root)), 1)
        self.assertEqual(len(prepared_output.read_links(self.root)), 1)

    def test_full_backup_restore_preserves_plan_output_link_and_file_hash(self):
        program = self._program()
        session, link, path = prepared_output.ensure_planned_and_prepare(
            self.root,
            program_id=program.program_id,
            program_revision=program.revision,
            scheduled_for="2027-03-05",
            participants=self.people(),
        )
        before_hash = hashlib.sha256(path.read_bytes()).hexdigest()

        archive = workspace.create_workspace_backup_archive(
            self.root,
            Path(self.temp.name) / "briefing-r3-backup.zip",
            app_version="10.25-r3",
        )
        restored = Path(self.temp.name) / "restored"
        workspace.restore_workspace_backup_archive(archive, restored)

        restored_session = planner.get_session(
            restored, session.session_id
        )
        self.assertEqual(restored_session.status, planner.STATUS_PREPARED)
        restored_link = prepared_output.get_link(
            restored, session.session_id
        )
        self.assertEqual(restored_link, link)
        restored_path = prepared_output.resolve_output(
            restored, restored_link
        )
        self.assertEqual(
            hashlib.sha256(restored_path.read_bytes()).hexdigest(),
            before_hash,
        )
        self.assertEqual(
            planner.program_for_session(
                restored, restored_session
            ).program_text,
            program.program_text,
        )

    def test_tampered_docx_fails_closed_and_conducted_session_is_not_prepared(self):
        program = self._program()
        session, link, path = prepared_output.ensure_planned_and_prepare(
            self.root,
            program_id=program.program_id,
            program_revision=program.revision,
            scheduled_for="2027-03-10",
            participants=(self.people()[0],),
        )
        path.write_bytes(path.read_bytes() + b"tamper")
        with self.assertRaisesRegex(ValueError, "змінений або пошкоджений"):
            prepared_output.resolve_output(self.root, link)

        second = planner.create_planned_session(
            self.root,
            planning_key="BDR:conducted:2027-03-11",
            program_id=program.program_id,
            program_revision=program.revision,
            scheduled_for="2027-03-11",
            participants=(self.people()[1],),
        )
        planner.mark_conducted(
            self.root,
            second.session_id,
            conducted_on="2027-03-11",
            evidence_note="Паперовий журнал БДР, стор. 22",
        )
        with self.assertRaisesRegex(ValueError, "Проведений"):
            prepared_output.prepare_session_document(
                self.root, second.session_id
            )


if __name__ == "__main__":
    unittest.main()
