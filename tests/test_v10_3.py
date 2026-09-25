# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

from release_naming import start_archive_stem

ROOT=Path(__file__).resolve().parents[1]


class TestTaxo103Stable(unittest.TestCase):
    def test_stable_checkpoint_identity_is_10_3(self):
        self.assertEqual(start_archive_stem("10.3"),"Taxo_v10_3_START")
        state=(ROOT/"PROJECT_STATE.md").read_text("utf-8")
        self.assertIn("**Stable:** Taxo 10.3 / `v10.3`",state)
        self.assertIn(
            "7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60",
            state,
        )

    def test_stable_release_notes_exist(self):
        text=(ROOT/"docs"/"releases"/"RELEASE_NOTES_v10_3.md").read_text("utf-8")
        self.assertIn("Taxo 10.3",text)
        self.assertIn("10.3-r6",text)

    def test_windows_installer_metadata_stays_stable_10_3(self):
        text=(ROOT/"installer"/"Taxo.iss").read_text("utf-8")
        self.assertIn('#define MyAppVersion "10.3"',text)
        self.assertIn("Taxo_v10_3_Windows_x64",text)
        self.assertIn("Roman Zavada",text)

    def test_macos_bundle_metadata_stays_stable_10_3(self):
        text=(ROOT/"Taxo_macos.spec").read_text("utf-8")
        self.assertIn("version='10.3'",text)
        self.assertIn("'CFBundleShortVersionString': '10.3'",text)


if __name__=="__main__":
    unittest.main()
