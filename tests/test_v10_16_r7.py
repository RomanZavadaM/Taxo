# -*- coding: utf-8 -*-
"""10.16-r7: order persistence stays outside Tk and preserves pair integrity."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import main
import order_editor_persistence
import order_editor_ui

ROOT = Path(__file__).resolve().parents[1]


def operations():
    return SimpleNamespace(
        TYPE_VEHICLE_ASSIGNMENT="vehicle_assignment",
        create_vehicle_assignment_order=mock.Mock(return_value=42),
        verify_vehicle_assignment_pairs=mock.Mock(return_value=2),
        create_order=mock.Mock(return_value=43),
        update_order=mock.Mock(),
    )


class OrderEditorPersistenceR7Tests(unittest.TestCase):
    def setUp(self):
        self.ops = operations()
        self.connection = object()
        self.values = dict(
            existing=None,
            order_type="vehicle_assignment",
            order_series="work",
            order_no="7",
            order_date="11.11.2026",
            place="Львів",
            subject="Закріплення",
            preamble="Підстава",
            body_text="Наказую",
            control_employee_id=3,
            initial_pairs=[(10, 1), (10, 2)],
        )

    def test_version_and_package_guard(self):
        self.assertIn(main.APP_VERSION, ("10.16-r7", "10.16-r8", "10.16-r9", "10.16-r10", "10.17-r1", "10.17-r2", "10.17-r3"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text(encoding="utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        start = (ROOT / "START.bat").read_text(encoding="utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("order_editor_persistence.py", start)

    def test_ui_delegates_write_but_retains_commit_and_rollback(self):
        source = inspect.getsource(order_editor_ui.open_order_editor)
        self.assertIn("order_editor_persistence.save_order(", source)
        self.assertIn("connection.commit()", source)
        self.assertIn("connection.rollback()", source)
        self.assertNotIn("ops.create_vehicle_assignment_order(", source)
        self.assertNotIn("ops.verify_vehicle_assignment_pairs(", source)
        self.assertIn("assignment_section.initial_pairs_for_save(", source)

    def test_assignment_creation_verifies_all_selected_pairs(self):
        result = order_editor_persistence.save_order(
            self.ops, self.connection, **self.values
        )
        self.assertEqual(result, 42)
        self.ops.create_vehicle_assignment_order.assert_called_once()
        self.assertEqual(
            self.ops.create_vehicle_assignment_order.call_args.kwargs["initial_pairs"],
            [(10, 1), (10, 2)],
        )
        self.ops.verify_vehicle_assignment_pairs.assert_called_once_with(
            self.connection, 42, [(10, 1), (10, 2)]
        )

    def test_partial_assignment_write_raises_before_commit(self):
        self.ops.verify_vehicle_assignment_pairs.return_value = 1
        with self.assertRaisesRegex(RuntimeError, "очікувалось 2, у наказі 1"):
            order_editor_persistence.save_order(
                self.ops, self.connection, **self.values
            )

    def test_existing_order_keeps_history_without_recreating_pairs(self):
        values = dict(self.values)
        values["existing"] = {"id": 15}
        result = order_editor_persistence.save_order(
            self.ops, self.connection, **values
        )
        self.assertEqual(result, 15)
        self.ops.update_order.assert_called_once()
        self.assertEqual(
            self.ops.update_order.call_args.kwargs["history_note"],
            "Редагування через інтерфейс",
        )
        self.ops.create_vehicle_assignment_order.assert_not_called()

    def test_other_order_type_uses_existing_create_order(self):
        values = dict(self.values)
        values["order_type"] = "general"
        values["initial_pairs"] = []
        result = order_editor_persistence.save_order(
            self.ops, self.connection, **values
        )
        self.assertEqual(result, 43)
        self.ops.create_order.assert_called_once()
        self.ops.verify_vehicle_assignment_pairs.assert_not_called()


if __name__ == "__main__":
    unittest.main()
