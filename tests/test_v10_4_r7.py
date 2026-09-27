# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class TestTaxo104R7DocumentControlBoundary(unittest.TestCase):
    def test_current_identity_is_r7(self):
        version=(ROOT/"VERSION.txt").read_text("utf-8")
        main=(ROOT/"main.py").read_text("utf-8")
        self.assertIn("Version: 10.4-r7",version)
        self.assertIn('APP_VERSION = "10.4-r7"',main)

    def test_vehicle_control_tree_is_child_of_grid_container(self):
        source=(ROOT/"vehicle_documents.py").read_text("utf-8")
        start=source.index("def open_vehicle_document_control")
        block=source[start:]
        self.assertIn("table = ttk.Frame(win)",block)
        self.assertIn("tree = ttk.Treeview(table, columns=cols",block)
        self.assertNotIn("tree = ttk.Treeview(win, columns=cols",block)
        self.assertLess(block.index("table = ttk.Frame(win)"), block.index("tree = ttk.Treeview(table"))

    def test_operational_document_control_has_no_registry_dependency(self):
        source=(ROOT/"vehicle_documents.py").read_text("utf-8")
        self.assertNotIn("from personnel_registry",source)
        self.assertNotIn("import personnel_registry",source)
        self.assertNotIn("registry_reconciliation",source)
        self.assertNotIn("shlyah",source.lower())

    def test_boundary_is_recorded_as_permanent_rule(self):
        rules=(ROOT/"PROJECT_RULES.md").read_text("utf-8")
        self.assertIn("Державні реєстри та локальний контроль документів",rules)
        self.assertIn("не визначає статуси",rules)
        self.assertIn("vehicle_document_summary",rules)


if __name__=="__main__":
    unittest.main()
