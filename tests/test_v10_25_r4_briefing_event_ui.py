# -*- coding: utf-8 -*-
"""10.25-r5 prep: event briefing + explicit conducted fact."""
from __future__ import annotations

import sqlite3
import tempfile
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
import unittest

import briefing_event_ui as event_ui
import briefing_planner as planner
import briefing_prepared_output as prepared_output
import safety_instructions_ui as brief
import workspace
from runtime_reachability import (
    runtime_routes, assert_widget_reachable, activate_widget,
)


class BriefingEventR4PrepTests(unittest.TestCase):
    def test_candidate_identity_and_package_guard(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.25-r5\n")
        self.assertIn('APP_VERSION = "10.25-r5"', (root / "main.py").read_text("utf-8"))
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn("Taxo 10.25-r5 - START", start)
        self.assertIn("briefing_event_ui.py", start)
        self.assertEqual((root / ".release" / "full-current").read_text("utf-8"), "10.25-r5\n")
        self.assertEqual((root / ".release" / "stable-current").read_text("utf-8"), "10.24-r9\n")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="taxo_1025_r4_")
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
        self.program = planner.create_program(
            self.root,
            direction="БДР",
            kind="Позаплановий (спеціальний)",
            title="Подієва програма БДР",
            program_text="1. Розбір фактичної події.\n2. Запобіжні дії.",
            source_note="Локальна програма підприємства",
            approved_by="Керівник",
            valid_from="2026-11-01",
        )
        self.people = (
            {
                "id": 61,
                "name": "Водій Один",
                "personnel_no": "061",
                "position": "Водій",
            },
            {
                "id": 62,
                "name": "Водій Два",
                "personnel_no": "062",
                "position": "Водій",
            },
        )

    def test_event_reason_is_required_and_does_not_close_regular_plan(self):
        planned = planner.create_planned_session(
            self.root,
            planning_key="BDR:regular:2026-Q4",
            program_id=self.program.program_id,
            program_revision=self.program.revision,
            scheduled_for="2026-12-15",
            participants=self.people,
        )
        with self.assertRaisesRegex(ValueError, "[Пп]ідстава"):
            event_ui.create_event(
                self.root,
                program_id=self.program.program_id,
                program_revision=self.program.revision,
                scheduled_for="2026-11-27",
                reason="",
                participants=(self.people[0],),
            )

        event = event_ui.create_event(
            self.root,
            program_id=self.program.program_id,
            program_revision=self.program.revision,
            scheduled_for="2026-11-27",
            reason="Небезпечна подія на маршруті",
            participants=(self.people[0],),
        )
        self.assertEqual(event.mode, planner.MODE_EVENT)
        self.assertEqual(event.status, planner.STATUS_PLANNED)
        self.assertEqual(
            planner.get_session(self.root, planned.session_id).status,
            planner.STATUS_PLANNED,
        )

        prepared, link, path = prepared_output.prepare_session_document(
            self.root, event.session_id
        )
        self.assertEqual(prepared.status, planner.STATUS_PREPARED)
        self.assertTrue(path.is_file())
        self.assertIsNotNone(link)
        self.assertFalse(prepared.conducted_on)

        conducted = event_ui.record_conducted(
            self.root,
            event.session_id,
            conducted_on="2026-11-27",
            evidence_note="Паперовий журнал БДР, запис 27.11.2026, стор. 18",
        )
        self.assertEqual(conducted.status, planner.STATUS_CONDUCTED)
        self.assertEqual(conducted.prepared_at, prepared.prepared_at)
        self.assertEqual(
            planner.get_session(self.root, planned.session_id).status,
            planner.STATUS_PLANNED,
        )

        same = event_ui.record_conducted(
            self.root,
            event.session_id,
            conducted_on="2026-11-27",
            evidence_note="Паперовий журнал БДР, запис 27.11.2026, стор. 18",
        )
        self.assertEqual(same, conducted)
        with self.assertRaisesRegex(ValueError, "історію не переписувати"):
            event_ui.record_conducted(
                self.root,
                event.session_id,
                conducted_on="2026-11-28",
                evidence_note="Інший запис",
            )

    def test_event_conducted_fact_and_output_survive_full_backup_restore(self):
        event = event_ui.create_event(
            self.root,
            program_id=self.program.program_id,
            program_revision=self.program.revision,
            scheduled_for="2026-11-26",
            reason="Зміна умов руху після аварійної ситуації",
            participants=self.people,
        )
        prepared, link, _path = prepared_output.prepare_session_document(
            self.root, event.session_id
        )
        conducted = event_ui.record_conducted(
            self.root,
            prepared.session_id,
            conducted_on="2026-11-26",
            evidence_note="Паперовий журнал, стор. 21",
        )
        audit_before = event_ui.session_audit(
            self.root, conducted.session_id
        )

        archive = workspace.create_workspace_backup_archive(
            self.root,
            Path(self.temp.name) / "r4-backup.zip",
            app_version="10.25-r5",
        )
        restored = Path(self.temp.name) / "restored"
        workspace.restore_workspace_backup_archive(archive, restored)
        audit_after = event_ui.session_audit(
            restored, conducted.session_id
        )

        self.assertEqual(audit_after["session"], audit_before["session"])
        self.assertEqual(audit_after["program"], audit_before["program"])
        self.assertEqual(audit_after["prepared_output"], link)
        restored_path = prepared_output.resolve_output(
            restored, audit_after["prepared_output"]
        )
        self.assertTrue(restored_path.is_file())
        self.assertEqual(
            audit_after["session"].evidence_note,
            "Паперовий журнал, стор. 21",
        )


class _DummyCon:
    def close(self):
        pass


class BriefingEventLiveR4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="taxo_1025_r4_ui_")
        self.workspace = Path(self.temp.name) / "workspace"
        workspace.ensure_workspace(self.workspace)
        self.program = planner.create_program(
            self.workspace,
            direction="БДР",
            kind="Позаплановий (спеціальний)",
            title="Подієва програма",
            program_text="Текст подієвої програми.",
            source_note="Локальна програма",
            valid_from="2026-11-01",
        )
        self.employee_rows = [
            {
                "id": 71,
                "label": "Тест Водій · таб. № 071 — Водій",
                "name": "Тест Водій",
                "position": "Водій",
                "personnel_no": "071",
                "search_text": "тест водій 071 71",
            },
        ]
        self.root = tk.Tk()
        self.root.geometry("780x560")
        self.book = ttk.Notebook(self.root)
        self.book.pack(fill="both", expand=True)

        def fit(win, width, height, min_width, min_height):
            win.geometry(
                "%dx%d" % (
                    min(int(width), 900),
                    min(int(height), 600),
                )
            )
            win.minsize(int(min_width), int(min_height))

        self.errors = []
        self.core = SimpleNamespace(
            tk=tk,
            ttk=ttk,
            db=lambda: _DummyCon(),
            fit_window_to_screen=fit,
            configure_toplevel=lambda win, **kwargs: (
                win.minsize(*kwargs["minsize"])
                if kwargs.get("minsize") else None
            ),
            messagebox=SimpleNamespace(
                showinfo=lambda *a, **k: None,
                showerror=lambda *a, **k: self.errors.append(a),
                showwarning=lambda *a, **k: None,
            ),
        )

    def tearDown(self):
        try:
            self.root.destroy()
        finally:
            self.temp.cleanup()

    @runtime_routes(
        "operations.instructions_event",
        "operations.instructions_event_create",
        "operations.instructions_conducted",
        "operations.instructions_session_history",
    )
    def test_event_create_conducted_and_history_are_live_and_reachable(self):
        with mock.patch.object(
            event_ui.entity_choices,
            "list_employee_choices",
            return_value=self.employee_rows,
        ), mock.patch.object(
            event_ui,
            "load_workspace_root",
            return_value=self.workspace,
        ), mock.patch.object(
            brief,
            "load_workspace_root",
            return_value=self.workspace,
        ):
            tab = brief.install_instruction_tab(
                SimpleNamespace(), self.core, self.book
            )
            self.book.select(tab)
            self.root.update()

            event_button = tab._taxo_briefing_event_button
            assert_widget_reachable(
                event_button, "operations.instructions_event"
            )
            activate_widget(
                event_button, "operations.instructions_event"
            )
            self.root.update()

            dialog = tab._taxo_briefing_event_window
            dialog._taxo_event_reason_var.set(
                "Небезпечна подія на маршруті"
            )
            available = dialog._taxo_event_available_people
            available.selection_set(0)
            dialog._taxo_event_add_people_button.invoke()
            self.root.update()
            create_button = dialog._taxo_event_create_button
            assert_widget_reachable(
                create_button, "operations.instructions_event_create"
            )
            activate_widget(
                create_button, "operations.instructions_event_create"
            )
            self.root.update()
            self.assertEqual(self.errors, [])

            sessions = planner.list_sessions(self.workspace)
            self.assertEqual(len(sessions), 1)
            event = sessions[0]
            self.assertEqual(event.mode, planner.MODE_EVENT)
            self.assertEqual(
                event.reason, "Небезпечна подія на маршруті"
            )

            tab._taxo_briefing_quarter_button.invoke()
            self.root.update()
            quarter = tab._taxo_briefing_quarter_window
            tree = quarter._taxo_briefing_quarter_tree
            self.assertEqual(len(tree.get_children()), 1)
            tree.selection_set(tree.get_children()[0])
            tree.focus(tree.get_children()[0])

            history_button = quarter._taxo_briefing_history_button
            assert_widget_reachable(
                history_button,
                "operations.instructions_session_history",
            )
            activate_widget(
                history_button,
                "operations.instructions_session_history",
            )
            self.root.update()
            history = quarter._taxo_briefing_history_window
            text = history._taxo_session_history_text.get("1.0", "end")
            self.assertIn("Небезпечна подія на маршруті", text)
            self.assertIn("За подією", text)
            history.destroy()
            self.root.update()

            quarter._taxo_briefing_conducted_button.invoke()
            self.root.update()
            fact = quarter._taxo_briefing_conducted_dialog
            fact._taxo_conducted_evidence.insert(
                "1.0", "Паперовий журнал БДР, стор. 33"
            )
            save = fact._taxo_conducted_save_button
            assert_widget_reachable(
                save, "operations.instructions_conducted"
            )
            activate_widget(
                save, "operations.instructions_conducted"
            )
            self.root.update()
            self.assertEqual(self.errors, [])

        saved = planner.get_session(self.workspace, event.session_id)
        self.assertEqual(saved.status, planner.STATUS_CONDUCTED)
        self.assertEqual(
            saved.evidence_note, "Паперовий журнал БДР, стор. 33"
        )


if __name__ == "__main__":
    unittest.main()
