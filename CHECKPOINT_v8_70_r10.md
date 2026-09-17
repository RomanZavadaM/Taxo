# Taxo v8.70 candidate r10 — single-driver work analysis

Date: 17.09.2026
Base: `main` at v8.70 candidate r9.

## Requested change

1. In the driver work-time table, the №340 protocol must not only be generated/saved as PDF; the user needs a direct **«Відкрити PDF»** button.
2. Add an hourly work-time balance for one selected driver as part of the weekly control around the existing 56-hour check.

## Implementation

- `taxo_app.py` is the r10 entry point used by `START.bat` and future PyInstaller builds.
- `work_analysis_ext.py` extends the existing large `main.py` without rewriting historical code.
- The №340 analysis window gets **«Відкрити PDF»**. It regenerates the current protocol in the workspace `Output` folder and opens it with the operating system's default PDF viewer.
- The single-driver analysis now shows every calendar week intersecting the selected month in `HH:MM`:
  - total **work time** and signed balance to **60:00**;
  - total **driving time** and signed balance to **56:00**.
- Positive balance means time remains to the limit; negative balance means the limit is exceeded.
- The report explicitly states that **56:00 applies to driving, not total work time**. The 4-calendar-month average 48:00/week remains a separate control.
- The same weekly balance section is included in the on-screen protocol and the generated PDF.

## Packaging / safety

- `START.bat`, Windows spec, macOS spec and the Windows installer are r10-aware.
- Windows/macOS source CI compiles `taxo_app.py` and `work_analysis_ext.py` and runs the full unittest suite.
- No database or personal data is added to the repository.
- Tachograph recognition logic is unchanged.

## Tests added

`tests/test_v8_70_r10.py` covers:
- signed `HH:MM` balances;
- separate 60:00 work / 56:00 driving limits;
- negative balances on overrun;
- insertion of the weekly balance into the protocol;
- stable safe default PDF file naming.
