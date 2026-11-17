# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

import document_catalog


def _row(key, kind, day="2026-11-17", source="vault", scan_count=0):
    return {
        "key": (source, key, 0),
        "source": source,
        "sources": (source,),
        "source_id": key,
        "source_label": "Сховище" if source == "vault" else "Наказ",
        "date": day,
        "created_at": day + "T12:00:00",
        "number": "1" if source == "order" else "",
        "kind": kind,
        "title": "Тест " + kind,
        "person": "",
        "order_type": "road_safety" if source == "order" else "",
        "revision_label": "r1" if source == "vault" else "",
        "file_state": "Незмінна копія" if source == "vault" else "Файл не прив'язаний",
        "vault_id": key if source == "vault" else "",
        "paper_scan_count": scan_count if source == "vault" else 0,
        "paper_scan_state": (
            "Є: %d" % scan_count
            if scan_count
            else ("Немає" if source == "vault" else "—")
        ),
    }


class DocumentTypeFilterR3Tests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            "rows": [
                _row("instruction", "Інструкція", scan_count=1),
                _row("act", "Акт"),
                _row("order", "Наказ", source="order"),
                _row("instruction-2", "Інструкція", day="2026-11-16"),
            ],
            "paper_status": "Word: 0.",
            "vault_status": "Сховище: 3.",
            "paper_scan_status": "Активні скани: 1.",
            "order_status": "Накази: 1.",
        }

    def test_r3_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.21-r5\n",
        )
        self.assertIn(
            'APP_VERSION = "10.21-r5"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.21-r5",
            (root / "START.bat").read_text("utf-8"),
        )

    def test_exact_type_filter_applies_before_paging(self):
        result = document_catalog.paginate_sources(
            self.snapshot,
            page_size=1,
            kind_filter="Інструкція",
        )
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["pages"], 2)
        self.assertEqual(result["rows"][0]["kind"], "Інструкція")

    def test_type_filter_combines_with_existing_filters(self):
        result = document_catalog.paginate_sources(
            self.snapshot,
            text_filter="тест інструкція",
            source_filter="vault",
            scan_filter="present",
            date_from="2026-11-17",
            date_to="2026-11-17",
            kind_filter="Інструкція",
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["rows"][0]["source_id"], "instruction")

    def test_available_types_come_from_full_snapshot(self):
        result = document_catalog.paginate_sources(
            self.snapshot,
            kind_filter="Наказ",
        )
        self.assertEqual(
            set(result["available_kinds"]),
            {"Акт", "Інструкція", "Наказ"},
        )

    def test_unknown_type_is_an_empty_read_only_view(self):
        result = document_catalog.paginate_sources(
            self.snapshot,
            kind_filter="Неіснуючий тип",
        )
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["rows"], [])

    def test_ui_exposes_readonly_type_filter(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn('text="Тип:"', source)
        self.assertIn('all_kinds_label = "Усі типи"', source)
        self.assertIn("kind_filter=(", source)
        self.assertIn("win._taxo_catalog_kind_filter_box", source)


if __name__ == "__main__":
    unittest.main()
