# -*- coding: utf-8 -*-
"""10.21-r8: driver/vehicle pairs must be explicit, never positional zip."""
import inspect
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import operations_orders as ops
import order_editor_assignments_ui


class AssignmentPairingR8Tests(unittest.TestCase):
    def test_current_identity_is_r8(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text(encoding="utf-8"),
            "Version: 10.25-r7\n",
        )
        self.assertIn(
            'APP_VERSION = "10.25-r7"',
            (root / "main.py").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "Taxo 10.25-r7",
            (root / "START.bat").read_text(encoding="utf-8"),
        )

    def test_core_rejects_positional_zip_for_multiple_vehicles(self):
        with self.assertRaisesRegex(ValueError, "Автоматичне парування"):
            ops.build_assignment_pairs([20, 10], [1, 2])

    def test_one_vehicle_many_drivers_remains_supported(self):
        self.assertEqual(
            ops.build_assignment_pairs([20], [2, 1]),
            [(20, 2), (20, 1)],
        )

    def test_editor_requires_one_vehicle_per_staging_action(self):
        section = order_editor_assignments_ui.OrderEditorAssignmentSection.__new__(
            order_editor_assignments_ui.OrderEditorAssignmentSection
        )
        section.core = SimpleNamespace(
            messagebox=SimpleNamespace(showerror=mock.Mock())
        )
        section.ops = SimpleNamespace(build_assignment_pairs=mock.Mock())
        section.dialog = object()
        section.initial_vehicles = [{"id": 10}, {"id": 20}]
        section.initial_drivers = [{"id": 1}, {"id": 2}]
        section.initial_vehicle_list = mock.Mock()
        section.initial_driver_list = mock.Mock()
        section.initial_vehicle_list.curselection.return_value = (0, 1)
        section.initial_driver_list.curselection.return_value = (0, 1)
        section.staged_initial_pairs = []
        section.assignment_count_var = mock.Mock()
        section._render_staged_pairs = mock.Mock()

        self.assertIsNone(section._stage_current_selection(show_error=True))
        section.ops.build_assignment_pairs.assert_not_called()
        section.core.messagebox.showerror.assert_called_once()

    def test_ui_text_explains_explicit_pairing(self):
        source = inspect.getsource(
            order_editor_assignments_ui.OrderEditorAssignmentSection
        )
        self.assertIn("Додати вибране як пари", source)
        self.assertIn("Taxo не групує два незалежні списки автоматично", source)


if __name__ == "__main__":
    unittest.main()
