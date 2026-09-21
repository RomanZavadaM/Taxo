from pathlib import Path
import unittest

from release_naming import start_archive_stem


ROOT = Path(__file__).resolve().parents[1]


class TestR96StartHardening(unittest.TestCase):
    def test_candidate_archive_name(self):
        self.assertEqual(
            start_archive_stem("9.1 candidate r9.6"),
            "Taxo_v9_1_candidate_r9_6_START",
        )

    def test_candidate_archive_name_can_include_unique_build_id(self):
        self.assertEqual(
            start_archive_stem("10.2-r1", build_id="9401f959"),
            "Taxo_v10_2_candidate_r1_9401f959_START",
        )
        self.assertEqual(
            start_archive_stem("10.2-r1"),
            "Taxo_v10_2_candidate_r1_START",
        )

    def test_start_bat_is_ascii_only_and_has_no_codepage_switch(self):
        raw = (ROOT / "START.bat").read_bytes()
        self.assertTrue(raw)
        self.assertTrue(all(byte < 128 for byte in raw))
        self.assertNotIn(b"chcp", raw.lower())
        self.assertIn(b"\r\n", raw)

    def test_start_bat_has_complete_and_incomplete_preflight_paths(self):
        text = (ROOT / "START.bat").read_text(encoding="ascii")
        self.assertIn('if not exist "requirements.txt" goto :package_incomplete', text)
        self.assertIn('if not exist "taxo_app.py" goto :package_incomplete', text)
        self.assertIn('TAXO_START_PREFLIGHT_ONLY', text)
        self.assertIn('START preflight OK.', text)
        self.assertIn(':package_incomplete', text)
        self.assertIn('Extract the ZIP completely before running START.bat.', text)

    def test_package_guard_still_precedes_python_and_pip(self):
        text = (ROOT / "START.bat").read_text(encoding="ascii")
        guard = text.index('if not exist "requirements.txt" goto :package_incomplete')
        python_check = text.index('py -3.13 -c "import sys"')
        pip = text.index('pip install -r')
        self.assertLess(guard, python_check)
        self.assertLess(python_check, pip)


if __name__ == "__main__":
    unittest.main()
