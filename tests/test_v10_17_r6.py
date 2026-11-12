# -*- coding: utf-8 -*-
"""10.17-r6: route UI consistency, sortable register, and operations-history exit."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import main
import order_register_ui

ROOT = Path(__file__).resolve().parents[1]


class RouteUiConsistencyR6Tests(unittest.TestCase):
    def test_revision_identity(self):
        self.assertIn(main.APP_VERSION, ("10.17-r6", "10.17-r7"))
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: " + main.APP_VERSION + "\n",
        )
        self.assertIn("Taxo " + main.APP_VERSION, (ROOT / "START.bat").read_text("utf-8"))

    def test_route_register_is_click_sortable_and_refresh_preserves_selection(self):
        build = inspect.getsource(main.App.build_route_catalog)
        self.assertIn("command=lambda name=c:self.sort_route_catalog(name)", build)
        self.assertIn("self.route_catalog_sort", build)

        sorter = inspect.getsource(main.App.sort_route_catalog)
        self.assertIn("sort_treeview(self.route_catalog_tree,column,descending)", sorter)
        self.assertIn("update_route_catalog_sort_headings", sorter)

        refresh = inspect.getsource(main.App.load_route_catalog)
        self.assertIn("selected_route_id", refresh)
        self.assertIn('iid=str(r["id"])', refresh)
        self.assertIn("sort_treeview(self.route_catalog_tree,*selected_sort)", refresh)
        self.assertIn("selection_set(selected_route_id)", refresh)
        self.assertIn("self.route_catalog_tree.see(selected_route_id)", refresh)

    def test_route_editor_has_explicit_non_saving_exits(self):
        source = inspect.getsource(main.App.route_catalog_form)
        self.assertGreaterEqual(source.count('text="Скасувати"'), 5)
        self.assertIn('text="Зберегти маршрут"', source)
        self.assertIn('text="Готово — повернутися до маршруту"', source)
        self.assertNotIn('text="Скасувати",command=save', source)
        self.assertNotIn('text="Скасувати",command=save_stop', source)
        self.assertNotIn('text="Скасувати",command=save_seg', source)
        self.assertNotIn("WM_DELETE_WINDOW", source)

    def test_route_draft_deletions_require_confirmation(self):
        source = inspect.getsource(main.App.route_catalog_form)
        stop_prompt = source.index('"Видалити точку маршруту?"')
        stop_pop = source.index("stop_data[d].pop(index)")
        self.assertLess(stop_prompt, stop_pop)

        segment_prompt = source.index('"Видалити частину маршруту?"')
        segment_pop = source.index("seg_data.pop(index)")
        self.assertLess(segment_prompt, segment_pop)
        self.assertGreaterEqual(source.count("messagebox.askyesno("), 3)

    def test_order_history_toplevel_has_explicit_close(self):
        source = inspect.getsource(order_register_ui.install_order_register)
        history = source.split("    def show_history():", 1)[1].split(
            "    def _order_print_data", 1
        )[0]
        self.assertIn('text="Закрити",command=dlg.destroy', history)
        self.assertNotIn("commit()", history)
        self.assertNotIn("UPDATE ", history)
        self.assertNotIn("DELETE ", history)


if __name__ == "__main__":
    unittest.main()
