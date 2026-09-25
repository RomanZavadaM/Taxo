# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file

ROOT=Path(__file__).resolve().parents[1]


class TestTaxo103R9MainCheckpoint(unittest.TestCase):
    def test_candidate_identity_is_r9(self):
        self.assertEqual(main.APP_VERSION,"10.3-r9")
        self.assertEqual(main.APP_VERSION,version_from_file(ROOT/"VERSION.txt"))
        self.assertEqual(
            start_archive_stem("10.3-r9"),
            "Taxo_v10_3_candidate_r9_START",
        )

    def test_windows_candidate_installer_metadata(self):
        text=(ROOT/"installer"/"Taxo_v10_3_r9.iss").read_text("utf-8")
        self.assertIn('#define MyAppVersion "10.3-r9"',text)
        self.assertIn("Taxo_v10_3_candidate_r9_Setup_Windows_x64",text)
        self.assertIn("Roman Zavada",text)
        self.assertIn("Copyright (C) 2026 Roman Zavada",text)

    def test_macos_candidate_bundle_metadata(self):
        text=(ROOT/"Taxo_macos_v10_3_r9.spec").read_text("utf-8")
        self.assertIn("version='10.3.9'",text)
        self.assertIn("'CFBundleShortVersionString': '10.3'",text)
        self.assertIn("'CFBundleVersion': '9'",text)

    def test_executable_specs_include_legal_notices(self):
        win=(ROOT/"Taxo.spec").read_text("utf-8")
        mac=(ROOT/"Taxo_macos_v10_3_r9.spec").read_text("utf-8")
        for name in ("LICENSE.md","COPYRIGHT.md","THIRD_PARTY_NOTICES.md"):
            self.assertIn(name,win)
            self.assertIn(name,mac)

    def test_r9_is_packaging_checkpoint_not_business_model_change(self):
        notes=(ROOT/"docs"/"releases"/"RELEASE_NOTES_v10_3_r9.md").read_text("utf-8")
        self.assertIn("без нової бізнес-логіки",notes)
        self.assertIn("Windows",notes)
        self.assertIn("macOS",notes)


if __name__=="__main__":
    unittest.main()
