from pathlib import Path
import unittest

import personnel_v91
import v91_features
from release_naming import start_archive_stem, version_from_file


ROOT = Path(__file__).resolve().parents[1]


class TestTaxo100StableReleaseBaseline(unittest.TestCase):
    def test_current_source_is_10_0_1_candidate_r1(self):
        self.assertEqual(version_from_file(ROOT / "VERSION.txt"), "10.0.1 candidate r1")
        text = (ROOT / "VERSION.txt").read_text("utf-8")
        self.assertIn("Version: 10.0.1 candidate r1", text)
        self.assertIn("Release type: hotfix candidate / pre-release", text)
        self.assertIn("Current stable / rollback point: Taxo 10.0", text)

    def test_runtime_version_markers_are_candidate_r1(self):
        self.assertEqual(v91_features.APP_VERSION, "10.0.1 candidate r1")
        self.assertEqual(personnel_v91.APP_VERSION, "10.0.1 candidate r1")
        self.assertIn("Taxo 10.0.1 candidate r1", v91_features.WINDOW_TITLE)
        self.assertIn("Taxo 10.0.1 candidate r1", personnel_v91.WINDOW_TITLE)
        self.assertIn("Taxo 10.0.1 candidate r1", (ROOT / "taxo_app.py").read_text("utf-8"))

    def test_candidate_start_archive_name(self):
        self.assertEqual(
            start_archive_stem("10.0.1 candidate r1"),
            "Taxo_v10_0_1_candidate_r1_START",
        )

    def test_windows_release_metadata(self):
        installer = (ROOT / "installer/Taxo.iss").read_text("utf-8")
        windows = (ROOT / ".github/workflows/build-windows-v8.70.yml").read_text("utf-8")
        self.assertIn('#define MyAppVersion "10.0"', installer)
        self.assertIn("Taxo_v10_0_Setup_Windows_x64", installer)
        self.assertIn("Taxo_v10_0_Windows_x64", installer)
        self.assertIn("Taxo_v10_0_Setup_Windows_x64.exe", windows)
        self.assertIn("Taxo_v10_0_Windows_x64_Portable.zip", windows)

    def test_macos_release_metadata(self):
        spec = (ROOT / "Taxo_macos.spec").read_text("utf-8")
        workflow = (ROOT / ".github/workflows/build-macos-v8.70.yml").read_text("utf-8")
        self.assertIn("version='10.0'", spec)
        self.assertIn("'CFBundleShortVersionString': '10.0'", spec)
        self.assertIn("'CFBundleVersion': '10.0'", spec)
        self.assertIn("Taxo_v10_0_macOS_", workflow)

    def test_stable_publisher_covers_all_platforms(self):
        workflow = (ROOT / ".github/workflows/publish-v10.0.yml").read_text("utf-8")
        for marker in (
            "windows-latest",
            "macos-15",
            "macos-15-intel",
            "Taxo_v10_0_Windows_x64_Portable.zip",
            "Taxo_v10_0_Setup_Windows_x64.exe",
            "Taxo_v10_0_macOS_",
            "Taxo_v10_0_START.zip",
            "gh release create 'v10.0'",
            "--latest",
        ):
            self.assertIn(marker, workflow)
        self.assertNotIn("--prerelease", workflow)


if __name__ == "__main__":
    unittest.main()
