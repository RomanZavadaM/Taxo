# -*- coding: utf-8 -*-
"""10.23-r1: separate seasonal-measures category in the document catalog."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

import document_catalog


def _row(identifier, category):
    return {
        "key": ("order", identifier, 0),
        "source": "order",
        "sources": ("order",),
        "source_id": identifier,
        "source_label": "Наказ",
        "date": "2026-11-18",
        "created_at": "2026-11-18T10:00:00",
        "number": str(identifier),
        "kind": "Наказ",
        "title": "Документ " + str(identifier),
        "person": "",
        "employee_refs": (),
        "vehicle_refs": (),
        "entity_text": "",
        "order_type": "",
        "order_series": "work",
        "category": category,
        "revision_label": "",
        "file_state": "",
        "vault_id": "",
        "paper_scan_count": 0,
        "paper_scan_state": "—",
        "paper_original_state": "—",
    }


class SeasonalDocumentCategoryR6Tests(unittest.TestCase):
    def test_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.24-r10\n")
        self.assertIn('APP_VERSION = "10.24-r10"', (root / "main.py").read_text("utf-8"))
        self.assertIn("Taxo 10.24-r10", (root / "START.bat").read_text("utf-8"))

    def test_structured_seasonal_order_has_own_category(self):
        self.assertIn(document_catalog.CATEGORY_SEASONAL, document_catalog.DOCUMENT_CATEGORIES)
        self.assertEqual(document_catalog._order_category("work", "seasonal_operation"), document_catalog.CATEGORY_SEASONAL)
        self.assertEqual(document_catalog._order_category("personnel", "seasonal_operation"), document_catalog.CATEGORY_PERSONNEL)
        self.assertEqual(document_catalog._order_category("work", "generic"), document_catalog.CATEGORY_OPERATIONAL)

    def test_seasonal_category_is_available_to_filter(self):
        snapshot = {
            "rows": [_row("1", document_catalog.CATEGORY_SEASONAL), _row("2", document_catalog.CATEGORY_OPERATIONAL)],
            "paper_status": "", "vault_status": "", "paper_scan_status": "",
            "paper_original_status": "", "order_status": "",
        }
        result = document_catalog.paginate_sources(snapshot, category_filter=document_catalog.CATEGORY_SEASONAL)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["rows"][0]["source_id"], "1")
        self.assertIn(document_catalog.CATEGORY_SEASONAL, result["available_categories"])

    def test_order_reader_uses_order_type_not_subject_words(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "Data"
            data.mkdir()
            con = sqlite3.connect(data / "driver_worktime.sqlite3")
            try:
                con.executescript("""
                    CREATE TABLE operations_orders(
                        id INTEGER PRIMARY KEY, order_date TEXT, order_no TEXT,
                        order_type TEXT, subject TEXT, order_series TEXT, created_at TEXT
                    );
                """)
                con.executemany(
                    """INSERT INTO operations_orders(
                        id,order_date,order_no,order_type,subject,order_series,created_at
                    ) VALUES(?,?,?,?,?,?,?)""",
                    [
                        (1,"2026-11-18","1","seasonal_operation","Зимова підготовка","work","2026-11-18T08:00:00"),
                        (2,"2026-11-18","2","generic","Сезонні заходи лише у тексті","work","2026-11-18T09:00:00"),
                        (3,"2026-11-18","3","seasonal_operation","Кадровий наказ","personnel","2026-11-18T10:00:00"),
                    ],
                )
                con.commit()
            finally:
                con.close()
            rows, status = document_catalog._read_orders(root)
        by_id = {item["source_id"]: item for item in rows}
        self.assertEqual(by_id[1]["category"], document_catalog.CATEGORY_SEASONAL)
        self.assertEqual(by_id[2]["category"], document_catalog.CATEGORY_OPERATIONAL)
        self.assertEqual(by_id[3]["category"], document_catalog.CATEGORY_PERSONNEL)
        self.assertEqual(status, "Накази: 3.")


if __name__ == "__main__":
    unittest.main()
