# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file

ROOT=Path(__file__).resolve().parents[1]

class TestTaxo103Stable(unittest.TestCase):
    def test_stable_version_is_10_3(self):
        self.assertEqual(main.APP_VERSION,"10.3")
        self.assertEqual(version_from_file(ROOT/"VERSION.txt"),"10.3")
        self.assertEqual(start_archive_stem("10.3"),"Taxo_v10_3_START")

    def test_stable_metadata(self):
        text=(ROOT/"VERSION.txt").read_text("utf-8")
        self.assertIn("Release type: stable",text)
        self.assertIn("Verified candidate: Taxo 10.3-r6",text)

    def test_windows_installer_metadata(self):
        text=(ROOT/"installer"/"Taxo.iss").read_text("utf-8")
        self.assertIn('#define MyAppVersion "10.3"',text)
        self.assertIn("Taxo_v10_3_Windows_x64",text)
        self.assertIn("Roman Zavada",text)

    def test_macos_bundle_metadata(self):
        text=(ROOT/"Taxo_macos.spec").read_text("utf-8")
        self.assertIn("version='10.3'",text)
        self.assertIn("'CFBundleShortVersionString': '10.3'",text)

if __name__=="__main__":
    unittest.main()
