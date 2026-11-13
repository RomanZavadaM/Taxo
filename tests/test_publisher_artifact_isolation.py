# -*- coding: utf-8 -*-
"""Regression contract for secure exact-head release artifact selection."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PUBLISH = ROOT / ".github" / "workflows" / "publish-current.yml"


class PublisherArtifactIsolationTests(unittest.TestCase):
    def setUp(self):
        self.source = PUBLISH.read_text(encoding="utf-8")

    def test_hold_blocks_previously_flagged_r8(self):
        self.assertIn('if [ "${version}" = "10.18-r8" ]; then', self.source)
        self.assertIn("SECURITY HOLD; publishing blocked", self.source)

    def test_exact_run_ids_required_before_download(self):
        self.assertIn('[[ "${id}" =~ ^[0-9]+$ ]]', self.source)
        self.assertIn("Refusing artifact download without explicit run ID", self.source)
        self.assertIn('actual_sha="$(jq -r \'.head_sha\' <<< "${metadata}")"', self.source)
        self.assertIn('conclusion="$(jq -r \'.conclusion\' <<< "${metadata}")"', self.source)
        self.assertNotIn('gh run download ""', self.source)

    def test_each_platform_search_is_isolated(self):
        self.assertIn('source_dir="$3"', self.source)
        self.assertIn('find "${source_dir}" -type f -name "${pattern}"', self.source)
        self.assertNotIn('find collected -type f -name "${pattern}"', self.source)
        assert_links = (
            ("Windows_x64_Portable.zip", "collected/windows"),
            ("Setup_Windows_x64.exe", "collected/windows"),
            ("Windows7_x64_Portable.zip", "collected/win7"),
            ("Setup_Windows7_x64.exe", "collected/win7"),
            ("macOS_arm64_Portable.zip", "collected/macos"),
            ("macOS_x86_64_Portable.zip", "collected/macos"),
        )
        for name, directory in assert_links:
            with self.subTest(name=name):
                lines = [x for x in self.source.splitlines()
                         if x.strip().startswith("copy_one ") and name in x]
                self.assertEqual(len(lines), 1)
                self.assertTrue(lines[0].rstrip().endswith('"${directory}"'.replace("${directory}", directory)))

    def test_automatic_maintenance_publish_defaults_to_portable(self):
        self.assertIn('requested="portable"', self.source)
        self.assertIn('requested="${{ inputs.package_set }}"', self.source)

    def test_downloads_only_after_exact_head_gate(self):
        names = (
            "Find successful build runs for exact source",
            "Download isolated exact-head platform packages",
            "Assemble exact release files",
            "Publish immutable prerelease",
        )
        positions = [self.source.index(x) for x in names]
        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
