# Taxo v8.66 candidate r8 — publication checkpoint

Date: 2026-09-13

## Authoritative state
- Stable branch: `main`
- Stable release: **v8.65**
- Stable commit: `f9101c1a41d7c036bade5ce66989171399189d4b`
- Current candidate: **v8.66 candidate r8**
- Candidate branch: `work/v8.66-ui-polish-r8`
- Candidate pull request: **#8** (draft; do not merge before manual regression testing)
- Previous candidate PR #7 is superseded by r8.

## r8 fixes
- Monthly shift-schedule controls are split into two rows so all actions remain visible at 900×600, 1024×700 and 1200×760.
- Monthly schedule opens on the month/year from the current schedule date (`13.09.2026` → 09.2026).
- Reopening the window re-synchronizes the selected month/year.
- `Оновити` invalidates the previously generated schedule PDF.
- `Відкрити графік PDF` regenerates the current selected month when the previous PDF is stale, then opens the new file.

## Verification
- Python compile: PASS (`main.py`, `tachograph.py`, `attestation_render.py`).
- Monthly schedule layout: PASS at 900×600, 1024×700, 1200×760.
- Current r8 `main.py` Git blob SHA: `5f79ed43e4ec72b3144e29f1ff18febfefd58d3b`.
- Test package: `Taxo_v8_66_TEST_r8_START.zip`
- Test package SHA-256: `d2c37458f65174f9b2d7c2ac7a99f58359eac0bb1c06358fe0ab0198dc370116`

## Deliberately unchanged
- Tachograph recognition algorithm.
- Database schema.
- Stable `main` v8.65.
- Executable cadence: intermediate versions via `START.bat`; next Windows + macOS executable milestone is v8.70.

This file is the recovery point if chat context is lost.
