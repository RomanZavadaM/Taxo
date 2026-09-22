# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file


ROOT=Path(__file__).resolve().parents[1]


class TestTaxo102R7Packaging(unittest.TestCase):
    def test_r7_checkpoint_is_not_reused_by_later_revisions(self):
        self.assertEqual(version_from_file(ROOT/"VERSION.txt"),main.APP_VERSION)
        self.assertEqual(
            start_archive_stem("10.2-r7"),
            "Taxo_v10_2_candidate_r7_START",
        )

    def test_start_archive_name_is_exact(self):
        self.assertEqual(
            start_archive_stem("10.2-r7"),
            "Taxo_v10_2_candidate_r7_START",
        )

    def test_r7_publisher_uses_10_2_name_everywhere(self):
        text=(ROOT/".github/workflows/publish-v10.2-r7-source.yml").read_text("utf-8")
        self.assertIn("Taxo_v10_2_candidate_r7_START",text)
        self.assertIn("SHA256SUMS_v10_2_r7.txt",text)
        self.assertIn("refs/tags/v10.2-r7",text)
        self.assertNotIn("Taxo_v10_1_candidate_r7_START",text)

    def test_r6_bad_asset_name_is_documented_not_reused(self):
        old=(ROOT/".github/workflows/publish-v10.2-r6-source.yml").read_text("utf-8")
        self.assertIn("Taxo_v10_1_candidate_r6_START",old)
        self.assertNotEqual(
            start_archive_stem("10.2-r7"),
            "Taxo_v10_1_candidate_r6_START",
        )


if __name__=="__main__":
    unittest.main()
