# -*- coding: utf-8 -*-
"""Regression for full-catalog date sorting before pagination."""
import unittest
from pathlib import Path

import document_catalog


def row(key, day, title, source="vault", scans=0):
    return {
        "key": (source, key, 0),
        "source": source,
        "sources": (source,),
        "source_id": key,
        "source_label": "Наказ" if source == "order" else "Сховище",
        "date": day,
        "created_at": (day + "T10:00:00") if day else "",
        "number": "",
        "kind": "Наказ" if source == "order" else "Акт",
        "title": title,
        "person": "",
        "order_type": "",
        "revision_label": "",
        "file_state": "",
        "vault_id": key if source == "vault" else "",
        "paper_scan_count": scans,
        "paper_scan_state": "Є: %d" % scans if scans else "Немає",
    }


class DocumentDateSortR4Tests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            "rows": [
                row("invalid", "не-дата", "Пошкоджена"),
                row("late", "2026-11-17", "Пізня", scans=1),
                row("missing", "", "Без дати"),
                row("early", "2025-03-01", "Рання", scans=1),
                row("middle", "2026-05-01", "Середня", scans=1),
                row("order", "2026-01-01", "Наказ", source="order"),
                row("same", "2026-05-01", "Середня друга", scans=1),
            ],
            "paper_status": "",
            "vault_status": "",
            "paper_scan_status": "",
            "order_status": "",
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
            "Version: 10.24-r7\n",
        )
        self.assertIn(
            'APP_VERSION = "10.24-r7"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.24-r7",
            (root / "START.bat").read_text("utf-8"),
        )

    def test_both_directions_put_bad_dates_last(self):
        self.assertEqual(
            self.ids(date_sort="newest"),
            ["late", "middle", "same", "order", "early", "invalid", "missing"],
        )
        self.assertEqual(
            self.ids(date_sort="oldest"),
            ["early", "order", "middle", "same", "late", "invalid", "missing"],
        )

    def test_sort_filters_full_result_before_pagination(self):
        page = document_catalog.paginate_sources(
            self.snapshot,
            date_sort="oldest",
            source_filter="vault",
            scan_filter="present",
            kind_filter="Акт",
            date_from="2026-01-01",
            page_size=1,
            page=1,
        )
        self.assertEqual(page["total"], 3)
        self.assertEqual(page["pages"], 3)
        # Same-day ties retain the pre-existing source-specific order.
        self.assertEqual(page["rows"][0]["source_id"], "middle")

    def test_default_path_keeps_legacy_snapshot_order(self):
        self.assertEqual(
            self.ids(),
            ["invalid", "late", "missing", "early", "middle", "order", "same"],
        )

    def test_sort_never_modifies_snapshot(self):
        before = [item["source_id"] for item in self.snapshot["rows"]]
        self.ids(date_sort="oldest")
        self.ids(date_sort="newest")
        self.assertEqual(
            [item["source_id"] for item in self.snapshot["rows"]], before
        )

    def test_ui_heading_toggles_and_resets_pagination(self):
        root = Path(__file__).resolve().parents[1]
        code = (
            root / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn('tree.heading("date", text="Дата ▼", command=toggle_date_sort)', code)
        self.assertIn('"oldest" if state["date_sort"] == "newest" else "newest"', code)
        self.assertIn("date_sort=date_sort", code)
        self.assertIn("refresh(reset=True)", code)


if __name__ == "__main__":
    unittest.main()
