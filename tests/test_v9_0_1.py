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
        self.assertIn("Version: 9.0.1", text)
        self.assertIn("Release type: stable hotfix", text)

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
