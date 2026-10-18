# GitHub Actions usage audit — 2026-10-18

Status: **in progress; PR validation required; not merged**. Base: main `2bb7d58001301bf17d5ac8dbf06525a2a80e1af7`.

## Verified active workflow configuration
- `.github/workflows/build-windows-v8.70.yml`: all PRs + every main push; heavy Windows PyInstaller, unittest, setup/portable packaging. Job `build-windows` is the required branch-protection check per audit dated 2026-10-05.
- `build-win7-current.yml`: all main pushes and PRs matching selected paths; formerly included `WORKLOG.md`; PyInstaller Windows 7 compatibility build.
- `build-macos-v8.70.yml`: all main pushes and selected-path PRs, including `WORKLOG.md`; two expensive architecture builds and regression runs.
- `source-test-archive.yml`: push to main or work/v9.* or work/v10.* (and manual); full Linux regression and START packaging on *every* push.
- No Rust or npm jobs in these four verified active files. The 2026-10-05 audit records 72 historical workflows archived, leaving these four active.
- Runs/minutes billing breakdown **not available from this GitHub connector**. This is verified trigger analysis, **not** a measured usage-by-job ranking.

## Changes in this PR
1. Windows/macOS concurrency now groups PR runs by PR number and cancels superseded PR CI, but retains non-canceling behavior for push/main and manual runs. Release packaging must never be interrupted by an unrelated push.
2. Remove `WORKLOG.md` from Win7 and macOS pull-request path lists. Worklog-only PRs must not launch those platform builds.
3. START packaging now excludes docs-only pushes via `paths-ignore`; mixed code+docs pushes still run START. Manual START builds remain possible.

## Important remaining work, not claimed complete
- Required `build-windows` remains heavy on docs-only PRs: simply applying a top-level `paths` filter would leave the required check pending and block merge. First design a lightweight, always-present required gate and preserve a heavyweight code-build check, updating GitHub branch protection in lockstep.
- Draft PR gating and fine-grained path-aware platform checks require validating final required checks, `ready_for_review` and security of PR-derived path filtering. Never weaken dependency license and bundle gates.
- Audit current Actions run durations, cache feasibility (Python pip rather than Rust/npm), and manual/tag/release paths using GitHub Actions UI/API before further optimization.
- Preserve complete Windows, Windows 7, macOS arm64/x86_64 and START packaging for release checkpoints.
- Validate with docs-only, code-only, platform-specific and release-driving PRs; do not merge on YAML review alone.
- `PROJECT_STATE.md` should remain unchanged until integration is confirmed; do not create a product revision for CI-only maintenance.

## Validation matrix
- Docs-only PR: required Windows check remains, Win7/macOS PR jobs absent; document total heavy minutes for remaining optimization.
- Repeated PR commits: old Windows/macOS PR runs canceled; latest SHA passes.
- Code/platform PR: all currently applicable checks execute and pass.
- Docs-only main push: START packaging skipped. Note Windows/macOS/Win7 main-push builds still occur until next safe optimization step.
- Mixed code+docs main push: START runs.
- workflow_dispatch: no change to manually invoked release/test packaging.

Ownership: resume from START_HERE -> PROJECT_RULES -> PROJECT_STATE -> WORKLOG -> Issue #61. This PR is a narrow first stage.
