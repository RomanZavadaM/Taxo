# Taxo — CURRENT CHECKPOINT

Date: 2026-09-15

## Current development version

- Version: **v8.70 candidate r8**; based on published r7.
- Publication target: GitHub `main`; the old v8.65 head is superseded after verified merge.
- Previous development checkpoints remain preserved: v8.66 r10 and v8.70 r1–r3.
- r8 is an executable release checkpoint: Windows Setup/Portable, macOS arm64/x86_64, source ZIP and shared checksums are built and verified in one GitHub workflow.
- Publication branch: `work/v8.70-personnel-timesheet-r8`.

## Personnel and timekeeping

- `Працівники → Реєстр усіх працівників` stores all employees once, with personnel number, dates, position, phone, status and multiple roles.
- Existing drivers migrate automatically into the employee register and keep their driver cards and all historical links.
- Removing the `Водій` role closes the linked driver card with an end date but does not delete the employee, schedule, timesheet or waybill history.
- Existing r2 doctors/mechanics and dispatch shifts migrate into the common employee and shift tables.
- Dispatch shifts support role, exact date/time, D+ end day, location, planned hours, actual hours and overlap checks.
- The monthly personnel summary combines driver plan from `worklog` with non-driver shifts. Cross-midnight hours are allocated to the calendar month they actually occupy.
- The personnel timesheet now has monthly summary and daily views for every employee. A daily row stores day type, optional plan override, optional actual hours and notes.
- Driver schedules and personnel shifts remain automatic plan sources. A manual row supplements them and can be cleared to return to automatic data.
- Overnight personnel shifts are split between their actual calendar dates.
- The daily personnel table now supports copy/paste across selected dates, multi-date plan-to-actual and clearing, plus safe 8-hour planning for otherwise empty weekdays.
- Individual Excel/PDF reports and control identify plan, optional actual, deviations and exact missing-fact dates.
- The monthly all-personnel balance provides daily hours/codes plus plan/fact/deviation totals in the UI, editable Excel and printable PDF.

## Odometer and mileage history

- Each route may store an optional planned distance for its complete outbound/return scenario.
- The issued waybill snapshots that route plan, prints it separately from actual mileage and preserves it if the route is edited later.
- A start reading plus route plan shows a forecast end reading in the UI; the forecast is never stored as an actual reading.
- With both actual readings, deviation beyond the greater of 10 km or 10% of plan produces a warning only.
- A waybill may have optional start and/or end odometer readings; leaving both blank never blocks issue.
- Readings are stored in `vehicle_odometer_readings` per vehicle, driver, timestamp, source and source record.
- Source `waybill` is active now; the same history table is ready for future `tachograph` readings without changing recognition in r7.
- If both readings exist, the difference is calculated and printed on page two.
- A decreasing end value or a value below the previous vehicle reading produces a warning only. Data is still saved and the waybill remains issuable.

## Waybill numbering and lifecycle

- `Підприємство → Пули серій і номерів` stores series, range, next number, width, effective dates and automatic/manual mode.
- Exactly one active pool may cover a given work date. The pool is selected by work date, not print date.
- Preview does not consume a number. First issue consumes it only after successful PDF creation.
- Reprint keeps series/number and increments revision without advancing the pool.
- Annulment records its reason and does not return the number to the pool. A later issue receives a new number.
- `waybill_events` keeps issue/reprint/void history; `waybills` keeps the current document snapshot.

## Route and form № 1-АП

- Every route has an explicit start location, end location, start direction and D+ start/end day.
- Each outbound/return point stores its type (`АТП`, `Зупинка`, `Автостанція`, `Відпочинок`, `Нічліг`, `Інше`).
- Arrival and departure have independent D+ day values, so `D0 23:55 → D+1 00:40` is represented correctly.
- The primary entry path accepts two pasted Excel/text columns `Точка | Час` for both directions, automatically infers arrival/departure placement, day rollover, route endpoints and D+ bounds.
- One route that returns on the next day produces one official waybill number whose date is printed as the full interval, for example `14.09.2026 - 15.09.2026`; both dates are stored in the register.
- The reverse side prints outbound and return schedules with real calendar dates and highlights the direction where work begins. Internal D+ offsets are never printed.
- The front side prints the official series/number, route/vehicle/driver plan, start/end locations and scheduled doctor/mechanic names. Handwritten signatures and unknown actual/fuel/control fields remain blank.

## Compatibility and constraints

- Database migration is additive; no driver, vehicle, route, worklog, tachograph record or old dispatch table is deleted.
- Dates in the UI remain `ДД.ММ.РРРР`.
- Persistent data remains in `Documents/DriverWorktime`; the distribution ZIP contains no database or personal data.
- Every r8 executable job rejects bundled `.db`, `.sqlite` or `.sqlite3` files before publication.
- Tachograph recognition and the rule that tachograph facts never overwrite plan `worklog/work_segments` are unchanged.
