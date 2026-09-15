# Taxo v8.70 candidate r6 — checkpoint

Date: 2026-09-15
Base: published `main` v8.70 r5 (`e7b40709a07abb8721576280bd8c7b3111370f57`)
Branch: `work/v8.70-personnel-odometer-r6`

## Personnel timekeeping

- `employee_time_entries` stores one optional manual daily row per employee.
- The monthly summary and daily register cover every employee, not only drivers.
- Automatic plan sources are kept: driver `worklog/work_segments` and `employee_shifts`.
- Daily manual plan may override the automatic plan; actual hours and notes are optional.
- `План → факт` quickly confirms a day; clearing the manual row restores automatic values.
- Overnight personnel shifts are allocated to the calendar dates they actually occupy.

## Odometer history

- `vehicle_odometer_readings` stores vehicle, driver, work date, timestamp, reading kind, kilometres, source and source id.
- Waybill start/end readings are optional and may be entered before or after issue.
- The waybill snapshot stores start, end and calculated distance; page two prints available values.
- Consistency checks are warning-only: end below start, or a new reading below the previous vehicle reading.
- The source model is ready for future tachograph readings; tachograph recognition itself is unchanged in r6.

## Safety and distribution

- Database migration is additive and does not delete existing records.
- No user database or personal data is included in the source checkpoint.
- Routine candidate testing uses `START.bat`.
- Windows/macOS executable creation is manual-only; normal GitHub changes run source compilation and tests without packaging.
