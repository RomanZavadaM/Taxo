# Taxo v8.66 candidate r6 checkpoint

Date: 2026-09-13
Base branch state: v8.66 candidate r5 (`50ac5a71f16f72247731050d54da335a4d2888fe`).
Stable production baseline remains v8.65 on `main` (`f9101c1a41d7c036bade5ce66989171399189d4b`).

## r6 scope

- UI stabilization only; tachograph recognition algorithm unchanged.
- Add a `Розділи` menu so every one of the 9 main tabs remains reachable when Notebook headers do not fit.
- Remember and restore the last selected main tab.
- Fix tachograph initial sash placement after a hidden Notebook tab receives a real size.
- Reserve roughly 70% of tachograph width for preview/results and roughly 30% for the scan catalog on initial layout.
- Compact tachograph metadata, timeline, interval actions and protocol actions so critical controls remain visible on smaller screens.
- Do not continuously overwrite user-adjusted sash positions after the initial layout.

## Verification

- Python compilation: PASS.
- Full app smoke test at 900x600: PASS.
- Full app smoke test at 1024x700: PASS.
- Tachograph critical-control layout at 900x600: PASS.
- Tachograph critical-control layout at 1024x700: PASS.
- Tachograph critical-control layout at 1200x760: PASS.
- Database schema: unchanged.
- Tachograph recognition algorithm: unchanged.

The exact source delta from candidate r5 is stored in `PATCH_v8_66_r6.diff`; the complete tested START.bat package is `Taxo_v8_66_TEST_r6_START.zip`.
