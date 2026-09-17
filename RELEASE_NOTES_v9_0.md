# Taxo 9.0

Taxo 9.0 is the new stable baseline after the verified v8.70 candidate line.

## Main changes

- Added a standalone **60-day driver activity register** with minute-by-minute coverage of every calendar day.
- The register separates driving, other work, availability, breaks, rest, absence and undefined time and checks every day to exactly **24:00**.
- Tachograph/manual facts, automatic recognition, timesheet data, confirmation forms and calculated intervals are clearly identified by source; missing information remains **«Невизначено»**.
- The single-driver **№340 / weekly work-time control** keeps work time and driving time separate: **60:00 work-time limit** and **56:00 driving-time limit**.
- Added a **driver selector directly inside the №340 / 60-hour balance window**.
- Added an editable **report formation date** to both the №340 PDF and the 60-day activity-register PDF.
- The №340 PDF can be generated and opened directly from the analysis window.
- Preserves the configurable shared workspace, timesheets, route planning, vehicle/odometer history, waybill workflow and tachograph modules from the verified v8.70 line.

## Distribution

The v9.0 release publishes:

- `Taxo_v9_0_START.zip` — source/start package for routine checking via `START.bat`;
- `Taxo_v9_0_Setup_Windows_x64.exe`;
- `Taxo_v9_0_Windows_x64_Portable.zip`;
- `Taxo_v9_0_macOS_arm64_Portable.zip`;
- `Taxo_v9_0_macOS_x86_64_Portable.zip`;
- `SHA256SUMS_v9_0.txt`.

User databases, scans and personal/business data are **not included** in release packages. Existing workspace data remains separate from the program version.
