# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
from datetime import date
import sqlite3

import personnel_registry as registry

ROOT=Path(__file__).resolve().parents[1]


class TestTaxo104R7DocumentControlBoundary(unittest.TestCase):
    def test_r7_checkpoint_identity_remains_historical(self):
        release_index=(ROOT/"docs/releases/RELEASE_INDEX.md").read_text("utf-8")
        self.assertIn("Taxo 10.4-r7",release_index)
        self.assertIn("9f397a092fe828570927bc39cef7a3a467e2aff0",release_index)
        self.assertIn("immutable",release_index)

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

    def test_registry_modes_never_delete_missing_values(self):
        changes=[
            {"old":"LOCAL","new":"REGISTRY"},
            {"old":"","new":"NEW"},
            {"old":"LOCAL_ONLY","new":""},
        ]
        self.assertEqual(registry._changes_for_mode(changes,registry.IMPORT_COMPARE),[])
        fill=registry._changes_for_mode(changes,registry.IMPORT_FILL_EMPTY)
        self.assertEqual([c["new"] for c in fill],["NEW"])
        update=registry._changes_for_mode(changes,registry.IMPORT_UPDATE)
        self.assertEqual([c["new"] for c in update],["REGISTRY","NEW"])

    def test_quarterly_status_uses_calendar_quarter(self):
        con=sqlite3.connect(":memory:")
        con.row_factory=sqlite3.Row
        con.execute("CREATE TABLE employees(id INTEGER PRIMARY KEY, active INTEGER, last_name TEXT, first_name TEXT, middle_name TEXT)")
        registry.ensure_schema_on_connection(con)
        con.execute("INSERT INTO employee_registry_imports(source_kind,source_name,file_sha256,imported_at,total_rows,mode) VALUES(?,?,?,?,?,?)",
                    (registry.SOURCE_SUMMARY,"test.xlsx","abc","2026-07-01T09:00:00",1,registry.IMPORT_COMPARE))
        self.assertTrue(registry.registry_quarter_status(con,today=date(2026,9,30))["current"])
        self.assertFalse(registry.registry_quarter_status(con,today=date(2026,10,1))["current"])
        con.close()

    def test_boundary_is_recorded_as_permanent_rule(self):
        rules=(ROOT/"PROJECT_RULES.md").read_text("utf-8")
        self.assertIn("Державні реєстри та локальний контроль документів",rules)
        self.assertIn("не визначає статуси",rules)
        self.assertIn("vehicle_document_summary",rules)


if __name__=="__main__":
    unittest.main()
