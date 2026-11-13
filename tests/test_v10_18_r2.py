# -*- coding: utf-8 -*-
"""10.18-r2: military-accounting sorting, single-instance windows and confirmations."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import main
import military_accounting_ui
import military_transport_ui
import table_sorting

ROOT = Path(__file__).resolve().parents[1]


class MilitaryAccountingUiR2Tests(unittest.TestCase):
    def test_candidate_identity(self):
        self.assertIn(main.APP_VERSION, ("10.18-r2", "10.18-r3", "10.18-r4", "10.18-r5", "10.18-r6"))
        self.assertEqual((ROOT / "VERSION.txt").read_text("utf-8"), "Version: " + main.APP_VERSION + "\n")
        self.assertIn("Taxo " + main.APP_VERSION, (ROOT / "START.bat").read_text("utf-8"))

    def test_shared_sort_helpers_are_canonical(self):
        source = inspect.getsource(table_sorting.configure_sortable_tree)
        self.assertIn("sort_treeview(", source)
        self.assertNotIn(".execute(", source)
        self.assertNotIn(".commit(", source)
        self.assertIs(military_transport_ui._configure_sortable_tree, table_sorting.configure_sortable_tree)
        self.assertIs(military_transport_ui._restore_tree_selection, table_sorting.restore_tree_selection)

    def test_three_windows_are_single_instance_and_keep_explicit_close(self):
        source = inspect.getsource(military_accounting_ui.install)
        for attr in ("_military_accounting_overview_window", "_military_actions_window", "_military_reconciliation_window"):
            self.assertIn(attr, source)
        self.assertGreaterEqual(source.count("if _alive(existing):"), 3)
        self.assertGreaterEqual(source.count('text="Закрити", command=win.destroy'), 2)
        self.assertIn('text="Закрити",command=win.destroy', source)

    def test_actions_and_reconciliation_have_typed_sort(self):
        source = inspect.getsource(military_accounting_ui.install)
        for marker in (
            '("status", "Стан", "status", ("Відкрита", "Виконано", "Скасовано"))',
            '("due", "Строк", "date", None)',
            '("event", "Подія", "date", None)',
            '("date", "Дата", "date", None)',
            "apply_action_sort()",
            "apply_reconciliation_sort()",
        ):
            self.assertIn(marker, source)

    def test_refresh_restores_stable_ids(self):
        source = inspect.getsource(military_accounting_ui.install)
        self.assertIn('tree.insert("", "end", iid=str(row["id"])', source)
        self.assertIn('tree.insert("","end",iid=str(row["id"])', source)
        self.assertGreaterEqual(source.count("restore_tree_selection(tree, selected_ids)"), 2)

    def test_complete_action_requires_confirmation_before_db(self):
        source = inspect.getsource(military_accounting_ui.install)
        part = source.split("            def complete_selected():", 1)[1].split("            def set_order_date():", 1)[0]
        self.assertIn("askyesno(", part)
        self.assertIn("Позначити вибрану дію виконаною?", part)
        self.assertLess(part.index("askyesno("), part.index("con = core.db()"))


if __name__ == "__main__":
    unittest.main()
