# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

import document_catalog


def _row(key, day, title, source="vault", vault_id="vault", scan_count=0):
    return {
        "key": (source, key, 0),
        "source": source,
        "sources": (source,),
        "source_id": key,
        "source_label": "Сховище" if source == "vault" else "Наказ",
        "date": day,
        "created_at": day + "T12:00:00" if day else "",
        "number": "",
        "kind": "Документ",
        "title": title,
        "person": "",
        "order_type": "",
        "revision_label": "r1" if source == "vault" else "",
        "file_state": "Незмінна копія" if source == "vault" else "Файл не прив'язаний",
        "vault_id": vault_id if source == "vault" else "",
        "paper_scan_count": scan_count if source == "vault" else 0,
        "paper_scan_state": "Є: %d" % scan_count if scan_count else ("Немає" if source == "vault" else "—"),
    }


class DocumentDateFilterR2Tests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            _row("old", "2026-01-01", "Старий"),
            _row("from", "2026-02-01", "Від межі", scan_count=1),
            _row("middle", "2026-02-15", "Середина", scan_count=1),
            _row("to", "2026-02-28", "До межі"),
            _row("new", "2026-03-01", "Новий"),
            _row("unknown", "", "Без дати"),
            _row("broken", "не-дата", "Пошкоджена дата"),
            _row("order", "2026-02-20", "Наказ", source="order"),
        ]
        self.snapshot = {
            "rows": self.rows,
            "paper_status": "Word: 0.",
            "vault_status": "Сховище: 7.",
            "paper_scan_status": "Активні скани: 2.",
            "order_status": "Накази: 1.",
        }

    def test_r2_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.24-r5\n",
        )
        self.assertIn(
            'APP_VERSION = "10.24-r5"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.24-r5",
            (root / "START.bat").read_text("utf-8"),
        )

    def test_period_is_inclusive_and_filters_before_paging(self):
        result = document_catalog.paginate_sources(
            self.snapshot,
            page_size=2,
            date_from="2026-02-01",
            date_to="2026-02-28",
        )
        self.assertEqual(result["total"], 4)
        self.assertEqual(result["pages"], 2)
        self.assertEqual(
            [row["source_id"] for row in result["rows"]],
            ["from", "middle"],
        )

    def test_period_combines_with_text_source_and_scan_filters(self):
        result = document_catalog.paginate_sources(
            self.snapshot,
            text_filter="середина",
            source_filter="vault",
            scan_filter="present",
            date_from="2026-02-01",
            date_to="2026-02-28",
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["rows"][0]["source_id"], "middle")

    def test_unknown_or_malformed_row_dates_are_excluded_only_when_period_active(self):
        active = document_catalog.paginate_sources(
            self.snapshot, date_from="2026-01-01"
        )
        ids = [row["source_id"] for row in active["rows"]]
        self.assertNotIn("unknown", ids)
        self.assertNotIn("broken", ids)

        unchanged = document_catalog.paginate_sources(self.snapshot)
        self.assertIn("unknown", [row["source_id"] for row in unchanged["rows"]])
        self.assertIn("broken", [row["source_id"] for row in unchanged["rows"]])

    def test_invalid_bounds_are_explicit(self):
        with self.assertRaisesRegex(ValueError, "РРРР-ММ-ДД"):
            document_catalog.paginate_sources(
                self.snapshot, date_from="17.11.2026"
            )
        with self.assertRaisesRegex(ValueError, "не може бути пізніше"):
            document_catalog.paginate_sources(
                self.snapshot,
                date_from="2026-03-01",
                date_to="2026-02-01",
            )

    def test_ui_exposes_period_controls_and_passes_both_bounds(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn('text="Від:"', source)
        self.assertIn('text="До:"', source)
        self.assertIn("date_from=date_from_filter", source)
        self.assertIn("date_to=date_to_filter", source)
        self.assertIn("win._taxo_catalog_date_from_entry", source)
        self.assertIn("win._taxo_catalog_date_to_entry", source)


if __name__ == "__main__":
    unittest.main()
