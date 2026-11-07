# -*- coding: utf-8 -*-
"""CI maintenance regression guards — 2026-11-07.

Process-only checks. Product version must not change because of this slice.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows"


class TestCiMaintenance20261107(unittest.TestCase):
    def _read(self, name):
        return (WF / name).read_text("utf-8")

    def test_required_windows_check_still_runs_on_every_pr(self):
        text = self._read("build-windows-v8.70.yml")
        trigger = text[text.index("on:"):text.index("\npermissions:")]
        self.assertRegex(trigger, r"\n  pull_request:\s*\n(?!\s{4}(?:paths|paths-ignore):)")
        self.assertIn("build-windows:", text)

    def test_platform_pr_runs_cancel_superseded_heads(self):
        for name in (
            "build-windows-v8.70.yml",
            "build-win7-current.yml",
            "build-macos-v8.70.yml",
        ):
            text = self._read(name)
            self.assertIn(
                "group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}",
                text,
                name,
            )
            self.assertIn(
                "cancel-in-progress: ${{ github.event_name == 'pull_request' }}",
                text,
                name,
            )

    def test_ordinary_docs_main_pushes_skip_heavy_platform_and_start_workflows(self):
        for name in (
            "build-windows-v8.70.yml",
            "build-win7-current.yml",
            "build-macos-v8.70.yml",
            "source-test-archive.yml",
        ):
            text = self._read(name)
            self.assertIn("- '!docs/**'", text, name)
            self.assertIn("- 'docs/releases/**'", text, name)
            self.assertIn("- '!HANDOFF_CURRENT.md'", text, name)
            self.assertIn("- '!WORKLOG.md'", text, name)

    def test_release_security_workflow_sensitive_paths_keep_full_platform_checks(self):
        for name in ("build-win7-current.yml", "build-macos-v8.70.yml"):
            text = self._read(name)
            for path in (
                "- '.github/workflows/**'",
                "- 'scripts/**'",
                "- 'requirements*.txt'",
                "- 'docs/releases/**'",
                "- 'THIRD_PARTY_NOTICES.md'",
                "- '.release/**'",
            ):
                self.assertIn(path, text, f"{name}: {path}")

    def test_windows_docs_fast_path_excludes_release_notes(self):
        text = self._read("build-windows-v8.70.yml")
        self.assertIn("Detect ordinary documentation-only PR", text)
        self.assertIn("steps.scope.outputs.docs_only != 'true'", text)
        self.assertIn("-not $file.StartsWith('docs/releases/')", text)
        self.assertIn("Verify multilingual documentation", text)


if __name__ == "__main__":
    unittest.main()
