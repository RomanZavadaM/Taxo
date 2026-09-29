# -*- coding: utf-8 -*-
from __future__ import annotations

import ast
import unittest
from pathlib import Path


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

    def test_r6_runtime_layer_is_outermost(self):
        text = Path("taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from v1076_features import install as install_v1076", text)
        self.assertIn("App = install_v1076(core, App)", text)
        self.assertGreater(
            text.index("App = install_v1076(core, App)"),
            text.index("App = install_v1075(core, App)"),
        )

    def test_current_identity_is_r6(self):
        self.assertIn("Version: 10.7-r6", Path("VERSION.txt").read_text(encoding="utf-8"))
        self.assertIn('APP_VERSION = "10.7-r6"', Path("main.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
