import unittest
from pathlib import Path

import main
from release_naming import candidate_stem, checksum_stem, github_env_lines


ROOT = Path(__file__).resolve().parents[1]

def version_key(value):
    base, sep, revision = str(value or "").strip().partition("-r")
    major, minor = (int(part) for part in base.split(".", 1))
    return major, minor, int(revision) if sep else 0


class ReleaseNamingR8Tests(unittest.TestCase):
    def test_r8_identity_is_historical_anchor(self):
        self.assertGreaterEqual(version_key(main.APP_VERSION), (10, 11, 8))
        current = (ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()
        self.assertTrue(current.startswith("Version: "))
        self.assertEqual(
            version_key(current[len("Version: "):]),
            version_key(main.APP_VERSION),
        )

    def test_release_naming_tokens_come_from_version(self):
        self.assertEqual(candidate_stem("10.11-r8"), "Taxo_v10_11_candidate_r8")
        self.assertEqual(checksum_stem("10.11-r8"), "10_11_r8")
        self.assertEqual(
            github_env_lines("10.11-r8"),
            (
                "TAXO_VERSION=10.11-r8",
                "TAXO_CANDIDATE_STEM=Taxo_v10_11_candidate_r8",
                "TAXO_CHECKSUM_STEM=10_11_r8",
            ),
        )

    def test_active_platform_workflows_have_no_revision_specific_package_names(self):
        paths = (
            ".github/workflows/build-windows-v8.70.yml",
            ".github/workflows/build-win7-current.yml",
            ".github/workflows/build-macos-v8.70.yml",
        )
        forbidden = ("10.11-r7", "candidate_r7", "10_11_r7")
        for rel in paths:
            source = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("release_naming.py --github-env", source, rel)
            for token in forbidden:
                self.assertNotIn(token, source, rel)

    def test_installer_requires_explicit_version_and_bundle_inputs(self):
        source = (ROOT / "packaging/installer/Taxo.iss").read_text(encoding="utf-8")
        self.assertIn('#error "MyAppVersion must be supplied by the build workflow"', source)
        self.assertIn('#error "SourceBundle must be supplied by the build workflow"', source)
        self.assertIn('#error "OutputBase must be supplied by the build workflow"', source)
        self.assertNotIn("10.11-r7", source)
        self.assertNotIn("candidate_r7", source)

    def test_stable_promotion_derives_required_assets_from_marker_version(self):
        source = (ROOT / ".github/workflows/publish-current.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn('candidate="$(printf', source)
        self.assertIn('"Taxo_v${candidate}_Setup_Windows_x64.exe"', source)
        self.assertIn('"SHA256SUMS_v${sumstem}.txt"', source)
        self.assertNotIn("Taxo_v10_10_candidate_r5_Setup_Windows_x64.exe", source)
        self.assertNotIn("SHA256SUMS_v10_10_r5.txt", source)


if __name__ == "__main__":
    unittest.main()
