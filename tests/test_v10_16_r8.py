# -*- coding: utf-8 -*-
"""10.16-r8: order-editor assignment controls have a dedicated module."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import main
import order_editor_assignments_ui
import order_editor_ui

ROOT = Path(__file__).resolve().parents[1]


class OrderEditorAssignmentsR8Tests(unittest.TestCase):
    def test_version_and_start_require_assignment_module(self):
        self.assertIn(main.APP_VERSION, ("10.16-r8", "10.16-r9", "10.16-r10", "10.17-r1", "10.17-r2", "10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text(encoding="utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        start = (ROOT / "START.bat").read_text(encoding="utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("order_editor_assignments_ui.py", start)

    def test_order_editor_delegates_assignment_controls(self):
        source = inspect.getsource(order_editor_ui.open_order_editor)
        self.assertIn(
            "order_editor_assignments_ui.install_order_editor_assignments(",
            source,
        )
        self.assertIn(
            "assignment_section.initial_pairs_for_save(order_type)",
            source,
        )
        self.assertNotIn("core.tk.Listbox(", source)
        self.assertNotIn("ops.build_assignment_pairs(", source)

    def _section_without_tk(self):
        section = order_editor_assignments_ui.OrderEditorAssignmentSection.__new__(
            order_editor_assignments_ui.OrderEditorAssignmentSection
        )
        section.core = SimpleNamespace(
            messagebox=SimpleNamespace(
                askyesno=mock.Mock(return_value=True),
                showerror=mock.Mock(),
            )
        )
        section.ops = SimpleNamespace(
            TYPE_VEHICLE_ASSIGNMENT="vehicle_assignment",
            build_assignment_pairs=mock.Mock(
                return_value=[(10, 1), (10, 2)]
            ),
        )
        section.dialog = object()
        section.existing = None
        section.box = object()
        section.initial_vehicles = [{"id": 10}]
        section.initial_drivers = [{"id": 1}, {"id": 2}]
        section.initial_vehicle_list = mock.Mock()
        section.initial_driver_list = mock.Mock()
        section.initial_vehicle_list.curselection.return_value = (0,)
        section.initial_driver_list.curselection.return_value = (0, 1)
        section.staged_initial_pairs = []
        section.assignment_count_var = mock.Mock()
        section._render_staged_pairs = mock.Mock()
        return section

    def test_selected_pairs_are_staged_and_survive_focus_loss(self):
        section = self._section_without_tk()

        first = section.initial_pairs_for_save("vehicle_assignment")
        self.assertEqual(first, [(10, 1), (10, 2)])
        section.ops.build_assignment_pairs.assert_called_once_with(
            [10],
            [1, 2],
        )

        section.initial_vehicle_list.curselection.return_value = ()
        section.initial_driver_list.curselection.return_value = ()
        second = section.initial_pairs_for_save("vehicle_assignment")

        self.assertEqual(second, [(10, 1), (10, 2)])
        self.assertEqual(section.staged_initial_pairs, [(10, 1), (10, 2)])
        section.core.messagebox.askyesno.assert_not_called()

    def test_empty_assignment_order_still_requires_confirmation(self):
        section = self._section_without_tk()
        section.initial_vehicle_list.curselection.return_value = ()
        section.initial_driver_list.curselection.return_value = ()
        section.core.messagebox.askyesno.return_value = False

        self.assertIsNone(
            section.initial_pairs_for_save("vehicle_assignment")
        )
        section.core.messagebox.askyesno.assert_called_once()


if __name__ == "__main__":
    unittest.main()
