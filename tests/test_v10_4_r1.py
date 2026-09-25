# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file

ROOT = Path(__file__).resolve().parents[1]


class TestTaxo104R1FullCheckpoint(unittest.TestCase):
    def test_candidate_identity_is_10_4_r1(self):
        self.assertEqual(main.APP_VERSION, "10.4-r1")
        self.assertEqual(main.APP_VERSION, version_from_file(ROOT / "VERSION.txt"))
        self.assertEqual(
            start_archive_stem("10.4-r1"),
            "Taxo_v10_4_candidate_r1_START",
        )

    def test_modern_windows_installer_identity(self):
        text=(ROOT/"installer"/"Taxo_v10_4_r1.iss").read_text("utf-8")
        self.assertIn('#define MyAppVersion "10.4-r1"', text)
        self.assertIn("Taxo_v10_4_candidate_r1_Setup_Windows_x64", text)

    def test_windows7_installer_identity_and_minimum(self):
        text=(ROOT/"installer"/"Taxo_v10_4_r1_win7.iss").read_text("utf-8")
        self.assertIn('#define MyAppVersion "10.4-r1"', text)
        self.assertIn("MinVersion=6.1sp1", text)
        self.assertIn("Taxo_v10_4_candidate_r1_Setup_Windows7_x64", text)

    def test_macos_bundle_identity(self):
        text=(ROOT/"Taxo_macos_v10_4_r1.spec").read_text("utf-8")
        self.assertIn("version='10.4.1'", text)
        self.assertIn("'CFBundleShortVersionString': '10.4'", text)
        self.assertIn("'CFBundleVersion': '1'", text)

    def test_release_notes_include_windows7_and_full_platform_set(self):
        text=(ROOT/"docs"/"releases"/"RELEASE_NOTES_v10_4_r1.md").read_text("utf-8")
        self.assertIn("Windows 7 SP1 x64 Portable", text)
        self.assertIn("macOS ARM64", text)
        self.assertIn("macOS Intel x86_64", text)
        self.assertIn("api-ms-win-core-path-l1-1-0.dll", text)


if __name__ == "__main__":
    unittest.main()
