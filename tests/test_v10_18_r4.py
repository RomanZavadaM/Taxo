# -*- coding: utf-8 -*-
"""10.18-r4: tachograph table sorting and sorting edge cases."""
from __future__ import annotations
import inspect
import unittest
from pathlib import Path
import main
import table_sorting
import tachograph

ROOT = Path(__file__).resolve().parents[1]


class FakeTree:
    def __init__(self):
        self.records = {
            "zero": {"confidence": 0},
            "two": {"confidence": 2},
            "blank": {"confidence": ""},
        }
        self.order = ["blank", "two", "zero"]
        self.selected = ("zero",)
        self.focused = "zero"
        self.headings = {}

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

    def heading(self, key, **kwargs):
        self.headings.setdefault(key, {}).update(kwargs)


class TachographTableSortingR4Tests(unittest.TestCase):
    def test_candidate_identity(self):
        self.assertIn(main.APP_VERSION, ("10.18-r4", "10.18-r5"))
        self.assertIn((ROOT / "VERSION.txt").read_text("utf-8"), ("Version: 10.18-r4\n", "Version: 10.18-r5\n"))
        self.assertIn("Taxo %s" % main.APP_VERSION, (ROOT / "START.bat").read_text("utf-8"))

    def test_numeric_zero_is_not_treated_as_missing(self):
        rows=(("zero",0),("two",2),("blank",""),("none",None))
        self.assertEqual(table_sorting.sorted_row_ids(rows,"km",value_type="number"),["zero","two","blank","none"])
        self.assertEqual(table_sorting.sorted_row_ids(rows,"km",descending=True,value_type="number"),["two","zero","blank","none"])

    def test_missing_dates_stay_last_in_both_directions(self):
        rows=(("missing",""),("old","02.01.2026"),("new","12.11.2026"))
        self.assertEqual(table_sorting.sorted_row_ids(rows,"date",value_type="date"),["old","new","missing"])
        self.assertEqual(table_sorting.sorted_row_ids(rows,"date",descending=True,value_type="date"),["new","old","missing"])

    def test_current_sort_reapplies_after_refresh_with_zero_and_blank(self):
        tree=FakeTree()
        state={}
        apply_sort=table_sorting.configure_sortable_tree(
            tree,
            (("confidence","Впевненість","number",None),),
            state,
            "intervals",
        )
        tree.headings["confidence"]["command"]()
        self.assertEqual(tree.order,["zero","two","blank"])
        self.assertEqual(tree.selection(),("zero",))

        # Simulate a refresh that restores rows in database/default order.
        tree.order=["two","blank","zero"]
        apply_sort()
        self.assertEqual(tree.order,["zero","two","blank"])
        self.assertEqual(tree.selection(),("zero",))

    def test_tachograph_working_tables_use_typed_sorting(self):
        source=inspect.getsource(tachograph.TachographModule.build)
        for marker in (
            '("id","ID","number",None)',
            '("disc","Шайба","number",None)',
            '("date","Дата","date",None)',
            '("start","Початок","duration",None)',
            '("end","Кінець","duration",None)',
            '("confidence","Впевненість","number",None)',
            'self.apply_disc_sort=configure_sortable_tree(',
            'self.apply_interval_sort=configure_sortable_tree(',
        ):
            self.assertIn(marker,source)

    def test_refresh_reapplies_sort_and_restores_stable_ids(self):
        source=inspect.getsource(tachograph.TachographModule.load)
        self.assertIn('iid=str(r["id"])',source)
        self.assertIn("self.apply_disc_sort()",source)
        self.assertIn("restore_tree_selection(self.tree,selected_ids)",source)
        source=inspect.getsource(tachograph.TachographModule.load_intervals)
        self.assertIn('iid=str(r["id"])',source)
        self.assertIn("self.apply_interval_sort()",source)
        self.assertIn("restore_tree_selection(self.itree,selected_ids)",source)

    def test_sorting_layer_does_not_write_database(self):
        source=inspect.getsource(table_sorting)
        self.assertNotIn(".execute(",source)
        self.assertNotIn(".commit(",source)

if __name__ == "__main__":
    unittest.main()
