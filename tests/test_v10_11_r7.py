import re
import unittest
from pathlib import Path

import main


ROOT = Path(__file__).resolve().parents[1]


def version_key(value: str):
    match = re.fullmatch(r"(\d+)\.(\d+)-r(\d+)(?:\.(\d+))?", value)
    if not match:
        raise AssertionError(f"unexpected version format: {value}")
    major, minor, revision, subrevision = match.groups()
    return int(major), int(minor), int(revision), int(subrevision or 0)


class Win7GeneralRegressionR7Tests(unittest.TestCase):
    def test_r7_identity_is_current(self):
        self.assertEqual(main.APP_VERSION, "10.11-r7")
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text(encoding="utf-8").strip(),
            "Version: 10.11-r7",
        )

    def test_win7_runs_full_unittest_discovery_before_packaging(self):
        source = (ROOT / ".github/workflows/build-win7-current.yml").read_text(
            encoding="utf-8"
        )
        full_suite = "python -m unittest discover -s tests -v"
        build = "python -m PyInstaller --noconfirm --clean packaging/Taxo_win7.spec"
        self.assertIn(full_suite, source)
        self.assertIn(build, source)
        self.assertLess(source.index(full_suite), source.index(build))
        self.assertIn("Set up CPython 3.8.10 x64", source)
        self.assertIn("Run full regression suite on Python 3.8", source)

    def test_win7_stages_legacy_layout_before_full_suite(self):
        source = (ROOT / ".github/workflows/build-win7-current.yml").read_text(
            encoding="utf-8"
        )
        stage = "python tests/stage_legacy_layout.py"
        full_suite = "python -m unittest discover -s tests -v"
        self.assertIn(stage, source)
        self.assertIn(full_suite, source)
        self.assertLess(source.index(stage), source.index(full_suite))

    def test_win7_gate_is_not_limited_to_only_recent_security_modules(self):
        source = (ROOT / ".github/workflows/build-win7-current.yml").read_text(
            encoding="utf-8"
        )
        start = source.index("      - name: Run full regression suite on Python 3.8")
        end = source.index("      - name: Build Windows 7 portable", start)
        section = source[start:end]
        self.assertIn("unittest discover -s tests -v", section)
        self.assertNotIn("tests.test_v10_11_r5", section)
        self.assertNotIn("tests.test_v10_11_r6", section)


if __name__ == "__main__":
    unittest.main()
