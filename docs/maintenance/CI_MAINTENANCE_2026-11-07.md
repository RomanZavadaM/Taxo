# Taxo CI maintenance — 2026-11-07

Status: **IN PROGRESS / process-only**. Product version is unchanged.

Base: `main` `387b909bdabfa5df1a4a08d859f2993632a05db5`.
Current replacement PR: #220.
Historical drafts #142 and #152 are reference-only and must not be merged.

## Confirmed problems

1. Superseded Windows / Windows 7 / macOS PR runs from an older head continued consuming runners after a newer commit.
2. Ordinary docs-only work could trigger full platform builds and START packaging, including pushes to `work/v10.*`.

## Current design

- `build-windows` remains present on every pull request because branch protection requires it.
- For an ordinary documentation-only PR, Windows keeps checkout + documentation validation but skips Python setup, regression, PyInstaller and package artifacts.
- Windows / Win7 / macOS PR concurrency is grouped by PR number; only pull-request runs may be cancelled as superseded.
- Main/manual runs are not cancelled by the new concurrency rule.
- Ordinary docs-only pushes to main/work branches are filtered from Windows / Win7 / macOS / START workflows.
- `docs/releases/**` is explicitly re-included.
- Workflow, code, tests, dependencies, scripts, packaging, VERSION, legal notices and `.release/**` remain full-check paths.
- `publish-current.yml` is unchanged; exact-source release publishing remains separate.

## Validation still required

- full Windows / Win7 / macOS CI on PR #220;
- live proof that an older PR head becomes cancelled after a newer commit;
- docs-only PR smoke: required Windows check succeeds in lightweight mode while Win7/macOS do not launch;
- post-merge docs-only main push: platform and START heavy workflows do not launch;
- release-sensitive smoke remains full path;
- only after those checks: close #142/#152 as superseded and update recovery docs.

## Live superseded-run evidence

- PR #220 first valid platform head reached full Windows CI (run #1262 / id 42398097195), Win7 and macOS also started.
- Earlier Win7/macOS runs from superseded heads were already observed as `cancelled` after newer commits.
- This documentation checkpoint is intentionally a newer PR head to verify that the currently running Windows/Win7/macOS jobs are all cancelled by PR-number concurrency.
