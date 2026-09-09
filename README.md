# Taxo — v8.29

Windows desktop application for driver worktime, timesheets, activity-confirmation forms, route planning and an experimental analog tachograph module.

## Current version

**v8.29**

Highlights:
- driver selection directly on the Timesheet tab;
- PDF/XLSX exports include every calendar day of the selected month;
- wrapped PDF cells prevent route/vehicle text overlap;
- monthly totals row in PDF/XLSX;
- preliminary work-time compliance analysis based on Regulation №340, using the edition effective from 26.07.2026;
- planned / actual schedule separation, with tachograph data flowing into the actual side;
- tachograph scan recognition, candidate intervals, 24-hour timeline and summary statistics;
- activity-confirmation DOCX generation with DD.MM.YYYY dates and improved Ukrainian-side formatting.

## Run on Windows

1. Install Python 3.13.
2. Run `START.bat`.

The repository root contains a small launcher. The full v8.29 program source is stored in `releases/Taxo_v8_29_source.zip`; the launcher extracts it locally and starts the application.

## Data storage

The repository does **not** contain the working database. User data stays outside the program folder under:

`%USERPROFILE%\Documents\DriverWorktime\`

including the main SQLite database, backups, output files and tachograph working data.

## Notes

The tachograph recognition and Regulation №340 checks are assistance/verification tools. Recognition candidates should be reviewed before transferring them into the actual timesheet.
