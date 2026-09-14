# Taxo v8.70 — Driver work schedules and waybills

[Українська](README.md) | **English** | [Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md)

Taxo is a Ukrainian-language desktop application for managing transport-company personnel, driver schedules, working-time records, routes, vehicles, activity attestation forms, bus waybills and analog tachograph records. The current consolidated version is **v8.70 r5** on the `main` branch.

## Main capabilities

- A unified employee register with personnel numbers, employment dates and multiple roles, including driver, doctor, mechanic, dispatcher and conductor.
- Driver schedules and monthly time sheets with separate planned working time and planned driving time. A working day may contain several segments.
- Route and vehicle catalogues. Each route contains one precise timetable and may start away from the depot, cross midnight, include rest or overnight stays, and finish on a later calendar day.
- A simplified route workflow: paste two columns, `Point | Time`, for the outbound and return directions. Midnight transitions and route boundaries are calculated automatically; a detailed editor remains available for exceptional cases.
- Two-page vector A4 bus waybills based on form No. 1-AP. Driver, vehicle, route and planned times are taken from the schedule. Multiday documents display real calendar dates, not internal `D+N` markers.
- Official waybill series and number pools with validity periods, automatic or manual numbering, revision history and annulment records.
- Duty schedules for doctors and mechanics. Their names can be inserted in the waybill, while handwritten signatures and unknown actual, fuel and control fields remain blank.
- Activity attestation forms in DOCX, PDF and JPG, plus backup and restore of persistent application data.
- An analog tachograph-disc workspace for scans, activity intervals and comparison of factual driving with the plan. Tachograph facts do not overwrite planned schedule data.

## Running and data storage

On Windows, the source package can be started with `START.bat`. Ready-made Windows Setup and Portable packages, as well as native macOS packages for Apple Silicon and Intel, are produced by GitHub Actions at executable checkpoints.

The application stores user data outside the program directory under `Documents/DriverWorktime`. SQLite databases and personal data are intentionally excluded from the repository and all distribution packages, so updating the program does not replace operational data.

The interface and generated official forms are currently in Ukrainian. This repository page is translated to make the project easier to review internationally.

## Project status

v8.70 r5 is the active consolidated development line. Earlier branches are retained as historical checkpoints. The application should still be validated with real company data and printed forms before operational deployment.
