# -*- coding: utf-8 -*-
"""Taxo 10.10-r2 — CI hardening and regression-suite isolation.

* One-off publish/apply/repair workflows are archived in
  ``docs/history/workflows/`` and no longer executed by GitHub. Two of them
  (``publish-v10.3.yml``, ``update-release-description-v9.yml``) could rewrite
  historical releases on a push to ``main``.
* Only the four active gates stay in ``.github/workflows/`` and none of them
  may write repository contents or releases.
* The required ``build-windows`` check runs on every pull request, so
  documentation-only PRs can be integrated.

The CI working tree restores archived YAML into ``.github/workflows/`` for
historical tests (``tests/stage_legacy_layout.py``), therefore the inventory is
read from git, not from the file system.
"""
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = {
    "build-windows-v8.70.yml",
    "build-win7-current.yml",
    "build-macos-v8.70.yml",
    "source-test-archive.yml",
}
ARCHIVE = ROOT / "docs" / "history" / "workflows"


def _tracked(path):
    if shutil.which("git") is None:
        return None
    try:
        out = subprocess.run(
            ["git", "ls-files", "--", path], cwd=str(ROOT),
            capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    files = [line.strip() for line in out.splitlines() if line.strip()]
    return files or None


class TestWorkflowInventory(unittest.TestCase):
    def test_only_active_gates_are_executable(self):
        tracked = _tracked(".github/workflows")
        if tracked is None:
            self.skipTest("git checkout not available")
        names = {Path(p).name for p in tracked}
        self.assertEqual(names, ACTIVE)

    def test_active_gates_cannot_write_releases(self):
        for name in sorted(ACTIVE):
            text = (ROOT / ".github" / "workflows" / name).read_text("utf-8")
            self.assertNotRegex(text, r"contents:\s*write", name)
            self.assertNotIn("gh release", text, name)
            self.assertNotIn("softprops/action-gh-release", text, name)

    def test_dangerous_historical_publishers_are_archived(self):
        for name in ("publish-v10.3.yml", "update-release-description-v9.yml"):
            self.assertTrue((ARCHIVE / name).is_file(), name)
        tracked = _tracked(".github/workflows")
        if tracked is not None:
            self.assertFalse(any(Path(p).name.startswith(("publish-", "apply-", "repair-", "restore-",
                                                          "backfill-", "update-release-"))
                                 for p in tracked))
        self.assertTrue((ARCHIVE / "README.md").is_file())

    def test_required_check_runs_on_every_pull_request(self):
        text = (ROOT / ".github" / "workflows" / "build-windows-v8.70.yml").read_text("utf-8")
        block = text[text.index("on:"):text.index("\npermissions:")]
        self.assertRegex(block, r"\n  pull_request:\s*\n(?!\s{4}paths)")
        self.assertIn("build-windows:", text)

    def test_historical_tests_get_archived_workflows_in_ci_only(self):
        stage = (ROOT / "tests" / "stage_legacy_layout.py").read_text("utf-8")
        self.assertIn('ROOT / "docs" / "history" / "workflows"', stage)
        self.assertIn('ROOT / ".github" / "workflows"', stage)


class TestRevisionIdentity(unittest.TestCase):
    def test_version_is_10_10_r2_or_later(self):
        version = (ROOT / "VERSION.txt").read_text("utf-8").strip()
        match = re.fullmatch(r"Version: 10\.(\d+)-r(\d+)", version)
        self.assertIsNotNone(match, version)
        self.assertGreaterEqual((int(match.group(1)), int(match.group(2))), (10, 2))
        number = version.split(": ", 1)[1]
        self.assertIn(f'APP_VERSION = "{number}"', (ROOT / "main.py").read_text("utf-8"))


if __name__ == "__main__":
    unittest.main()
