# -*- coding: utf-8 -*-
from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path
import version_compat  # 10.10 stable-aware version parsing


class RetentionBackupOrderR6Tests(unittest.TestCase):
    @staticmethod
    def _init_db_call_order():
        tree = ast.parse(Path("main.py").read_text(encoding="utf-8"))
        fn = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "init_db"
        )
        calls = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in {"auto_backup_database", "purge_old"}:
                    calls.append((node.lineno, node.func.id))
        return [name for _line, name in sorted(calls)]

    @staticmethod
    def _current_version_tuple():
        text = Path("VERSION.txt").read_text(encoding="utf-8")
        match = version_compat.search_version_line(text)
        if not match:
            raise AssertionError("Current VERSION.txt has no Taxo candidate version")
        return tuple(map(int, match.groups()))

    def test_backup_precedes_retention_purge(self):
        calls = self._init_db_call_order()
        self.assertIn("auto_backup_database", calls)
        self.assertIn("purge_old", calls)
        self.assertLess(calls.index("auto_backup_database"), calls.index("purge_old"))

    def test_purge_keeps_48_month_cutoff_contract(self):
        text = Path("main.py").read_text(encoding="utf-8")
        self.assertIn("- 47", text)
        self.assertIn('DELETE FROM worklog WHERE work_date < ?', text)
        self.assertIn('DELETE FROM employee_time_entries WHERE work_date < ?', text)

    def test_r6_runtime_layer_remains_in_chain_after_later_revisions(self):
        text = Path("taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from v1076_features import install as install_v1076", text)
        self.assertIn("App = install_v1076(core, App)", text)
        self.assertGreater(
            text.index("App = install_v1076(core, App)"),
            text.index("App = install_v1075(core, App)"),
        )

    def test_r6_historical_identity_is_preserved_while_current_may_advance(self):
        self.assertGreaterEqual(self._current_version_tuple(), (10, 7, 6))
        historical = Path("v1076_features.py").read_text(encoding="utf-8")
        self.assertIn('APP_VERSION = "10.7-r6"', historical)
        notes = Path("docs/releases/RELEASE_NOTES_v10.7-r6.md").read_text(encoding="utf-8")
        self.assertIn("10.7-r6", notes)


if __name__ == "__main__":
    unittest.main()
