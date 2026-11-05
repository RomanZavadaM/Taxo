# -*- coding: utf-8 -*-
"""Taxo 10.10-r5 — macOS personnel navigation startup regression."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestMacPersonnelNavigationR5(unittest.TestCase):
    def test_revision_identity_is_r5(self):
        self.assertEqual((ROOT / "VERSION.txt").read_text("utf-8").strip(), "Version: 10.10-r5")
        self.assertIn('APP_VERSION = "10.10-r5"', (ROOT / "main.py").read_text("utf-8"))

    def test_personnel_navigation_supports_widget_without_command(self):
        source = (ROOT / "src" / "taxo" / "personnel_v91.py").read_text("utf-8")
        self.assertIn('if "command" in personnel_button.keys():', source)
        self.assertIn('personnel_button.configure(command=self.show_personnel_overview)', source)
        self.assertIn('personnel_button.bind(', source)
        self.assertIn('"<Button-1>"', source)
        self.assertIn('lambda _event: self.show_personnel_overview()', source)


if __name__ == "__main__":
    unittest.main()
