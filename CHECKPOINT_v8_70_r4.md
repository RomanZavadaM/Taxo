# Taxo v8.70 candidate r4 checkpoint

- Date: 14.09.2026.
- Base: preserved v8.70 candidate r3 commit `cbee66a3e4366f6aa7570c05cc2ea100669222eb`.
- Added one numbered waybill for a route spanning several calendar days; the form prints a full date interval and the register stores both boundary dates.
- Added the primary `Швидко вставити обидва напрямки` route workflow.
- The minimal pasted format is `Точка | Час`; Excel tabs, semicolons and vertical bars are accepted.
- First departure, last arrival, midnight D+ rollover, route endpoints and D+ bounds are derived automatically.
- Detailed point editing, point types, rest and overnight markers remain available for exceptional rows.
- Removing the Driver role now asks for an end date, deactivates only the driver card and preserves the employee and all historical records.
- Candidate is delivered through `START.bat` and GitHub Actions Windows Setup/Portable plus native macOS arm64/x86_64 builds.
- Publication uses branch `work/v8.70-waybill-r4`; stable `main` remains unchanged until manual acceptance.
