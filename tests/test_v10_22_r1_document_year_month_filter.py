# -*- coding: utf-8 -*-
"""10.22-r1: quick year/month navigation in the unified document catalog."""
from __future__ import annotations

import unittest
from pathlib import Path

import document_catalog


def row(identifier, day, *, source="order", category="Експлуатаційні", kind="Наказ", scans=0):
    return {
        "key": (source, identifier, 0),
        "source": source,
        "sources": (source,),
        "source_id": identifier,
        "source_label": "Наказ" if source == "order" else "Сховище",
        "date": day,
        "created_at": (day + "T10:00:00") if day and day[:4].isdigit() else "",
        "number": str(identifier) if source == "order" else "",
        "kind": kind,
        "title": "Документ " + str(identifier),
        "person": "",
        "order_type": "",
        "order_series": "",
        "category": category,
        "revision_label": "",
        "file_state": "",
        "vault_id": str(identifier) if source == "vault" else "",
        "paper_scan_count": scans if source == "vault" else 0,
        "paper_scan_state": (
            "Є: %d" % scans if scans
            else ("Немає" if source == "vault" else "—")
        ),
    }


class DocumentYearMonthR1Tests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            "rows": [
                row("2026-11-a", "2026-11-18"),
                row("2026-11-b", "2026-11-01", category="БДР"),
                row("2026-10", "2026-10-12"),
                row("2025-11", "2025-11-07", source="vault", kind="Інструкція", scans=1),
                row("2024-02", "2024-02-29"),
                row("invalid", "не-дата"),
                row("missing", ""),
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

    def test_available_years_are_real_dates_only_newest_first(self):
        result = document_catalog.paginate_sources(self.snapshot)
        self.assertEqual(result["available_years"], (2026, 2025, 2024))

    def test_available_months_follow_selected_year(self):
        all_months = document_catalog.paginate_sources(self.snapshot)
        self.assertEqual(all_months["available_months"], (2, 10, 11))
        year = document_catalog.paginate_sources(
            self.snapshot, year_filter="2026"
        )
        self.assertEqual(year["available_months"], (10, 11))

    def test_year_filter_applies_before_pagination(self):
        result = document_catalog.paginate_sources(
            self.snapshot, year_filter="2026", page_size=1
        )
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["pages"], 3)
        self.assertTrue(all(row["date"].startswith("2026-") for row in result["rows"]))

    def test_year_and_month_select_exact_calendar_slice(self):
        self.assertEqual(
            self.ids(year_filter="2026", month_filter="11"),
            ["2026-11-a", "2026-11-b"],
        )

    def test_month_without_year_is_supported_across_years(self):
        self.assertEqual(
            self.ids(month_filter="11"),
            ["2026-11-a", "2026-11-b", "2025-11"],
        )

    def test_year_month_combines_with_existing_filters(self):
        result = document_catalog.paginate_sources(
            self.snapshot,
            year_filter="2025",
            month_filter="11",
            source_filter="vault",
            scan_filter="present",
            kind_filter="Інструкція",
            category_filter="Експлуатаційні",
            date_from="2025-01-01",
            date_to="2025-12-31",
            text_filter="2025-11",
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["rows"][0]["source_id"], "2025-11")

    def test_invalid_or_missing_dates_remain_visible_without_calendar_filter(self):
        self.assertIn("invalid", self.ids())
        self.assertIn("missing", self.ids())

    def test_invalid_or_missing_dates_do_not_match_calendar_filter(self):
        filtered = self.ids(year_filter="2026")
        self.assertNotIn("invalid", filtered)
        self.assertNotIn("missing", filtered)

    def test_domain_never_mutates_snapshot(self):
        before = [item["source_id"] for item in self.snapshot["rows"]]
        self.ids(year_filter="2026", month_filter="11")
        self.assertEqual(
            [item["source_id"] for item in self.snapshot["rows"]], before
        )

    def test_ui_exposes_year_and_month_controls(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn('text="Рік / місяць:"', source)
        self.assertIn('all_years_label = "Усі роки"', source)
        self.assertIn('all_months_label = "Усі місяці"', source)
        self.assertIn("year_filter=(", source)
        self.assertIn("month_filter=(", source)
        self.assertIn("month_choice.set(all_months_label)", source)
        self.assertIn("win._taxo_catalog_year_filter_box", source)
        self.assertIn("win._taxo_catalog_month_filter_box", source)


if __name__ == "__main__":
    unittest.main()
