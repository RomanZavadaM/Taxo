# Taxo CI maintenance — 2026-11-07

Status: **COMPLETED / VERIFIED / process-only**. Product version remained **10.12-r9**.

Base before maintenance: `387b909bdabfa5df1a4a08d859f2993632a05db5`.
Replacement CI PR: #220.
CI integration commit: `894fdbb235b2b91c2bb334b8fadfb99566671fc9`.
Post-merge docs-only smoke PR: #222 → `bc32daa1b63c20aa4398fa35262d32456b62088c`.
Historical drafts #142 and #152 were not merged; after validation they were closed as superseded.

## Problems reproduced

1. Superseded Windows / Windows 7 / macOS PR runs from older heads continued consuming runners after a newer commit.
2. Ordinary docs-only changes could trigger full platform builds and START packaging.

## Integrated design

- Required `build-windows` remains present on **every pull request**. Active `Protect main` ruleset was read live and still requires exact status `build-windows`.
- Windows PR workflow classifies only ordinary documentation changes as docs-only. In that mode checkout + multilingual documentation validation run, while Python setup, dependencies, regression, START preflight, PyInstaller, ZIP/installer/checksums and package artifacts are skipped.
- `docs/releases/**` is explicitly release-sensitive and never treated as ordinary docs-only.
- Windows / Win7 / macOS PR concurrency is grouped by PR number; `cancel-in-progress` applies only to pull_request runs. Main/manual work is not cancelled.
- Win7/macOS full-check paths conservatively include code, tests, dependencies, scripts, packaging, workflow files, VERSION, legal notices, `.release/**` and `docs/releases/**`.
- Ordinary docs-only main pushes are excluded from Windows / Win7 / macOS and START workflows.
- `source-test-archive.yml` keeps full work for code/release-sensitive pushes and manual dispatch.
- `publish-current.yml` was not changed. Exact-source release gates remain separate and still require successful Windows / Win7 / macOS / START runs for issued source.

## Live validation evidence

### Superseded PR runs

- Old Windows run #1262 / id `42398097195` → **cancelled** after a newer #220 head.
- Old Win7 run #258 / id `42398097196` → **cancelled**.
- Older Win7/macOS runs from prior heads were also observed cancelled; macOS matrix jobs were interrupted and downstream packaging skipped.

### Full workflow-sensitive PR

Final #220 head: `0db456281f84f22d62e55b599b66abc35edc1be2`.

- Windows #1263 / id `42398148050` — **SUCCESS**.
- Win7 #259 / id `42398148017` — **SUCCESS**.
- macOS #1184 / id `42398148033` — **SUCCESS** on ARM64 and Intel.
- The Windows docs classifier ran successfully and selected the **full** path because workflow/tests were changed.

### Docs-only PR fast path

Disposable PR #221 changed only `docs/maintenance/CI_DOCS_ONLY_SMOKE_2026-11-07.md`.

- Only Windows #1264 / id `42398207597` started — **SUCCESS**.
- Documentation verification ran.
- Repository/version heavy check, Python setup, dependencies, regression, START guards, PyInstaller, installer, checksums and artifacts were all **skipped**.
- Win7/macOS did not start.
- PR #221 was closed without merge.

### Workflow-sensitive post-merge behavior

PR #220 merge commit: `894fdbb235b2b91c2bb334b8fadfb99566671fc9`.

- Windows #1265 / id `42398524456` — **SUCCESS**.
- Win7 #260 / id `42398524464` — **SUCCESS**.
- macOS #1185 / id `42398524403` — **SUCCESS** on ARM64 and Intel.
- START #2314 / id `42398524401` — **SUCCESS**.
- `Publish current Taxo release` did **not** start.

### Ordinary docs-only post-merge behavior

PR #222 changed only `docs/maintenance/CI_POST_MERGE_DOCS_SMOKE_2026-11-07.md`.

- PR check: only lightweight Windows #1266 / id `42398857520` — **SUCCESS**; heavy steps skipped; no Win7/macOS.
- Merge commit: `bc32daa1b63c20aa4398fa35262d32456b62088c`.
- GitHub Actions query for that exact merge SHA returned **0 workflow runs**.
- Therefore ordinary docs-only main push did not launch Windows, Win7, macOS, START or publisher.

## Release / version safety

- `VERSION.txt` remained `Version: 10.12-r9` throughout this slice.
- Product code and business logic were not changed.
- `publish-current.yml` blob remained unchanged (`9664b0daa7e9322fb4b5babd30c832e1b7a4c694`).
- Stable/Latest remains `v10.10-r5`; latest published candidate remains `v10.11-r10`.
- This maintenance is **not** a product revision and does not consume `10.12-r10`.

## Next

Next code slice is **10.12-r10**: live reachability gate for **«План → факт»**. Because that route changes factual data, test it separately with isolated data and explicit plan/fact integrity checks. Do not start a broad UX cleanup in the same slice.
