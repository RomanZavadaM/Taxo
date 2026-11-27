# -*- coding: utf-8 -*-
"""10.25-r4 prep: quarter briefing view over the r1 planning store."""
from __future__ import annotations

import tempfile
import tkinter as tk
from tkinter import ttk
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
import unittest

import briefing_planner as planner
import briefing_quarter_view as quarter_view
import safety_instructions_ui as brief
import workspace
from runtime_reachability import (
    runtime_routes, assert_widget_reachable, activate_widget,
)


class BriefingQuarterViewR2PrepTests(unittest.TestCase):
    def test_candidate_identity_and_package_guard(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.25-r4\n")
        self.assertIn('APP_VERSION = "10.25-r4"', (root / "main.py").read_text("utf-8"))
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn("Taxo 10.25-r4 - START", start)
        self.assertIn("briefing_quarter_view.py", start)
        self.assertEqual((root / ".release" / "full-current").read_text("utf-8"), "10.25-r4\n")
        self.assertEqual((root / ".release" / "stable-current").read_text("utf-8"), "10.24-r9\n")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="taxo_1025_r2_")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        workspace.ensure_workspace(self.root)

    @staticmethod
    def people():
        return (
            {
                "id": 21,
                "name": "Водій Один",
                "personnel_no": "021",
                "position": "Водій",
            },
            {
                "id": 22,
                "name": "Водій Два",
                "personnel_no": "022",
                "position": "Водій",
            },
        )

    def _programs(self):
        bdr1 = planner.create_program(
            self.root,
            direction="БДР",
            kind="Періодичний (повторний)",
            title="Сезонна БДР",
            program_text="Редакція 1.",
            valid_from="2027-01-01",
        )
        bdr2 = planner.revise_program(
            self.root,
            bdr1.program_id,
            program_text="Редакція 2.",
            valid_from="2027-03-01",
        )
        osh = planner.create_program(
            self.root,
            direction="Охорона праці",
            kind="Повторний",
            title="Повторний ОП",
            program_text="Програма ОП.",
            valid_from="2027-01-01",
        )
        return bdr1, bdr2, osh

    def test_quarter_filter_status_and_exact_program_revision(self):
        bdr1, bdr2, osh = self._programs()
        planned = planner.create_planned_session(
            self.root,
            planning_key="BDR:Q1:drivers",
            program_id=bdr1.program_id,
            program_revision=1,
            scheduled_for="2027-01-15",
            participants=self.people(),
        )
        event = planner.create_event_session(
            self.root,
            program_id=bdr2.program_id,
            program_revision=2,
            scheduled_for="2027-02-10",
            reason="Зміна локальної інструкції",
            participants=(self.people()[0],),
        )
        planner.mark_conducted(
            self.root,
            event.session_id,
            conducted_on="2027-02-10",
            evidence_note="Паперовий журнал БДР, стор. 7",
        )
        op = planner.create_planned_session(
            self.root,
            planning_key="OP:Q1:drivers",
            program_id=osh.program_id,
            program_revision=1,
            scheduled_for="2027-03-20",
            participants=(self.people()[1],),
        )
        planner.mark_prepared(self.root, op.session_id)
        planner.create_planned_session(
            self.root,
            planning_key="BDR:Q2:drivers",
            program_id=bdr2.program_id,
            program_revision=2,
            scheduled_for="2027-04-15",
            participants=self.people(),
        )

        rows = quarter_view.rows_for_quarter(
            self.root, 2027, 1, as_of=date(2027, 3, 10)
        )
        self.assertEqual(len(rows), 3)
        by_id = {row.session_id: row for row in rows}
        self.assertEqual(by_id[planned.session_id].status, "overdue")
        self.assertEqual(
            by_id[event.session_id].status, planner.STATUS_CONDUCTED
        )
        self.assertEqual(by_id[op.session_id].status, planner.STATUS_PREPARED)

        bdr_rows = quarter_view.rows_for_quarter(
            self.root,
            2027,
            1,
            direction="БДР",
            as_of=date(2027, 3, 10),
        )
        self.assertEqual(
            [row.session_id for row in bdr_rows],
            [planned.session_id, event.session_id],
        )
        first_program = quarter_view.get_exact_program(
            self.root, bdr_rows[0]
        )
        self.assertEqual(first_program.revision, 1)
        self.assertEqual(first_program.program_text, "Редакція 1.")
        self.assertEqual(
            quarter_view.quarter_bounds(2027, 1),
            (date(2027, 1, 1), date(2027, 4, 1)),
        )

    def test_idempotent_explicit_plan_generation_never_rewrites_conflict(self):
        bdr1, _bdr2, _osh = self._programs()
        first = quarter_view.ensure_planned_session(
            self.root,
            planning_key="BDR:Q1:explicit",
            program_id=bdr1.program_id,
            program_revision=1,
            scheduled_for="2027-01-18",
            participants=self.people(),
        )
        second = quarter_view.ensure_planned_session(
            self.root,
            planning_key="bdr:q1:EXPLICIT",
            program_id=bdr1.program_id,
            program_revision=1,
            scheduled_for="2027-01-18",
            participants=self.people(),
        )
        self.assertEqual(second.session_id, first.session_id)
        self.assertEqual(
            len(planner.list_sessions(self.root, mode=planner.MODE_PLANNED)),
            1,
        )
        with self.assertRaisesRegex(ValueError, "не переписано"):
            quarter_view.ensure_planned_session(
                self.root,
                planning_key="BDR:Q1:explicit",
                program_id=bdr1.program_id,
                program_revision=1,
                scheduled_for="2027-01-19",
                participants=self.people(),
            )
        saved = planner.get_session(self.root, first.session_id)
        self.assertEqual(saved.scheduled_for, "2027-01-18")
        self.assertEqual(len(planner.list_sessions(self.root)), 1)


class _DummyCon:
    def close(self):
        pass


class BriefingQuarterViewLiveR2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="taxo_1025_r2_ui_")
        self.workspace = Path(self.temp.name) / "workspace"
        workspace.ensure_workspace(self.workspace)
        program = planner.create_program(
            self.workspace,
            direction="БДР",
            kind="Періодичний (повторний)",
            title="Квартальна програма",
            program_text="Точний текст редакції 1.",
            valid_from="2026-10-01",
        )
        planner.create_planned_session(
            self.workspace,
            planning_key="BDR:2026-Q4:UI",
            program_id=program.program_id,
            program_revision=1,
            scheduled_for="2026-11-27",
            participants=(
                {
                    "id": 31,
                    "name": "Тест Водій",
                    "personnel_no": "031",
                    "position": "Водій",
                },
            ),
        )

        self.root = tk.Tk()
        self.root.geometry("780x540")
        self.book = ttk.Notebook(self.root)
        self.book.pack(fill="both", expand=True)

        def fit(win, width, height, min_width, min_height):
            win.geometry("%dx%d" % (min(int(width), 980), min(int(height), 620)))
            win.minsize(int(min_width), int(min_height))

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
                showerror=lambda *a, **k: self.fail(
                    "Unexpected UI error: %r" % (a,)
                ),
                showwarning=lambda *a, **k: None,
            ),
        )

    def tearDown(self):
        try:
            self.root.destroy()
        finally:
            self.temp.cleanup()

    @runtime_routes("operations.instructions_quarter")
    def test_quarter_button_is_reachable_in_small_window_and_opens_live_view(self):
        with mock.patch.object(
            brief, "load_workspace_root", return_value=self.workspace
        ), mock.patch.object(
            brief.ops, "list_employee_choices", return_value=[]
        ), mock.patch.object(
            brief, "quarter_for", return_value=(2026, 4)
        ):
            tab = brief.install_instruction_tab(
                SimpleNamespace(), self.core, self.book
            )
            self.book.select(tab)
            self.root.update()
            button = tab._taxo_briefing_quarter_button
            assert_widget_reachable(
                button, "operations.instructions_quarter"
            )
            activate_widget(
                button, "operations.instructions_quarter"
            )
            self.root.update()

            quarter_window = tab._taxo_briefing_quarter_window
            self.assertTrue(quarter_window.winfo_exists())
            tree = quarter_window._taxo_briefing_quarter_tree
            self.assertEqual(len(tree.get_children()), 1)
            values = tree.item(tree.get_children()[0], "values")
            self.assertIn("Квартальна програма (r1)", values)
            self.assertIn("Заплановано", values)

            direction = quarter_window._taxo_briefing_quarter_filter
            direction.set("Охорона праці")
            direction.event_generate("<<ComboboxSelected>>")
            self.root.update()
            self.assertEqual(len(tree.get_children()), 0)

            direction.set("БДР")
            direction.event_generate("<<ComboboxSelected>>")
            self.root.update()
            self.assertEqual(len(tree.get_children()), 1)
            program_button = quarter_window._taxo_briefing_quarter_program_button
            self.assertEqual(str(program_button.cget("state")), "normal")
            program_button.invoke()
            self.root.update()
            # Exact session -> program revision resolution is asserted above.
            # Tk does not expose nested Toplevels consistently through
            # winfo_children(), so successful invocation is the UI contract here.


if __name__ == "__main__":
    unittest.main()
