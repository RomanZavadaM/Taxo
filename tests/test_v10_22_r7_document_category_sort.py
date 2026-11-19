# -*- coding: utf-8 -*-
"""Regression for category sorting across the full document catalog."""
import unittest
from pathlib import Path

import document_catalog


def row(identifier, category, day="2026-11-18", kind="Наказ"):
    return {
        "key": ("order", identifier, 0),
        "source": "order", "sources": ("order",),
        "source_id": identifier, "source_label": "Наказ",
        "date": day, "created_at": day + "T12:00:00",
        "number": identifier, "kind": kind,
        "title": "Документ " + identifier,
        "person": "", "entity_text": "",
        "employee_refs": (), "vehicle_refs": (),
        "order_type": "", "order_series": "",
        "category": category,
        "revision_label": "", "file_state": "Файл не прив'язаний",
        "vault_id": "", "paper_scan_count": 0,
        "paper_scan_state": "—", "paper_original_state": "—",
    }


class DocumentCategorySortR7Tests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            "rows": [
                row("season", "Сезонні заходи"),
                row("unknown", document_catalog.CATEGORY_UNCLASSIFIED),
                row("safety", "Безпека дорожнього руху"),
                row("labor", "Охорона праці"),
                row("operations", "Експлуатаційні"),
                row("personnel", "Кадрові"),
            ],
            "paper_status": "", "vault_status": "",
            "paper_scan_status": "", "paper_original_status": "",
            "order_status": "",
        }

    def ids(self, **kwargs):
        result = document_catalog.paginate_sources(
            self.snapshot, page_size=100, **kwargs
        )
        return [item["source_id"] for item in result["rows"]]

    def test_version_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.22-r9\n")
        self.assertIn('APP_VERSION = "10.22-r9"', (root / "main.py").read_text("utf-8"))
        self.assertIn("Taxo 10.22-r9", (root / "START.bat").read_text("utf-8"))

    def test_category_sort_ascending_and_descending(self):
        self.assertEqual(
            self.ids(category_sort="ascending"),
            ["safety", "operations", "personnel", "labor", "season", "unknown"],
        )
        self.assertEqual(
            self.ids(category_sort="descending"),
            ["season", "labor", "personnel", "operations", "safety", "unknown"],
        )

    def test_unclassified_stays_last_and_sort_is_before_paging(self):
        page = document_catalog.paginate_sources(
            self.snapshot, category_sort="ascending",
            source_filter="order",
            date_from="2026-11-18", date_to="2026-11-18",
            page_size=2, page=1,
        )
        self.assertEqual(page["total"], 6)
        self.assertEqual(page["pages"], 3)
        self.assertEqual([item["source_id"] for item in page["rows"]], ["personnel", "labor"])

    def test_default_order_and_snapshot_are_unchanged(self):
        before = self.ids()
        self.ids(category_sort="ascending")
        self.ids(category_sort="descending")
        self.assertEqual(before, self.ids())
        self.assertEqual(before, [item["source_id"] for item in self.snapshot["rows"]])

    def test_ui_heading_exposes_category_toggle(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn(
            'tree.heading("category", text="Категорія", command=toggle_category_sort)',
            source,
        )
        self.assertIn("category_sort=category_sort", source)
        self.assertIn('state["sort_field"] = "category"', source)
        self.assertIn("refresh(reset=True)", source)


if __name__ == "__main__":
    unittest.main()
