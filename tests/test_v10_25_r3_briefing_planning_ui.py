# -*- coding: utf-8 -*-
"""10.25-r3 prep: cumulative selection and live planned-print workflow."""
from __future__ import annotations

import tempfile
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
import unittest

import briefing_planner as planner
import briefing_planning_ui as planning_ui
import briefing_prepared_output as prepared_output
import paper_document_store as document_store
import safety_instructions_ui as brief
import workspace
from runtime_reachability import (
    runtime_routes, assert_widget_reachable, activate_widget,
)


class EmployeeSelectionModelR3Tests(unittest.TestCase):
    def test_search_accumulates_identity_selection(self):
        rows = [
            {
                "id": 1,
                "name": "Іваненко Іван",
                "position": "Водій",
                "personnel_no": "001",
                "label": "Іваненко Іван · таб. № 001 — Водій",
                "search_text": "іваненко іван водій 001 1",
            },
            {
                "id": 2,
                "name": "Петренко Петро",
                "position": "Механік",
                "personnel_no": "002",
                "label": "Петренко Петро · таб. № 002 — Механік",
                "search_text": "петренко петро механік 002 2",
            },
        ]
        model = planning_ui.EmployeeSelectionModel(rows)
        first = model.search("іван")
        self.assertEqual([row["id"] for row in first], [1])
        model.add_ids([first[0]["id"]])

        second = model.search("петр")
        self.assertEqual([row["id"] for row in second], [2])
        model.add_ids([second[0]["id"]])

        self.assertEqual(model.selected_ids(), (1, 2))
        self.assertEqual(
            [row["name"] for row in model.selected_rows()],
            ["Іваненко Іван", "Петренко Петро"],
        )
        model.remove_ids([1])
        self.assertEqual(model.selected_ids(), (2,))
        self.assertEqual(
            [row["id"] for row in model.search("")], [1, 2]
        )


class _DummyCon:
    def close(self):
        pass


class BriefingPlanningLiveR3Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="taxo_1025_r3_ui_")
        self.workspace = Path(self.temp.name) / "workspace"
        workspace.ensure_workspace(self.workspace)
        self.program = planner.create_program(
            self.workspace,
            direction="БДР",
            kind="Періодичний (повторний)",
            title="Планова програма БДР",
            program_text="1. Швидкість.\n2. Дистанція.",
            source_note="Локальна програма",
            approved_by="Керівник",
            valid_from="2026-11-01",
        )
        self.employee_rows = [
            {
                "id": 51,
                "label": "Іваненко Іван · таб. № 051 — Водій",
                "name": "Іваненко Іван",
                "position": "Водій",
                "personnel_no": "051",
                "search_text": "іваненко іван водій 051 51",
            },
            {
                "id": 52,
                "label": "Петренко Петро · таб. № 052 — Водій",
                "name": "Петренко Петро",
                "position": "Водій",
                "personnel_no": "052",
                "search_text": "петренко петро водій 052 52",
            },
        ]

        self.root = tk.Tk()
        self.root.geometry("940x650")
        self.book = ttk.Notebook(self.root)
        self.book.pack(fill="both", expand=True)

        def fit(win, width, height, min_width, min_height):
            win.geometry(
                "%dx%d" % (
                    min(int(width), 900),
                    min(int(height), 590),
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
        "operations.instructions_planning",
        "operations.instructions_program_revision",
        "operations.instructions_prepare_planned",
    )
    def test_live_program_revision_and_planned_docx_actions_are_reachable(self):
        with mock.patch.object(
            brief.ops,
            "list_employee_choices",
            return_value=self.employee_rows,
        ), mock.patch.object(
            planning_ui.entity_choices,
            "list_employee_choices",
            return_value=self.employee_rows,
        ), mock.patch.object(
            planning_ui,
            "load_workspace_root",
            return_value=self.workspace,
        ), mock.patch.object(
            planning_ui.instruction_documents,
            "open_briefing_document",
        ):
            tab = brief.install_instruction_tab(
                SimpleNamespace(), self.core, self.book
            )
            self.book.select(tab)
            self.root.update()

            open_button = tab._taxo_briefing_planning_button
            assert_widget_reachable(
                open_button, "operations.instructions_planning"
            )
            activate_widget(
                open_button, "operations.instructions_planning"
            )
            self.root.update()

            dialog = tab._taxo_briefing_planning_window
            self.assertTrue(dialog.winfo_exists())
            self.assertTrue(dialog._taxo_briefing_program_rows)

            revise = dialog._taxo_briefing_revise_program_button
            assert_widget_reachable(
                revise,
                "operations.instructions_program_revision",
            )
            before_children = set(dialog.winfo_children())
            activate_widget(
                revise,
                "operations.instructions_program_revision",
            )
            self.root.update()
            editors = [
                child for child in dialog.winfo_children()
                if child not in before_children
                and isinstance(child, tk.Toplevel)
            ]
            self.assertTrue(editors)
            editors[-1].destroy()
            self.root.update()

            available = dialog._taxo_briefing_available_people
            available.selection_set(0)
            dialog._taxo_briefing_add_people_button.invoke()
            self.root.update()
            self.assertEqual(
                dialog._taxo_briefing_selection_model.selected_ids(),
                (51,),
            )

            search = dialog._taxo_briefing_search_entry
            search.delete(0, "end")
            search.insert(0, "петренко")
            self.root.update()
            available.selection_clear(0, "end")
            available.selection_set(0)
            dialog._taxo_briefing_add_people_button.invoke()
            self.root.update()
            self.assertEqual(
                dialog._taxo_briefing_selection_model.selected_ids(),
                (51, 52),
            )

            prepare = dialog._taxo_briefing_prepare_button
            assert_widget_reachable(
                prepare,
                "operations.instructions_prepare_planned",
            )
            activate_widget(
                prepare,
                "operations.instructions_prepare_planned",
            )
            self.root.update()
            self.assertEqual(self.errors, [])

        sessions = planner.list_sessions(self.workspace)
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].status, planner.STATUS_PREPARED)
        self.assertFalse(sessions[0].conducted_on)
        self.assertEqual(
            [p.employee_id for p in sessions[0].participants],
            [51, 52],
        )
        link = prepared_output.get_link(
            self.workspace, sessions[0].session_id
        )
        self.assertIsNotNone(link)
        path = prepared_output.resolve_output(self.workspace, link)
        self.assertTrue(path.is_file())
        records = document_store.list_documents(self.workspace)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], link.document_id)
        self.assertFalse(records[0]["paper_signed"])


if __name__ == "__main__":
    unittest.main()
