# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

import document_catalog


def _row(key, title, vault_id, count, source="vault"):
    return {
        "key": (source, key, 0),
        "source": source,
        "sources": (source,),
        "source_id": key,
        "source_label": "Сховище" if source == "vault" else "Наказ",
        "date": "2026-11-17",
        "created_at": "2026-11-17T12:00:00",
        "number": "",
        "kind": "Документ",
        "title": title,
        "person": "",
        "order_type": "",
        "revision_label": "r1" if source == "vault" else "",
        "file_state": "Незмінна копія" if source == "vault" else "Файл не прив'язаний",
        "vault_id": vault_id,
        "paper_scan_count": count,
        "paper_scan_state": (
            "Помилка перевірки"
            if count is None and vault_id
            else ("Є: %d" % count if count else ("Немає" if vault_id else "—"))
        ),
    }


class DocumentScanFilterR1Tests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            _row("with-2", "Зі сканами два", "vault-2", 2),
            _row("with-1", "Зі сканом один", "vault-1", 1),
            _row("without", "Без сканів", "vault-0", 0),
            _row("error", "Пошкоджена перевірка", "vault-error", None),
            _row("order", "Наказ без сховища", "", 0, source="order"),
        ]
        self.snapshot = {
            "rows": self.rows,
            "paper_status": "Word: 0.",
            "vault_status": "Сховище: 4.",
            "paper_scan_status": "Активні скани: 3.",
            "order_status": "Накази: 1.",
        }

    def test_r1_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.24-r9\n",
        )
        self.assertIn(
            'APP_VERSION = "10.24-r9"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.24-r9",
            (root / "START.bat").read_text("utf-8"),
        )

    def test_scan_modes_filter_full_snapshot_before_paging(self):
        present = document_catalog.paginate_sources(
            self.snapshot, page_size=1, scan_filter="present"
        )
        self.assertEqual(present["total"], 2)
        self.assertEqual(present["pages"], 2)
        self.assertEqual(present["rows"][0]["vault_id"], "vault-2")

        absent = document_catalog.paginate_sources(
            self.snapshot, scan_filter="absent"
        )
        self.assertEqual(
            [row["vault_id"] for row in absent["rows"]],
            ["vault-0"],
        )

        error = document_catalog.paginate_sources(
            self.snapshot, scan_filter="error"
        )
        self.assertEqual(
            [row["vault_id"] for row in error["rows"]],
            ["vault-error"],
        )

    def test_non_vault_and_unknown_state_are_not_called_no_scan(self):
        absent = document_catalog.paginate_sources(
            self.snapshot, scan_filter="absent"
        )
        self.assertNotIn("order", [row["source_id"] for row in absent["rows"]])
        error = document_catalog.paginate_sources(
            self.snapshot, scan_filter="error"
        )
        self.assertNotIn("order", [row["source_id"] for row in error["rows"]])

    def test_scan_filter_combines_with_text_and_source_filters(self):
        result = document_catalog.paginate_sources(
            self.snapshot,
            text_filter="один",
            source_filter="vault",
            scan_filter="present",
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["rows"][0]["vault_id"], "vault-1")
        self.assertEqual(result["paper_scan_status"], "Активні скани: 3.")

    def test_all_and_unknown_filter_keep_existing_catalog_behavior(self):
        all_rows = document_catalog.paginate_sources(
            self.snapshot, scan_filter="all"
        )
        unknown = document_catalog.paginate_sources(
            self.snapshot, scan_filter="future-value"
        )
        self.assertEqual(all_rows["total"], len(self.rows))
        self.assertEqual(unknown["total"], len(self.rows))

    def test_ui_exposes_read_only_scan_filter(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn('"Є скани": "present"', source)
        self.assertIn('"Немає сканів": "absent"', source)
        self.assertIn('"Помилка перевірки": "error"', source)
        self.assertIn("scan_filter=scan_filter", source)
        self.assertIn('win._taxo_catalog_scan_filter_box = scan_box', source)
        self.assertNotIn('text="Підписано"', source)


if __name__ == "__main__":
    unittest.main()
