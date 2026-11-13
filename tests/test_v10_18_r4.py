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

class TachographTableSortingR4Tests(unittest.TestCase):
    def test_candidate_identity(self):
        self.assertEqual(main.APP_VERSION, "10.18-r4")
        self.assertEqual((ROOT / "VERSION.txt").read_text("utf-8"), "Version: 10.18-r4\n")
        self.assertIn("Taxo 10.18-r4", (ROOT / "START.bat").read_text("utf-8"))

    def test_numeric_zero_is_not_treated_as_missing(self):
        rows=(("zero",0),("two",2),("blank",""),("none",None))
        self.assertEqual(table_sorting.sorted_row_ids(rows,"km",value_type="number"),["zero","two","blank","none"])
        self.assertEqual(table_sorting.sorted_row_ids(rows,"km",descending=True,value_type="number"),["two","zero","blank","none"])

    def test_missing_dates_stay_last_in_both_directions(self):
        rows=(("missing",""),("old","02.01.2026"),("new","12.11.2026"))
        self.assertEqual(table_sorting.sorted_row_ids(rows,"date",value_type="date"),["old","new","missing"])
        self.assertEqual(table_sorting.sorted_row_ids(rows,"date",descending=True,value_type="date"),["new","old","missing"])

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
