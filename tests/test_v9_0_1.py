import unittest
from pathlib import Path

import hotfix_901


ROOT = Path(__file__).resolve().parents[1]


class Taxo901HotfixTests(unittest.TestCase):
    def test_version_labels_are_current(self):
        self.assertEqual(hotfix_901.APP_VERSION, "9.0.1")
        self.assertIn("Taxo 9.0.1", hotfix_901.WINDOW_TITLE)
        self.assertEqual(hotfix_901.ABOUT_TITLE, "Taxo 9.0.1")
        self.assertIn("стабільне експлуатаційне виправлення", hotfix_901.ABOUT_TEXT)

    def test_version_file_marks_901(self):
        text = (ROOT / "VERSION.txt").read_text(encoding="utf-8")
        self.assertTrue(
            "Version: 9.0.1" in text
            or "Baseline: Taxo 9.0.1" in text
            or "Previous stable / rollback point: Taxo 9.0.1" in text
            or "Current stable / rollback point: Taxo 10.0" in text
        )
        release_type = next(
            line for line in text.splitlines() if line.startswith("Release type:")
        ).lower()
        if "Version: 9.0.1" in text:
            self.assertIn("stable hotfix", release_type)
        elif "Version: 10.0" in text:
            self.assertEqual(release_type, "release type: stable")
        else:
            self.assertIn("candidate", release_type)
            self.assertIn("pre-release", release_type)

    def test_operational_root_has_no_legacy_v8_report_clutter(self):
        forbidden_prefixes = (
            "CHECKPOINT_v8",
            "TEST_REPORT_v8",
            "PUBLISH_STATUS_v8",
            "PATCH_v8",
        )
        names = [path.name for path in ROOT.iterdir() if path.is_file()]
        leftovers = [name for name in names if name.startswith(forbidden_prefixes)]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
