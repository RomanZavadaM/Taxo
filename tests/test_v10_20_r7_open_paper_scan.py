# -*- coding: utf-8 -*-
import unittest
from pathlib import Path


class PaperScanOpenR7Tests(unittest.TestCase):
    def test_r7_identity(self):
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

    def test_open_is_explicit_and_uses_verified_scan(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "src" / "taxo" / "document_vault_paper_scans_ui.py"
        ).read_text("utf-8")
        self.assertIn("load_paper_scan(", source)
        self.assertIn("open_document(win, payload.path)", source)
        self.assertIn('text="Відкрити", state="disabled"', source)
        self.assertIn('start_background(\n            "open"', source)
        self.assertIn('elif kind == "open":', source)
        self.assertIn(
            "win._taxo_paper_scans_open = open_scan",
            source,
        )
        self.assertNotIn("system_open(", source)

    def test_open_button_depends_on_selection_and_busy_state(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "src" / "taxo" / "document_vault_paper_scans_ui.py"
        ).read_text("utf-8")
        self.assertIn("if value or not tree.selection()", source)
        self.assertIn(
            'state="disabled" if state["busy"] else "normal"',
            source,
        )

    def test_close_invalidates_pending_background_open(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "src" / "taxo" / "document_vault_paper_scans_ui.py"
        ).read_text("utf-8")
        self.assertIn('state["generation"] += 1', source)
        self.assertIn('if generation != state["generation"]', source)


if __name__ == "__main__":
    unittest.main()
