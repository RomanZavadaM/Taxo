# CI optimization — 2026-11-05

Status: **in progress; draft PR #152; not merged**.

Base: `main` `1f6a397fdd7b218a21ffc10f3fd87d5aad566d36`  
Branch: `ci/docs-only-optimization-20261105`  
Stable remains: `v10.10-r4`

## Purpose

Reduce wasted GitHub Actions usage without weakening release/build protection.

Ordinary documentation-only changes should not launch heavy Windows, Windows 7, macOS or START packaging work. Code, dependencies, packaging, scripts/security, workflow and release-sensitive changes keep full checks.

## Implementation

### Windows
- Pull requests still create the existing `build-windows` check so required-check behavior is preserved.
- A fail-closed classifier checks the complete PR diff.
- Only ordinary documentation changes are considered docs-only.
- `docs/releases/**` is explicitly release-sensitive and therefore forces full CI.
- For docs-only PRs, only checkout, classification and multilingual documentation verification run.
- Python setup, dependency installation, regression, START checks, PyInstaller, installer, checksums and executable artifact upload are skipped.
- Superseded PR runs may be cancelled; push/main runs are not cancelled.

### Windows 7 and macOS
- Pull-request and main-push filters run for all non-documentation changes.
- `docs/releases/**` is re-included and forces full checks.
- Ordinary Markdown/docs changes do not trigger these heavy platform builds.
- Workflow/release/security/code changes remain included by the conservative all-files-minus-docs pattern.
- Superseded PR runs may be cancelled; push/main runs are not cancelled.

### START packaging
- Main/work branch pushes that are only ordinary docs changes do not run START packaging.
- Any non-documentation change and `docs/releases/**` still run it.
- Manual `workflow_dispatch` remains available.

### Publish workflow
- `.github/workflows/publish-current.yml` was not weakened.
- Release publication still requires successful exact-source Windows, Windows 7, macOS and START runs.

## Live validation

### Full workflow-change PR — #152
Opening PR #152 changed workflow files. As required, GitHub started:
- Windows;
- Windows 7;
- macOS ARM64 + Intel.

This proves workflow changes are not classified as documentation-only.

### Docs-only smoke — PR #153
Temporary branch `ci/docs-only-smoke-20261105`, one file:
`docs/maintenance/CI_DOCS_ONLY_TRIGGER_TEST_2026-11-05.md`.

Observed:
- only Windows workflow run `41988510150` started;
- Windows 7 did not start;
- macOS did not start;
- Windows job `build-windows` completed **success**;
- classifier completed **success**;
- multilingual documentation verification completed **success**;
- Python setup, dependencies, compile, regression, START checks, PyInstaller, installer, checksums and executable upload were all **skipped**.

PR #153 is a temporary smoke and must be closed without merge.

## Safety / release invariants

- Stable `v10.10-r4` is unchanged.
- No product version/revision change.
- PR #151 remains a separate code/hotfix line.
- Old PR #142 is not reused or merged.
- Published tags/releases are untouched.
- `publish-current.yml` exact-source gating remains unchanged.
- Release-sensitive `docs/releases/**` changes force full platform/START checks.

## Remaining before integration

1. Final PR #152 full platform checks must finish successfully on the latest head.
2. Close PR #153 without merge.
3. Confirm latest PR #152 diff contains only CI/process documentation changes.
4. Update HANDOFF / WORKLOG / Issue #61 with final result.
5. Integration decision is separate; no automatic merge.
