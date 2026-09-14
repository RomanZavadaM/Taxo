# Taxo — CURRENT CHECKPOINT

Date: 2026-09-14

## Current candidate

- Version: **v8.70 candidate r3**.
- Stable published baseline: **v8.65**, GitHub `main` commit `f9101c1a41d7c036bade5ce66989171399189d4b`.
- Previous development checkpoints remain preserved: v8.66 r10, v8.70 r1 and v8.70 r2.
- Distribution for testing: source package with `START.bat`, Windows Setup/Portable and native macOS arm64/x86_64 candidate artifacts.
- Publication branch: `work/v8.70-waybill-r3`; stable `main` remains unchanged until manual acceptance.

## Personnel and timekeeping

- `Працівники → Реєстр усіх працівників` stores all employees once, with personnel number, dates, position, phone, status and multiple roles.
- Existing drivers migrate automatically into the employee register and keep their driver cards and all historical links.
- Existing r2 doctors/mechanics and dispatch shifts migrate into the common employee and shift tables.
- Dispatch shifts support role, exact date/time, D+ end day, location, planned hours, actual hours and overlap checks.
- The monthly personnel summary combines driver plan from `worklog` with non-driver shifts. Cross-midnight hours are allocated to the calendar month they actually occupy.

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
- The reverse side prints outbound and return schedules with day markers and highlights the direction where work begins.
- The front side prints the official series/number, route/vehicle/driver plan, start/end locations and scheduled doctor/mechanic names. Handwritten signatures and unknown actual/fuel/control fields remain blank.

## Compatibility and constraints

- Database migration is additive; no driver, vehicle, route, worklog, tachograph record or old dispatch table is deleted.
- Dates in the UI remain `ДД.ММ.РРРР`.
- Persistent data remains in `Documents/DriverWorktime`; the distribution ZIP contains no database or personal data.
- Tachograph recognition and the rule that tachograph facts never overwrite plan `worklog/work_segments` are unchanged.
