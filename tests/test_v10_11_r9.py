import re
import unittest
from pathlib import Path

import main


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_WORKFLOWS = (
    '.github/workflows/build-windows-v8.70.yml',
    '.github/workflows/build-win7-current.yml',
    '.github/workflows/build-macos-v8.70.yml',
    '.github/workflows/source-test-archive.yml',
    '.github/workflows/publish-current.yml',
)
EXPECTED_PINS = {
    'actions/checkout': '11d5960a326750d5838078e36cf38b85af677262',
    'actions/setup-python': 'a26af69be951a213d495a4c3e4e4022e16d87065',
    'actions/upload-artifact': 'ea165f8d65b6e75b540449e92b4886f43607fa02',
}


def version_key(value):
    base, sep, revision = str(value or "").strip().partition("-r")
    major, minor = (int(part) for part in base.split(".", 1))
    return major, minor, int(revision) if sep else 0


class WorkflowSupplyChainR9Tests(unittest.TestCase):
    def test_r9_identity_is_historical_anchor(self):
        self.assertGreaterEqual(version_key(main.APP_VERSION), (10, 11, 9))
        current = (ROOT / 'VERSION.txt').read_text(encoding='utf-8').strip()
        self.assertTrue(current.startswith('Version: '))
        self.assertEqual(
            version_key(current[len('Version: '):]),
            version_key(main.APP_VERSION),
        )

    def test_official_actions_are_pinned_to_expected_commit_shas(self):
        uses_re = re.compile(r'^\s*-?\s*uses:\s+(actions/(?:checkout|setup-python|upload-artifact))@([^\s#]+)', re.MULTILINE)
        for rel in ACTIVE_WORKFLOWS:
            source = (ROOT / rel).read_text(encoding='utf-8')
            for action, ref in uses_re.findall(source):
                self.assertRegex(ref, r'^[0-9a-f]{40}$', rel)
                self.assertEqual(ref, EXPECTED_PINS[action], rel)

    def test_no_moving_major_refs_remain_in_active_workflows(self):
        moving = re.compile(r'uses:\s+actions/(?:checkout|setup-python|upload-artifact)@v\d+')
        for rel in ACTIVE_WORKFLOWS:
            source = (ROOT / rel).read_text(encoding='utf-8')
            self.assertIsNone(moving.search(source), rel)

    def test_pin_comments_keep_human_major_version_context(self):
        joined = '\n'.join((ROOT / rel).read_text(encoding='utf-8') for rel in ACTIVE_WORKFLOWS)
        self.assertIn('actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4', joined)
        self.assertIn('actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5', joined)
        self.assertIn('actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4', joined)


if __name__ == '__main__':
    unittest.main()
