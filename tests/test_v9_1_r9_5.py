from pathlib import Path
import unittest

from release_naming import start_archive_stem


ROOT = Path(__file__).resolve().parents[1]


class TestR95StartPackage(unittest.TestCase):
    def test_candidate_revision_with_dot_keeps_full_revision(self):
        self.assertEqual(
            start_archive_stem("9.1 candidate r9.5"),
            "Taxo_v9_1_candidate_r9_5_START",
        )
        self.assertEqual(
            start_archive_stem("9.1 candidate r9.4"),
            "Taxo_v9_1_candidate_r9_4_START",
        )

    def test_stable_archive_name_is_unchanged(self):
        self.assertEqual(start_archive_stem("9.0.1"), "Taxo_v9_0_1_START")

    def test_start_bat_checks_package_before_pip(self):
        text = (ROOT / "START.bat").read_text(encoding="utf-8")
        guard = text.index('if not exist "requirements.txt" goto :package_incomplete')
        pip = text.index("pip install -r requirements.txt")
        self.assertLess(guard, pip)
        self.assertIn('if not exist "taxo_app.py" goto :package_incomplete', text)
        self.assertIn(":package_incomplete", text)
        self.assertIn("ZIP", text)

    def test_start_package_readme_exists(self):
        self.assertTrue((ROOT / "00_README_START.txt").is_file())


if __name__ == "__main__":
    unittest.main()
