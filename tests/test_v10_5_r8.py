# -*- coding: utf-8 -*-
import re
import unittest
from pathlib import Path

import v1055_features

ROOT = Path(__file__).resolve().parents[1]


class Win7TabIdCompatibilityR8Tests(unittest.TestCase):
    def test_python38_openpyxl_signature_is_recognized(self):
        self.assertTrue(v1055_features._is_childsheet_tabid_error(
            TypeError("__init__() got an unexpected keyword argument 'tabId'")
        ))

    def test_verbose_childsheet_signature_remains_recognized(self):
        self.assertTrue(v1055_features._is_childsheet_tabid_error(
            TypeError("ChildSheet.__init__() got an unexpected keyword argument 'tabId'")
        ))

    def test_unrelated_typeerrors_are_not_swallowed(self):
        self.assertFalse(v1055_features._is_childsheet_tabid_error(TypeError("other failure")))
        self.assertFalse(v1055_features._is_childsheet_tabid_error(
            TypeError("__init__() got an unexpected keyword argument 'tabIndex'")
        ))
        self.assertFalse(v1055_features._is_childsheet_tabid_error(ValueError("tabId")))


class R8IntegrationTests(unittest.TestCase):
    def test_candidate_identity_is_r8_or_later(self):
        version = (ROOT / "VERSION.txt").read_text(encoding="utf-8")
        match = re.search(r"Version:\s+(\d+)\.(\d+)-r(\d+)", version)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(tuple(map(int, match.groups())), (10, 5, 8))
        main = (ROOT / "main.py").read_text(encoding="utf-8")
        main_match = re.search(r'APP_VERSION\s*=\s*"(\d+)\.(\d+)-r(\d+)"', main)
        self.assertIsNotNone(main_match)
        self.assertGreaterEqual(tuple(map(int, main_match.groups())), (10, 5, 8))

    def test_r8_remains_in_entrypoint_chain_after_later_revisions(self):
        entry = (ROOT / "taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from v1058_features import install as install_v1058", entry)
        self.assertIn("install_v1058(", entry)
        self.assertIn("install_v1057(", entry)

    def test_source_package_requires_r8_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text(encoding="utf-8")
        self.assertIn("v1058_features.py", workflow)

    def test_r8_is_compatibility_only_checkpoint(self):
        source = (ROOT / "v1058_features.py").read_text(encoding="utf-8")
        self.assertIn("Windows 7 / openpyxl tabId compatibility checkpoint", source)
        self.assertIn('APP_VERSION = "10.5-r8"', source)


if __name__ == "__main__":
    unittest.main()
