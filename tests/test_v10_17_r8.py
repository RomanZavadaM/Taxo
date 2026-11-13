# -*- coding: utf-8 -*-
"""10.17-r8: order register typed sort, selection, and group-filter contracts."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import main
import order_register_ui
from table_sorting import sort_treeview, sorted_row_ids

ROOT = Path(__file__).resolve().parents[1]


class FakeTree:
    def __init__(self):
        self.records = {
            "12": {"date": "12.01.2025", "no": "12-К"},
            "2": {"date": "02.11.2026", "no": "2-К"},
            "3": {"date": "08.03.2024", "no": "3-К"},
        }
        self.order = ["12", "2", "3"]
        self.selected = ("12",)
        self.focused = "12"

    def get_children(self, parent=""):
        return tuple(self.order)

    def set(self, iid, column):
        return self.records[iid][column]

    def move(self, iid, parent, index):
        self.order.remove(iid)
        self.order.insert(index, iid)

    def selection(self):
        return self.selected

    def selection_set(self, iids):
        self.selected = (iids,) if isinstance(iids, str) else tuple(iids)

    def focus(self, iid=None):
        if iid is not None:
            self.focused = iid
        return self.focused


class OrderSortingR8Tests(unittest.TestCase):
    def test_identity(self):
        self.assertIn(main.APP_VERSION, ("10.17-r8", "10.17-r9", "10.17-r10", "10.18-r1", "10.18-r2", "10.18-r3", "10.18-r4", "10.18-r5", "10.18-r6", "10.18-r7", "10.18-r8"))
        self.assertEqual((ROOT / "VERSION.txt").read_text("utf-8"), "Version: " + main.APP_VERSION + "\n")
        self.assertIn("Taxo " + main.APP_VERSION, (ROOT / "START.bat").read_text("utf-8"))

    def test_order_number_natural_not_lexicographic(self):
        rows = [("a", "10-К"), ("b", "2-К"), ("c", "1-К"), ("d", "")]
        self.assertEqual(
            sorted_row_ids(rows, "no", value_type="text"),
            ["c", "b", "a", "d"],
        )
        self.assertEqual(
            sorted_row_ids(rows, "no", True, value_type="text"),
            ["a", "b", "c", "d"],
        )

    def test_order_date_is_a_date_and_missing_last(self):
        tree = FakeTree()
        self.assertEqual(sort_treeview(tree, "date", value_type="date"),
                         ["3", "12", "2"])
        self.assertEqual(tree.selection(), ("12",))
        self.assertEqual(tree.focus(), "12")
        self.assertEqual(sort_treeview(tree, "date", True, value_type="date"),
                         ["2", "12", "3"])

    def test_order_status_and_paper_are_explicit_ranks(self):
        self.assertEqual(
            sorted_row_ids(
                [("cancel", "Скасовано"), ("draft", "Чернетка"),
                 ("approved", "Діє в Taxo")],
                "status", value_type="status",
                status_order=("Чернетка", "Діє в Taxo", "Скасовано"),
            ),
            ["draft", "approved", "cancel"],
        )
        self.assertEqual(
            sorted_row_ids(
                [("no", "—"), ("yes", "підписано")],
                "paper", value_type="status",
                status_order=("підписано", "—"),
            ),
            ["yes", "no"],
        )

    def test_all_nine_columns_have_clickable_sort_and_visible_direction(self):
        source = inspect.getsource(order_register_ui.install_order_register)
        self.assertIn('("date", "Дата", 100, "date")', source)
        self.assertIn('("no", "№", 75, "text")', source)
        self.assertIn('("status", "Стан", 110, "status")', source)
        self.assertIn('("paper", "Паперовий оригінал", 140, "status")', source)
        self.assertIn("command=lambda name=key: sort_orders_by_header(name)", source)
        self.assertIn('direction = " ▼" if selected_sort[1] else " ▲"', source)

    def test_refresh_reapplies_sort_and_remembers_order_across_group_filter(self):
        source = inspect.getsource(order_register_ui.install_order_register)
        self.assertIn('order_tree.bind("<<TreeviewSelect>>", remember_order_selection', source)
        self.assertIn("remembered_order_id = current_selection[0]", source)
        self.assertIn("remembered_order_id = str(select_id)", source)
        self.assertIn('iid=str(oid)', source)
        self.assertIn("apply_order_sort()", source)
        self.assertIn("if remembered_order_id in visible_ids:", source)
        self.assertIn("order_tree.selection_set(remembered_order_id)", source)
        self.assertIn("order_tree.selection_set(())", source)
        self.assertIn("remembered_order_id = None", source)
        self.assertIn('group_filter_box.bind("<<ComboboxSelected>>"', source)

    def test_destructive_order_actions_still_require_confirmation(self):
        source = inspect.getsource(order_register_ui.install_order_register)
        for prompt in (
            '"Видалити наказ?"', '"Скасувати наказ?"',
            '"Ввести наказ у дію в Taxo?"',
        ):
            self.assertIn(prompt, source)
        self.assertIn("core.messagebox.askyesno(", source)


if __name__ == "__main__":
    unittest.main()
