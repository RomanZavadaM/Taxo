# Taxo v8.70 consolidated r5 checkpoint

- Date: 14.09.2026.
- Base: verified v8.70 candidate r4 commit `14b93fe2ace84a9ca2ea76e6bc456fc278e7c9ca`.
- Consolidates the preserved v8.66 r10 UI line and v8.70 r1-r4 personnel, numbering, route and waybill work into the active `main` branch.
- A route may span several calendar days while retaining one official waybill number.
- The form header prints the complete date interval, for example `14.09.2026 - 15.09.2026`.
- Planned departure, planned return and every second-page schedule row print actual calendar dates. Internal `D+N` offsets remain an editor/calculation detail and never appear in the PDF.
- The primary route entry remains the two-column `Точка | Час` paste workflow; the detailed editor is retained for exceptional stops, rest and overnight records.
- Driver-role completion preserves the employee, other roles and all historical records.
- Publication branch: `work/v8.70-consolidated-r5`; after checks, merge target is `main`.
- Distribution: `START.bat`, Windows Setup/Portable and native macOS arm64/x86_64 packages. No user database is bundled.
