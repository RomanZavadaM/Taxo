# Taxo v8.70 candidate r8 — checkpoint

Date: 2026-09-15
Base: published `main` v8.70 r7 (`7c91135297e15622bf967f109ded42c52197d172`)
Branch: `work/v8.70-personnel-timesheet-r8`

## Personnel timesheet

- The all-personnel daily timesheet now supports edit, copy day, paste to one or many dates, multi-date plan-to-actual and multi-date removal of manual entries.
- Manual actions update only `employee_time_entries`; driver schedules and personnel duty shifts remain intact as automatic plan sources.
- Empty-weekday autofill inserts an 8:00 plan only where no automatic plan and no manual row exist. It requires explicit confirmation and never invents actual hours.
- Employment and dismissal dates bound visible/collectable time. Dates outside employment are marked and excluded from totals.

## Reports and control

- Individual daily Excel/PDF reports include date, day type, plan, optional actual, deviation, source and notes.
- Personnel control identifies exact planned dates whose actual time is still missing.
- The monthly all-personnel balance shows daily actual hours/codes, plan, actual, deviation and missing-fact counts.
- Monthly personnel balance exports to editable Excel and printable A4 landscape PDF split into three date ranges.
- Every export uses the shared locked-file Retry / Create copy / Cancel workflow.

## Safety and distribution

- Database schema is unchanged from r7; no destructive migration is needed.
- Tachograph recognition, route mileage, odometer history and waybill logic are unchanged.
- Routine candidate testing uses `START.bat`; no EXE/app packaging is performed for r8.
- Source distribution contains no SQLite database, caches or personal data.
