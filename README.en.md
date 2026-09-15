# Taxo v8.70 — Driver work schedules and waybills

[Українська](README.md) | **English** | [Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md)

Taxo is a Ukrainian-language desktop application for managing transport-company personnel, driver schedules, working-time records, routes, vehicles, activity attestation forms, bus waybills and analog tachograph records. The current development candidate is **v8.70 r9**.

## Main capabilities

- A unified employee register with personnel numbers, employment dates and multiple roles, including driver, doctor, mechanic, dispatcher and conductor.
- Driver schedules and monthly time sheets with separate planned working time and planned driving time. A working day may contain several segments.
- Route and vehicle catalogues. Each route contains one precise timetable and may start away from the depot, cross midnight, include rest or overnight stays, and finish on a later calendar day.
- A simplified route workflow: paste two columns, `Point | Time`, for the outbound and return directions. Midnight transitions and route boundaries are calculated automatically; a detailed editor remains available for exceptional cases.
- Two-page vector A4 bus waybills based on form No. 1-AP. Driver, vehicle, route and planned times are taken from the schedule. Multiday documents display real calendar dates, not internal `D+N` markers.
- Official waybill series and number pools with validity periods, automatic or manual numbering, revision history and annulment records.
- Duty schedules for doctors and mechanics. Their names can be inserted in the waybill, while handwritten signatures and unknown actual, fuel and control fields remain blank.
- A full personnel timesheet with day copy/paste to multiple dates, bulk plan-to-actual and clear actions, safe eight-hour planning for empty weekdays, individual Excel/PDF reports, plan/actual control and a printable/editable monthly balance for all employees. Overnight shifts are split between calendar days.
- Optional start/end odometer readings on waybills. Readings are printed, accumulated per vehicle and used for non-blocking consistency warnings; the history is ready for a future `tachograph` data source.
- Each complete route scenario may have an optional planned distance. It is printed as the waybill plan, forecasts the ending odometer reading and gives a non-blocking warning when actual mileage differs by more than 10 km or 10%.
- Activity attestation forms in DOCX, PDF and JPG, plus backup and restore of persistent application data.
- An analog tachograph-disc workspace for scans, activity intervals and comparison of factual driving with the plan. Tachograph facts do not overwrite planned schedule data.
- Configurable local, network/NAS or cloud-synchronized workspaces. Both databases, scans, backups, generated documents and logs move together; a shared lock enforces sequential use by multiple installed copies.

## Running and data storage

On Windows, the source package can be started with `START.bat`. Ready-made Windows Setup and Portable packages, as well as native macOS packages for Apple Silicon and Intel, are produced by GitHub Actions at executable checkpoints.

The current Windows Setup, Portable ZIP, source ZIP and SHA-256 checksums are available from [GitHub Release v8.70](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70).

The default is `Documents/DriverWorktime`. Use `File → Working storage…` to migrate all data safely or attach an existing shared workspace. SQLite databases and personal data are intentionally excluded from the repository and every distribution package.

The interface and generated official forms are currently in Ukrainian. This repository page is translated to make the project easier to review internationally.

## Project status

v8.70 r9 is the active development candidate on top of the published r8 baseline. Earlier branches are retained as historical checkpoints. The application should still be validated with real company data and printed forms before operational deployment.
