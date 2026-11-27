# -*- coding: utf-8 -*-
"""Regression for natural number sort across the full document catalog."""
import unittest
from pathlib import Path

import document_catalog


def row(identifier, number, day="2026-11-17", kind="Наказ", scans=0):
    return {
        "key": ("order", identifier, 0),
        "source": "order", "sources": ("order",),
        "source_id": identifier,
        "source_label": "Наказ",
        "date": day, "created_at": day + "T12:00:00",
        "number": number, "kind": kind,
        "title": "Документ " + identifier,
        "person": "", "order_type": "",
        "revision_label": "", "file_state": "Файл не прив'язаний",
        "vault_id": "", "paper_scan_count": scans,
        "paper_scan_state": "—",
    }


class DocumentNumberSortR5Tests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            "rows": [
                row("ten", "10"),
                row("blank", ""),
                row("two", "2"),
                row("a10", "10-А"),
                row("a2", "2-А"),
                row("one", "1"),
                row("none", "  "),
                row("other", "5", kind="Інструкція"),
                row("tie", "02"),
            ],
            "paper_status": "", "vault_status": "",
            "paper_scan_status": "", "order_status": "",
        }

    def ids(self, **kwargs):
        result = document_catalog.paginate_sources(
            self.snapshot, page_size=100, **kwargs
        )
        return [item["source_id"] for item in result["rows"]]

    def test_version_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.25-r5\n",
        )
        self.assertIn('APP_VERSION = "10.25-r5"', (root / "main.py").read_text("utf-8"))
        self.assertIn("Taxo 10.25-r5", (root / "START.bat").read_text("utf-8"))

    def test_natural_numeric_and_mixed_numbers(self):
        self.assertEqual(
            self.ids(number_sort="ascending"),
            ["one", "two", "tie", "a2", "other", "ten", "a10", "blank", "none"],
        )
        self.assertEqual(
            self.ids(number_sort="descending"),
            ["a10", "ten", "other", "a2", "two", "tie", "one", "blank", "none"],
        )

    def test_number_sort_is_after_filters_before_paging(self):
        page = document_catalog.paginate_sources(
            self.snapshot, number_sort="ascending",
            kind_filter="Наказ",
            source_filter="order",
            date_from="2026-11-17", date_to="2026-11-17",
            page_size=2, page=1,
        )
        self.assertEqual(page["total"], 8)
        self.assertEqual(page["pages"], 4)
        self.assertEqual(
            [item["source_id"] for item in page["rows"]],
            ["tie", "a2"],
        )

    def test_default_unchanged_and_snapshot_not_modified(self):
        before = self.ids()
        self.ids(number_sort="ascending")
        self.ids(number_sort="descending")
        self.assertEqual(before, self.ids())
        self.assertEqual(before, [r["source_id"] for r in self.snapshot["rows"]])

    def test_ui_heading_exposes_toggle_and_resets_page(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn('tree.heading("number", text="№", command=toggle_number_sort)', source)
        self.assertIn("number_sort=number_sort", source)
        self.assertIn('state["sort_field"] = "number"', source)
        self.assertIn("refresh(reset=True)", source)


if __name__ == "__main__":
    unittest.main()
