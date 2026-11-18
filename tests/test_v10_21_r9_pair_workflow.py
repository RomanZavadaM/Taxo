# -*- coding: utf-8 -*-
"""10.22-r1: regression for exact order-scoped assignment workflows."""
from __future__ import annotations

import inspect
import sqlite3
import unittest
from types import SimpleNamespace
from unittest import mock

import operations_orders as ops
import order_editor_assignments_ui
import order_editor_ui
from test_v10_13_r8 import make_db


class PairWorkflowR9Tests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()

    def tearDown(self):
        self.con.close()

    def section(self, pairs=None):
        section = order_editor_assignments_ui.OrderEditorAssignmentSection.__new__(
            order_editor_assignments_ui.OrderEditorAssignmentSection
        )
        section.core = SimpleNamespace(
            messagebox=SimpleNamespace(
                showerror=mock.Mock(), showinfo=mock.Mock(),
                askyesno=mock.Mock(return_value=True),
            )
        )
        section.ops = ops
        section.dialog = object()
        section.existing = None
        section.box = object()
        section.initial_vehicles = [
            {"id": 10, "label": "Автобус 10"},
            {"id": 20, "label": "Автобус 20"},
        ]
        section.initial_drivers = [
            {"id": 1, "label": "Іваненко"},
            {"id": 2, "label": "Петренко"},
        ]
        section.initial_vehicle_list = mock.Mock()
        section.initial_driver_list = mock.Mock()
        section.staged_pair_tree = mock.Mock()
        section.staged_initial_pairs = list(pairs or [])
        section.assignment_count_var = mock.Mock()
        section._render_staged_pairs = mock.Mock()
        section.staged_pair_tree.selection.return_value = ("1",)
        section.initial_vehicle_list.curselection.return_value = (1,)
        section.initial_driver_list.curselection.return_value = (0,)
        return section

    def test_reverse_order_is_not_automatically_zipped(self):
        with self.assertRaisesRegex(ValueError, "Автоматичне парування"):
            ops.build_assignment_pairs([20, 10], [1, 2])

    def test_replace_one_staged_pair_keeps_other_pair(self):
        sec = self.section([(10, 1), (20, 2)])
        sec._replace_selected_pair()
        self.assertEqual(sec.staged_initial_pairs, [(20, 1), (20, 2)])
        sec._render_staged_pairs.assert_called_once()

    def test_duplicate_pair_replacement_does_not_modify_any_row(self):
        sec = self.section([(10, 1), (20, 2)])
        sec.initial_driver_list.curselection.return_value = (1,)
        sec._replace_selected_pair()
        self.assertEqual(sec.staged_initial_pairs, [(10, 1), (20, 2)])
        sec.core.messagebox.showerror.assert_called_once()
        sec._render_staged_pairs.assert_not_called()

    def test_ambiguous_pair_replacement_refuses_mutation(self):
        sec = self.section([(10, 1), (20, 2)])
        sec.initial_driver_list.curselection.return_value = (0, 1)
        sec._replace_selected_pair()
        self.assertEqual(sec.staged_initial_pairs, [(10, 1), (20, 2)])
        sec._render_staged_pairs.assert_not_called()

    def test_double_click_loads_exact_staged_pair(self):
        sec = self.section([(10, 1), (20, 2)])
        sec.staged_pair_tree.selection.return_value = ("2",)
        sec._load_selected_staged_pair()
        sec.initial_vehicle_list.selection_set.assert_called_with(1)
        sec.initial_driver_list.selection_set.assert_called_with(1)

    def test_prepared_pair_copy_deduplicates_and_keeps_associations(self):
        sec = self.section([(20, 1)])
        count = sec._merge_prepared_pairs([
            (10, 2), (20, 1), (10, 2), (20, 2)
        ])
        self.assertEqual(count, 2)
        self.assertEqual(sec.staged_initial_pairs, [
            (20, 1), (10, 2), (20, 2)
        ])

    def test_import_reads_existing_order_pairs_not_list_positions(self):
        source = ops.create_vehicle_assignment_order(
            self.con, order_no="101", order_date="17.11.2026",
            initial_pairs=[(20, 1), (10, 2)]
        )
        self.con.commit()
        sec = self.section()
        sec.core.db = mock.Mock(return_value=self.con)
        # Read using a non-closing connection proxy for this in-memory test.
        class Proxy:
            def __getattr__(self, key):
                return getattr(self.con, key)
            def __init__(self, con):
                self.con = con
            def close(self):
                pass
        sec.core.db.return_value = Proxy(self.con)
        available = sec._available_prepared_pairs()
        self.assertEqual(
            [(v, d) for v, d, _, _ in available],
            [(20, 1), (10, 2)]
        )
        self.assertEqual(sec._merge_prepared_pairs(
            [(v, d) for v, d, _, _ in available]), 2)
        self.assertEqual(ops.vehicle_assignment_pairs(self.con, source),
                         [(20, 1), (10, 2)])

    def test_create_save_reopen_exact_pairs_and_keep_original_unchanged(self):
        original = ops.create_vehicle_assignment_order(
            self.con, order_no="201", order_date="17.11.2026",
            initial_pairs=[(20, 1), (10, 2)]
        )
        new_id = ops.create_vehicle_assignment_order(
            self.con, order_no="202", order_date="18.11.2026",
            initial_pairs=[(20, 1), (10, 2)]
        )
        self.con.commit()
        self.assertEqual(ops.vehicle_assignment_pairs(self.con, new_id),
                         [(20, 1), (10, 2)])
        self.assertEqual(ops.vehicle_assignment_pairs(self.con, original),
                         [(20, 1), (10, 2)])

    def test_existing_pair_update_reopen_and_delete(self):
        order = ops.create_vehicle_assignment_order(
            self.con, order_date="17.11.2026",
            initial_pairs=[(10, 1), (20, 2)]
        )
        existing = ops.order_assignments(self.con, order)
        target = int(existing[0]["id"])
        ops.update_vehicle_assignment(
            self.con, target, vehicle_id=20, employee_id=1,
            valid_from="17.11.2026", history_note="Тест",
        )
        self.con.commit()
        self.assertEqual(ops.vehicle_assignment_pairs(self.con, order),
                         [(20, 1), (20, 2)])
        self.assertEqual(int(ops.get_vehicle_assignment(self.con, target)["employee_id"]), 1)
        ops.delete_vehicle_assignment(self.con, existing[1]["id"],
                                      history_note="Тест")
        self.con.commit()
        self.assertEqual(ops.vehicle_assignment_pairs(self.con, order),
                         [(20, 1)])

    def test_existing_duplicate_update_refused_and_original_kept(self):
        order = ops.create_vehicle_assignment_order(
            self.con, order_date="17.11.2026",
            initial_pairs=[(10, 1), (20, 2)]
        )
        self.con.commit()
        rows = ops.order_assignments(self.con, order)
        with self.assertRaisesRegex(ValueError, "вже є"):
            ops.update_vehicle_assignment(
                self.con, rows[0]["id"],
                vehicle_id=20, employee_id=2,
                valid_from="17.11.2026",
            )
        self.con.rollback()
        self.assertEqual(ops.vehicle_assignment_pairs(self.con, order),
                         [(10, 1), (20, 2)])

    def test_delete_cancel_preserves_pair(self):
        sec = self.section()
        sec.existing_pair_tree = mock.Mock()
        sec.existing_pair_tree.selection.return_value = ("31",)
        sec.core.messagebox.askyesno.return_value = False
        sec.core.db = mock.Mock()
        sec._remove_existing_pair()
        sec.core.db.assert_not_called()
        sec.core.messagebox.askyesno.assert_called_once()

    def test_existing_editor_edits_in_place_without_tab_switch(self):
        source = inspect.getsource(
            order_editor_assignments_ui.OrderEditorAssignmentSection._edit_existing_pair
        )
        self.assertIn("self._pair_dialog(", source)
        self.assertNotIn("self.dialog.destroy()", source)
        self.assertNotIn("self.book.select(", source)

    def test_save_in_pair_dialog_refreshes_current_order(self):
        source = inspect.getsource(
            order_editor_assignments_ui.OrderEditorAssignmentSection._pair_dialog
        )
        self.assertIn("self._refresh_existing_pairs(", source)
        self.assertIn("self.ops.verify_vehicle_assignment_pairs(", source)
        self.assertIn("con2.commit()", source)

    def test_existing_order_section_is_not_placed_over_presets(self):
        source = inspect.getsource(
            order_editor_assignments_ui.OrderEditorAssignmentSection._build_existing_order_section
        )
        self.assertIn("row=8", source)

    def test_new_order_save_still_uses_staged_explicit_pairs(self):
        source = inspect.getsource(order_editor_ui.open_order_editor)
        self.assertIn("assignment_section.initial_pairs_for_save", source)

    def test_saved_order_never_jumps_to_unrelated_assignment_tab(self):
        source = inspect.getsource(order_editor_ui.open_order_editor)
        self.assertNotIn("book.select(assignments_tab)", source)
        self.assertIn("book.select(orders_tab)", source)


if __name__ == "__main__":
    unittest.main()
