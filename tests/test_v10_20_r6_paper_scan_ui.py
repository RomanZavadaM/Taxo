# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

from document_vault_paper_scans_ui import _size_label


class PaperScanUiR6Tests(unittest.TestCase):
    def test_version_identity_and_package_guard(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.20-r6\n",
        )
        self.assertIn(
            'APP_VERSION = "10.20-r6"',
            (root / "main.py").read_text("utf-8"),
        )
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn("Taxo 10.20-r6", start)
        self.assertIn("document_vault_paper_scans_ui.py", start)

    def test_scan_dialog_is_background_and_read_only_listing(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "src" / "taxo" / "document_vault_paper_scans_ui.py"
        ).read_text("utf-8")
        self.assertIn("threading.Thread(", source)
        self.assertIn("register_paper_scan(", source)
        self.assertIn("list_paper_scans(", source)
        self.assertIn("askopenfilename(", source)
        self.assertIn("Додати скан…", source)
        self.assertIn("не означає, що документ підписано", source)
        self.assertNotIn("signed =", source)
        self.assertNotIn("document_status =", source)

    def test_catalog_exposes_scan_action_only_for_vault_document(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn(
            "from document_vault_paper_scans_ui import open_paper_scans_dialog",
            source,
        )
        self.assertIn('text="Скани…"', source)
        self.assertIn('if row and row.get("vault_id")', source)
        self.assertIn("open_paper_scans_dialog(", source)
        self.assertIn(
            "win._taxo_catalog_paper_scans = manage_paper_scans",
            source,
        )

    def test_human_readable_sizes(self):
        self.assertEqual(_size_label(12), "12 B")
        self.assertEqual(_size_label(2048), "2.0 KB")
        self.assertEqual(_size_label(3 * 1024 * 1024), "3.0 MB")


if __name__ == "__main__":
    unittest.main()
