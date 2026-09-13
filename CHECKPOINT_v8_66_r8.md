# Taxo — checkpoint v8.66 candidate r8

Date: 2026-09-13

## Current candidate
- Version: **v8.66 candidate r8**
- Stable base: v8.65, `main` commit `f9101c1a41d7c036bade5ce66989171399189d4b`.
- Candidate branch: `work/v8.66-ui-polish-r8`.
- Draft PR: **#8**.
- Stable `main` must remain unchanged until manual regression acceptance.

## Preserved fixes through r8
- r5: scrollable driver card and employment-date filtering in schedules/timesheets.
- r6: `Розділи` menu, remembered last tab, corrected TAHO pane sizing, compact controls and layout smoke tests.
- r7: direct system clipboard, Ukrainian-layout shortcuts, Alt+1…Alt+9 navigation, wheel scrolling, hide/show TAHO catalog.
- r8: monthly shift-schedule toolbar split into two rows; month/year follows current schedule date; reopening re-syncs the date; `Оновити` invalidates stale PDF state; `Відкрити графік PDF` regenerates the selected month when needed.

## Verification
- `main.py`, `tachograph.py`, `attestation_render.py`: Python compile PASS.
- Monthly schedule controls: PASS at 900×600, 1024×700, 1200×760.
- r8 `main.py` Git blob SHA: `5f79ed43e4ec72b3144e29f1ff18febfefd58d3b`.
- Test archive: `Taxo_v8_66_TEST_r8_START.zip`.
- Archive SHA-256: `d2c37458f65174f9b2d7c2ac7a99f58359eac0bb1c06358fe0ab0198dc370116`.

## Deliberately unchanged
- Tachograph recognition algorithm.
- Database schema.
- PLAN/FACT separation model.
- Executable policy: intermediate versions via `START.bat`; next full Windows + macOS executable milestone is v8.70.

This immutable checkpoint is the recovery source if chat context is lost.
