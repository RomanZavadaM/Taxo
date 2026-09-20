from pathlib import Path
import unittest

from release_naming import start_archive_stem


ROOT = Path(__file__).resolve().parents[1]


class TestTaxo100StableRelease(unittest.TestCase):
    def test_stable_10_release_docs_remain_present(self):
        notes = (ROOT / "docs/releases/RELEASE_NOTES_v10_0.md").read_text("utf-8")
        audit = (ROOT / "docs/maintenance/AUDIT_v10_0_STABLE.md").read_text("utf-8")
        self.assertIn("Taxo 10.0", notes)
        self.assertIn("Stable release", notes)
        self.assertIn("91c0d6365a40eb09fe40f97a2965da40b314bc15", audit)

    def test_stable_start_archive_name(self):
        self.assertEqual(start_archive_stem("10.0"), "Taxo_v10_0_START")

    def test_windows_release_metadata_for_stable_10_is_immutable(self):
        installer = (ROOT / "installer/Taxo.iss").read_text("utf-8")
        windows = (ROOT / ".github/workflows/build-windows-v8.70.yml").read_text("utf-8")
        self.assertIn('#define MyAppVersion "10.0"', installer)
        self.assertIn("Taxo_v10_0_Setup_Windows_x64", installer)
        self.assertIn("Taxo_v10_0_Windows_x64", installer)
        self.assertIn("Taxo_v10_0_Setup_Windows_x64.exe", windows)
        self.assertIn("Taxo_v10_0_Windows_x64_Portable.zip", windows)

    def test_macos_stable_10_packaging_metadata_is_preserved(self):
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
