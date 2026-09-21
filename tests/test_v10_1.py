from pathlib import Path
import inspect
import unittest

import main
from release_naming import start_archive_stem

ROOT = Path(__file__).resolve().parents[1]

class TestTaxo101StableRelease(unittest.TestCase):
    def test_stable_identity(self):
        self.assertRegex(main.APP_VERSION,r"^10\\.(?:1|[2-9][0-9]*)(?:-r[0-9.]+)?$")
        version=(ROOT/"VERSION.txt").read_text("utf-8")
        self.assertIn("Version: 10.1",version)
        self.assertIn("Release type: stable",version)
        self.assertEqual(start_archive_stem("10.1"),"Taxo_v10_1_START")

    def test_verified_r5_navigation_fix_is_in_stable(self):
        build=inspect.getsource(main.App.build_ui)
        timesheet=inspect.getsource(main.App.show_employee_timesheet)
        self.assertIn('add_nav("Звіти","chart",command=self.show_reports_home)',build)
        self.assertNotIn('add_nav("Звіти","chart",command=self.show_employee_timesheet)',build)
        self.assertIn("_employee_timesheet_win",timesheet)
        self.assertNotIn('sidebar=tk.Frame(shell,bg=PALETTE["sidebar"]',timesheet)

    def test_windows_stable_metadata(self):
        installer=(ROOT/"installer/Taxo.iss").read_text("utf-8")
        self.assertIn('#define MyAppVersion "10.1"',installer)
        self.assertIn("Taxo_v10_1_Setup_Windows_x64",installer)
        workflow=(ROOT/".github/workflows/build-windows-v8.70.yml").read_text("utf-8")
        self.assertIn("Taxo_v10_1_Windows_x64_Portable.zip",workflow)

    def test_macos_stable_metadata(self):
        spec=(ROOT/"Taxo_macos.spec").read_text("utf-8")
        self.assertIn("version='10.1'",spec)
        self.assertIn("'CFBundleShortVersionString': '10.1'",spec)
        self.assertIn("'CFBundleVersion': '10.1'",spec)
        workflow=(ROOT/".github/workflows/build-macos-v8.70.yml").read_text("utf-8")
        self.assertIn("Taxo_v10_1_macOS_",workflow)

    def test_stable_publisher_covers_all_packages(self):
        workflow=(ROOT/".github/workflows/publish-v10.1.yml").read_text("utf-8")
        for marker in (
            "windows-latest","macos-15","macos-15-intel",
            "Taxo_v10_1_Setup_Windows_x64.exe",
            "Taxo_v10_1_Windows_x64_Portable.zip",
            "Taxo_v10_1_macOS_arm64_Portable.zip",
            "Taxo_v10_1_macOS_x86_64_Portable.zip",
            "Taxo_v10_1_START.zip","SHA256SUMS_v10_1.txt",
            "gh release create 'v10.1'","--latest",
        ):
            self.assertIn(marker,workflow)
        self.assertNotIn("--prerelease",workflow)

    def test_stable_release_docs(self):
        notes=(ROOT/"docs/releases/RELEASE_NOTES_v10_1.md").read_text("utf-8")
        audit=(ROOT/"docs/maintenance/AUDIT_v10_1_STABLE.md").read_text("utf-8")
        self.assertIn("Taxo 10.1",notes)
        self.assertIn("v10.1-r5",notes)
        self.assertIn("Ручний Windows",audit)

if __name__=="__main__":
    unittest.main()
