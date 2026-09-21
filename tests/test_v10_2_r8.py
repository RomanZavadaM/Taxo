# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import next_candidate_version, start_archive_stem, version_from_file


ROOT = Path(__file__).resolve().parents[1]


class TestTaxo102R8ReleaseSafety(unittest.TestCase):
    def test_version_is_r8_everywhere(self):
        self.assertEqual(main.APP_VERSION, "10.2-r8")
        self.assertEqual(version_from_file(ROOT / "VERSION.txt"), "10.2-r8")

    def test_r8_has_unique_start_archive_name(self):
        self.assertEqual(
            start_archive_stem("10.2-r8"),
            "Taxo_v10_2_candidate_r8_START",
        )
        self.assertNotEqual(
            start_archive_stem("10.2-r8"),
            start_archive_stem("10.2-r7"),
        )

    def test_next_revision_after_r8_is_r9(self):
        self.assertEqual(next_candidate_version("10.2-r8"), "10.2-r9")

    def test_canonical_rules_exist(self):
        rules = (ROOT / "PROJECT_RULES.md").read_text("utf-8")
        self.assertIn("старий архів не видавати повторно", rules)
        self.assertIn("перед тим як дати посилання користувачу", rules)

    def test_required_windows_check_tracks_rule_files(self):
        workflow = (ROOT / ".github/workflows/build-windows-v8.70.yml").read_text("utf-8")
        self.assertIn("'PROJECT_RULES.md'", workflow)
        self.assertIn("'PROJECT_STATE.md'", workflow)
        self.assertIn("'docs/maintenance/DEVELOPMENT_RULES.md'", workflow)


if __name__ == "__main__":
    unittest.main()
