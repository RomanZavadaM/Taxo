# -*- coding: utf-8 -*-
"""Regression: a ready-document tree filters existing records without copies."""
import unittest
from pathlib import Path

import document_catalog
from document_library_tree import navigation_nodes, matches_navigation


def row(identifier, kind, day):
    return {
        "key": ("order", identifier, 0), "source": "order",
        "sources": ("order",), "source_id": identifier,
        "date": day, "created_at": "2026-11-19T10:00:00",
        "kind": kind, "title": identifier, "number": identifier,
        "category": "Експлуатаційні", "employee_refs": (),
        "vehicle_refs": (), "person": "", "entity_text": "",
    }


class ReadyDocumentTreeR8Tests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            "rows": [
                row("a", "Наказ", "2026-11-18"),
                row("b", "Лист", "2025-01-10"),
                row("c", "Наказ", "2026-01-05"),
                row("d", "Акт", ""),
                row("e", "Лист", "invalid"),
            ],
            "paper_status": "", "order_status": "",
        }

    def filtered(self, value, **filters):
        return document_catalog.paginate_sources(
            self.snapshot, library_filter=value, **filters
        )

    def test_version_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.22-r8\n")
        self.assertIn('APP_VERSION = "10.22-r8"', (root / "main.py").read_text("utf-8"))
        self.assertIn("Taxo 10.22-r8", (root / "START.bat").read_text("utf-8"))

    def test_kind_groups_count_complete_snapshot_without_duplicates(self):
        nodes = navigation_nodes(self.snapshot, "kind")
        self.assertEqual(nodes[0][3], 5)
        self.assertEqual(
            {node[2]: node[3] for node in nodes[1:]},
            {"Акт": 1, "Лист": 2, "Наказ": 2},
        )
        self.assertEqual(
            [item["source_id"] for item in self.filtered(("kind", "Лист"))["rows"]],
            ["b", "e"],
        )

    def test_date_tree_includes_missing_dates(self):
        nodes = navigation_nodes(self.snapshot, "date")
        self.assertIn(("undated", "all", "Без дати", 2, ("undated",)), nodes)
        self.assertIn(
            ("month:2026:11", "year:2026", "11 — Листопад", 1, ("month", 2026, 11)),
            nodes,
        )
        self.assertEqual(self.filtered(("undated",))["total"], 2)
        self.assertEqual(self.filtered(("year", 2026))["total"], 2)

    def test_folder_selection_filters_before_pagination(self):
        result = self.filtered(("kind", "Наказ"), page_size=1, page=1)
        self.assertEqual(result["total"], 2)
        self.assertEqual([item["source_id"] for item in result["rows"]], ["c"])
        self.assertEqual(
            self.filtered(("month", 2026, 1))["rows"][0]["source_id"], "c"
        )

    def test_folder_filter_combines_with_existing_controls(self):
        self.assertEqual(self.filtered(("year", 2026), text_filter="a")["total"], 1)
        self.assertEqual(
            self.filtered(("year", 2026), date_from="2026-11-01")["total"], 1
        )
        self.assertEqual(self.filtered(("all",), kind_filter="Наказ")["total"], 2)

    def test_navigation_never_mutates_source(self):
        original = list(self.snapshot["rows"])
        self.filtered(("undated",))
        self.filtered(("kind", "Лист"))
        self.assertEqual(original, self.snapshot["rows"])
        self.assertFalse(matches_navigation(original[0], ("undated",)))
        with self.assertRaises(ValueError):
            navigation_nodes(self.snapshot, "unknown")

    def test_ui_uses_real_tree_on_existing_catalog(self):
        source = (Path(__file__).resolve().parents[1] / "src" / "taxo" / "document_catalog_ui.py").read_text("utf-8")
        self.assertIn('library_tree = core.ttk.Treeview(', source)
        self.assertIn('values=("За видами", "За датами")', source)
        self.assertIn('library_filter=library_filter', source)
        self.assertIn('library_tree.bind("<<TreeviewSelect>>", select_library_node)', source)


if __name__ == "__main__":
    unittest.main()
