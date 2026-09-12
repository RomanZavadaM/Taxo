# Taxo — CURRENT CHECKPOINT

Date: 2026-09-12

## Current candidate
- Version: **v8.66 candidate r1**
- Base: stable v8.65, GitHub `main` commit `f9101c1a41d7c036bade5ce66989171399189d4b`.
- Scope: UI usability only; tachograph recognition logic is postponed and unchanged.
- Main fixes: reliable clipboard actions, visible multi-row toolbars, screen-fitted windows, restored application menu, permanently visible tachograph day timeline and statistics button.
- macOS work branch: `work/v8.66-macos-executable`; native `Taxo.app` candidates for Apple Silicon and Intel, built separately from the Windows package.

## Stable release
- Version: **v8.65**
- Promoted from verified candidate **r3**.
- Previous stable: v8.64 (`c2ebee7bb832680e1c98a447cb90ebd115349fed`).
- Stable v8.65 remains untouched while v8.66 is tested separately.

## v8.65 time model
- Existing schedule intervals are PLAN driving intervals.
- Each segment has explicit WORK start/end plus DRIVING start/end.
- Durations are derived from boundaries.
- Legacy driving boundaries initially copy 1:1 into working boundaries.
- `Без тахо — стандартні 8 год`: work=8h, drive=0h.
- Tachograph future data = FACTUAL driving; it must not overwrite PLAN automatically.

## r3 release fixes
- Centralized output-file exception handler for locked/open PDF/XLSX files.
- On locked existing file: Retry / Create copy / Cancel.
- Nonhandled GUI exceptions are logged locally to `Documents/DriverWorktime/Logs/Taxo_errors.log`.
- Graphical schedule no longer hides labels of short bands; every work/driving band receives an adaptive label.

## Release assets expected
- `Taxo_v8_65_Setup_Windows_x64.exe`
- `Taxo_v8_65_Windows_x64_Portable.zip`
- `Taxo_v8_65_source.zip`
- `SHA256SUMS_v8_65.txt`
