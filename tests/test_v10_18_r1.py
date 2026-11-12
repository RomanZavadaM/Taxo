# -*- coding: utf-8 -*-
"""10.18-r1: sortable military-transport registers with stable selection."""
from __future__ import annotations
import inspect
import unittest
from pathlib import Path
import main
import military_transport_ui

ROOT = Path(__file__).resolve().parents[1]

class FakeTree:
    def __init__(self):
        self.records = {
            "old": {"date": "02.01.2026", "status": "Виконано"},
            "new": {"date": "12.11.2026", "status": "Відкрита"},
            "none": {"date": "", "status": "Скасовано"},
        }
        self.order = ["new", "none", "old"]
        self.selected = ("new",)
        self.focused = "new"
        self.headings = {}
        self.seen = None
    def get_children(self, parent=""): return tuple(self.order)
    def set(self, iid, column): return self.records[iid][column]
    def move(self, iid, parent, index):
        self.order.remove(iid); self.order.insert(index, iid)
    def selection(self): return self.selected
    def selection_set(self, iids):
        self.selected = (iids,) if isinstance(iids, str) else tuple(iids)
    def focus(self, iid=None):
        if iid is not None: self.focused = iid
        return self.focused
    def see(self, iid): self.seen = iid
    def heading(self, key, **kwargs): self.headings.setdefault(key, {}).update(kwargs)

class MilitaryTransportSortingR1Tests(unittest.TestCase):
    def test_candidate_identity(self):
        self.assertIn(main.APP_VERSION, ("10.18-r1", "10.18-r2", "10.18-r3"))
        self.assertEqual((ROOT/"VERSION.txt").read_text("utf-8"), "Version: " + main.APP_VERSION + "\n")
        self.assertIn("Taxo " + main.APP_VERSION, (ROOT/"START.bat").read_text("utf-8"))

    def test_sort_helper_clicks_dates_and_keeps_missing_last(self):
        tree=FakeTree(); state={}
        military_transport_ui._configure_sortable_tree(
            tree,
            (("date","Дата","date",None),
             ("status","Стан","status",("Відкрита","Виконано","Скасовано"))),
            state,"demo",
        )
        tree.headings["date"]["command"]()
        self.assertEqual(tree.order, ["old","new","none"])
        self.assertEqual(tree.selection(), ("new",))
        self.assertEqual(tree.headings["date"]["text"], "Дата ▲")
        tree.headings["date"]["command"]()
        self.assertEqual(tree.order, ["new","old","none"])
        self.assertEqual(tree.headings["date"]["text"], "Дата ▼")

    def test_restore_selection_uses_stable_visible_ids(self):
        tree=FakeTree(); tree.selected=()
        kept=military_transport_ui._restore_tree_selection(tree,("missing","old"))
        self.assertEqual(kept,("old",))
        self.assertEqual(tree.selection(),("old",))
        self.assertEqual(tree.focus(),"old")
        self.assertEqual(tree.seen,"old")

    def test_all_five_working_tables_are_type_aware(self):
        source=inspect.getsource(military_transport_ui.install)
        for marker in (
            '("next", "Наступна дія", "date", None)',
            '("date", "Дата", "date", None)',
            '("due", "Строк", "date", None)',
            '("submitted", "Подано", "datetime", None)',
            '("from", "Від", "date", None)',
            'apply_vehicle_sort = _configure_sortable_tree(',
            'apply_order_sort = _configure_sortable_tree(',
            'apply_action_sort = _configure_sortable_tree(',
            'apply_report_sort = _configure_sortable_tree(',
            'apply_worker_sort = _configure_sortable_tree(',
        ): self.assertIn(marker,source)

    def test_refresh_uses_stable_ids_and_reapplies_sort(self):
        source=inspect.getsource(military_transport_ui.install)
        self.assertIn('report_tree.insert("","end",iid=str(row["id"])',source)
        self.assertIn('worker_tree.insert("","end",iid=str(row["id"])',source)
        for marker in (
            "apply_vehicle_sort()","apply_order_sort()","apply_action_sort()",
            "apply_report_sort()","apply_worker_sort()",
            "_restore_tree_selection(order_tree, selected_ids)",
            "_restore_tree_selection(action_tree, selected_ids)",
            "_restore_tree_selection(report_tree, selected_ids)",
            "_restore_tree_selection(worker_tree, selected_ids)",
        ): self.assertIn(marker,source)

    def test_sort_helpers_are_ui_only(self):
        source=inspect.getsource(military_transport_ui._configure_sortable_tree)
        self.assertNotIn("core.db",source)
        self.assertNotIn(".execute(",source)
        self.assertNotIn(".commit(",source)
        self.assertIn("sort_treeview(",source)

if __name__=="__main__":
    unittest.main()
