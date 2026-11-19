# -*- coding: utf-8 -*-
"""10.22-r9: structured category navigation in the unified document catalog."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

import document_catalog


def row(identifier, category, *, source="order", kind="Наказ", scans=0):
    return {
        "key": (source, identifier, 0),
        "source": source,
        "sources": (source,),
        "source_id": identifier,
        "source_label": "Наказ" if source == "order" else "Сховище",
        "date": "2026-11-18",
        "created_at": "2026-11-18T10:00:00",
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


class DocumentCategoryR10Tests(unittest.TestCase):
    def test_r10_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.22-r9\n",
        )
        self.assertIn(
            'APP_VERSION = "10.22-r9"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.22-r9",
            (root / "START.bat").read_text("utf-8"),
        )

    def snapshot(self):
        return {
            "rows": [
                row("1", document_catalog.CATEGORY_PERSONNEL),
                row("2", document_catalog.CATEGORY_OPERATIONAL),
                row("3", document_catalog.CATEGORY_OCCUPATIONAL_SAFETY),
                row("4", document_catalog.CATEGORY_ROAD_SAFETY),
                row("5", document_catalog.CATEGORY_FIRE_SAFETY),
                row("6", document_catalog.CATEGORY_SEASONAL),
                row("v1", document_catalog.CATEGORY_UNCLASSIFIED,
                    source="vault", kind="Інструкція", scans=1),
            ],
            "paper_status": "",
            "vault_status": "",
            "paper_scan_status": "",
            "order_status": "",
        }

    def test_personnel_series_wins_without_free_text_guessing(self):
        self.assertEqual(
            document_catalog._order_category("personnel", "road_safety"),
            document_catalog.CATEGORY_PERSONNEL,
        )
        self.assertEqual(
            document_catalog._order_category("work", "generic"),
            document_catalog.CATEGORY_OPERATIONAL,
        )

    def test_explicit_safety_types_have_stable_categories(self):
        self.assertEqual(
            document_catalog._order_category("work", "road_safety"),
            document_catalog.CATEGORY_ROAD_SAFETY,
        )
        self.assertEqual(
            document_catalog._order_category("work", "accident_commission"),
            document_catalog.CATEGORY_ROAD_SAFETY,
        )
        self.assertEqual(
            document_catalog._order_category("work", "occupational_safety"),
            document_catalog.CATEGORY_OCCUPATIONAL_SAFETY,
        )
        self.assertEqual(
            document_catalog._order_category("work", "safety_training"),
            document_catalog.CATEGORY_OCCUPATIONAL_SAFETY,
        )
        self.assertEqual(
            document_catalog._order_category("work", "fire_safety"),
            document_catalog.CATEGORY_FIRE_SAFETY,
        )

    def test_category_filter_applies_before_paging(self):
        result = document_catalog.paginate_sources(
            self.snapshot(),
            category_filter=document_catalog.CATEGORY_ROAD_SAFETY,
            page_size=1,
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["pages"], 1)
        self.assertEqual(
            result["rows"][0]["category"],
            document_catalog.CATEGORY_ROAD_SAFETY,
        )

    def test_category_combines_with_existing_filters(self):
        result = document_catalog.paginate_sources(
            self.snapshot(),
            source_filter="vault",
            scan_filter="present",
            kind_filter="Інструкція",
            date_from="2026-11-18",
            date_to="2026-11-18",
            category_filter=document_catalog.CATEGORY_UNCLASSIFIED,
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["rows"][0]["source_id"], "v1")

    def test_missing_legacy_category_is_explicitly_unclassified(self):
        snapshot = self.snapshot()
        legacy = row("legacy", document_catalog.CATEGORY_OPERATIONAL)
        legacy.pop("category")
        snapshot["rows"] = [legacy]
        result = document_catalog.paginate_sources(
            snapshot,
            category_filter=document_catalog.CATEGORY_UNCLASSIFIED,
        )
        self.assertEqual(result["total"], 1)

    def test_available_categories_are_user_facing_and_stable(self):
        result = document_catalog.paginate_sources(self.snapshot())
        self.assertEqual(
            result["available_categories"],
            document_catalog.DOCUMENT_CATEGORIES,
        )

    def test_category_is_part_of_text_search(self):
        result = document_catalog.paginate_sources(
            self.snapshot(), text_filter="БДР"
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["rows"][0]["source_id"], "4")

    def test_order_reader_uses_series_and_type_not_subject_words(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "Data"
            data.mkdir()
            db = data / "driver_worktime.sqlite3"
            con = sqlite3.connect(db)
            try:
                con.executescript(
                    """
                    CREATE TABLE operations_orders(
                        id INTEGER PRIMARY KEY,
                        order_date TEXT,
                        order_no TEXT,
                        order_type TEXT,
                        subject TEXT,
                        order_series TEXT,
                        created_at TEXT
                    );
                    """
                )
                con.executemany(
                    """INSERT INTO operations_orders(
                        id,order_date,order_no,order_type,subject,
                        order_series,created_at
                    ) VALUES(?,?,?,?,?,?,?)""",
                    [
                        (1,"2026-11-18","1","generic",
                         "Про охорону праці у тексті","personnel",
                         "2026-11-18T08:00:00"),
                        (2,"2026-11-18","2","road_safety",
                         "Звичайна тема","work",
                         "2026-11-18T09:00:00"),
                        (3,"2026-11-18","3","generic",
                         "Про БДР лише у вільному тексті","work",
                         "2026-11-18T10:00:00"),
                    ],
                )
                con.commit()
            finally:
                con.close()
            rows, status = document_catalog._read_orders(root)
        by_id = {item["source_id"]: item for item in rows}
        self.assertEqual(by_id[1]["category"], document_catalog.CATEGORY_PERSONNEL)
        self.assertEqual(by_id[2]["category"], document_catalog.CATEGORY_ROAD_SAFETY)
        self.assertEqual(by_id[3]["category"], document_catalog.CATEGORY_OPERATIONAL)
        self.assertEqual(status, "Накази: 3.")

    def test_ui_exposes_category_column_and_filter(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn('text="Категорія:"', source)
        self.assertIn('("category", "Категорія", 145)', source)
        self.assertIn("category_filter=(", source)
        self.assertIn("win._taxo_catalog_category_filter_box", source)


if __name__ == "__main__":
    unittest.main()
