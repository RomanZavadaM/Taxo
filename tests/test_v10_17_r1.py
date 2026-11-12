# -*- coding: utf-8 -*-
"""10.17-r1: sorting visible vehicle rows without altering business data."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import main
import table_sorting
import vehicle_registry_ui

ROOT = Path(__file__).resolve().parents[1]


class FakeTree:
    def __init__(self, rows):
        self.rows = {iid: dict(values) for iid, values in rows}
        self.order = [iid for iid, _ in rows]
        self.selected = ()
        self.focused = ""

    def get_children(self, parent=""):
        return tuple(self.order)

    def set(self, iid, column):
        return self.rows[iid][column]

    def move(self, iid, parent, index):
        self.order.remove(iid)
        self.order.insert(index, iid)

    def selection(self):
        return self.selected

    def selection_set(self, iids):
        self.selected = tuple(iids)

    def focus(self, iid=None):
        if iid is not None:
            self.focused = iid
        return self.focused


class VehicleTableSortingR1Tests(unittest.TestCase):
    def test_version_start_and_new_module(self):
        self.assertIn(main.APP_VERSION, ("10.17-r1", "10.17-r2", "10.17-r3", "10.17-r4", "10.17-r5", "10.17-r6"))
        self.assertEqual((ROOT / "VERSION.txt").read_text("utf-8"), "Version: " + main.APP_VERSION + "\n")
        start = (ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("table_sorting.py", start)

    def test_years_and_identifiers_are_numeric(self):
        rows = [("a", "2014"), ("b", "2008"), ("c", "1995"), ("d", "")]
        self.assertEqual(table_sorting.sorted_row_ids(rows, "year"), ["c", "b", "a", "d"])
        self.assertEqual(table_sorting.sorted_row_ids(rows, "year", True), ["a", "b", "c", "d"])
        self.assertEqual(table_sorting.sorted_row_ids([("x", "18"), ("y", "2")], "id"), ["y", "x"])

    def test_text_is_natural_and_case_insensitive(self):
        rows = [("a", "Авто 11"), ("b", "авто 2"), ("c", "Авто 1")]
        self.assertEqual(table_sorting.sorted_row_ids(rows, "name"), ["c", "b", "a"])

    def test_document_status_prioritizes_valid_then_problems(self):
        rows = [
            ("problem", "Проблема: Страховка"),
            ("ready", "Актуально"),
            ("missing", ""),
            ("unknown", "Потребує перевірки"),
        ]
        self.assertEqual(
            table_sorting.sorted_row_ids(rows, "documents"),
            ["ready", "unknown", "problem", "missing"],
        )
        self.assertEqual(
            table_sorting.sorted_row_ids(rows, "documents", True),
            ["problem", "unknown", "ready", "missing"],
        )

    def test_sort_preserves_visible_selection_and_focus(self):
        tree = FakeTree([
            ("first", {"year": "2014"}),
            ("second", {"year": "2006"}),
            ("third", {"year": ""}),
        ])
        tree.selected = ("first",)
        tree.focused = "first"
        result = table_sorting.sort_treeview(tree, "year")
        self.assertEqual(result, ["second", "first", "third"])
        self.assertEqual(tree.selection(), ("first",))
        self.assertEqual(tree.focus(), "first")

    def test_registry_keeps_filters_and_reapplies_selected_sort_after_refresh(self):
        source = inspect.getsource(vehicle_registry_ui)
        self.assertIn("command=lambda name=col: sort_by_header(name)", source)
        self.assertIn('sort_treeview(app.vehicle_tree, *selected_sort)', source)
        self.assertIn('selected_ids = _selected_vehicle_ids(app.vehicle_tree)', source)
        self.assertIn('from vehicle_form_ui import vehicle_form', source)
        self.assertNotIn("import main", source)

    def test_headings_mark_direction_without_mutating_data(self):
        class Headings:
            def __init__(self):
                self.texts = {}

            def heading(self, name, text):
                self.texts[name] = text

        tree = Headings()
        vehicle_registry_ui.update_sort_headings(
            tree, {"year": "Рік", "documents": "Документи"},
            ("year", True),
        )
        self.assertEqual(tree.texts["year"], "Рік ▼")
        self.assertEqual(tree.texts["documents"], "Документи")


if __name__ == "__main__":
    unittest.main()
