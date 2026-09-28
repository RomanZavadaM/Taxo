# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md)

Taxo is a desktop application for a single transport company: personnel and drivers, schedules, work-time accounting, waybills, activity confirmation forms, vehicles, document control, reports, and selective analogue tachograph processing.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Latest full checkpoint in `main`:** [Taxo 10.5-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8).  
> **Previous stable / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.5-r8` is a full candidate/checkpoint and does not become stable without a separate owner decision.

## 10.5-r8 downloads

[Windows x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Setup_Windows_x64.exe) · [Windows x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Windows7_x64_Portable.zip) · [macOS ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_macOS_arm64_Portable.zip) · [macOS Intel](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_macOS_x86_64_Portable.zip) · [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/SHA256SUMS_v10_5_r8.txt)

User databases, SQLite files, scans, caches, and personal documents are never bundled into GitHub releases.

## Main features

- personnel and driver registry with roles and history;
- individual and periodic driver schedules;
- work-time timesheets with split shifts and explicit plan/fact separation;
- work, driving, break and rest control;
- separate weekly balances for **60:00 work time** and **56:00 driving time**;
- 60-day minute-by-minute driver activity register;
- vehicle registry, mileage history and vehicle-document control;
- insurance, additional liability insurance, technical inspection, registration documents and tachograph inspection protocol;
- route and time scenarios;
- waybills, activity confirmation forms, PDF/Excel reports;
- analogue tachograph scans and manual verification;
- configurable workspace, backup and transfer tools.

## Registry and military-accounting work in 10.5

The 10.5 line added vehicle reconciliation with “Shlyakh” data, editable working values separated from immutable government snapshots, a unified employee-document register, lossless government XLSX import, an enterprise military-transport statement, and a local Diia-first annual personnel military-accounting reconciliation workflow.

Taxo does **not** pretend to be a government API. Local preparation is not treated as an official state fact, and the application does not claim automatic transmission to Diia, Oberih or Shlyakh.

## What changed in 10.5-r8

Windows 7 / Python 3.8 can return a shorter openpyxl error for some Shlyakh XLSX files: `unexpected keyword argument 'tabId'` without the word `ChildSheet`. r8 recognises that narrow case, retries using an in-memory compatibility copy, and never rewrites the source XLSX.

Full notes: [10.5-r8 release notes](docs/releases/RELEASE_NOTES_v10_5_r8.md).

## Documentation

The canonical operational documentation is maintained in Ukrainian:

- [Documentation index](docs/README.md)
- [System overview](docs/SYSTEM_OVERVIEW.md)
- [Quick start](docs/guides/QUICK_START.md)
- [Personnel manual](docs/guides/USER_MANUAL.md)
- [Administration and backups](docs/guides/ADMIN_GUIDE.md)
- [Troubleshooting](docs/guides/TROUBLESHOOTING.md)
- [Release index](docs/releases/RELEASE_INDEX.md)

## Development state

New sessions should start from `START_HERE.md`, then `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` and Issue #61.

Each completed development step gets a new revision `r1 … r10`; after `r10`, the minor version increases and the revision returns to `r1`. Issued revisions are immutable. After `10.5-r8`, the next code revision is **10.5-r9**.

## Copyright and licence

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.**

Taxo is proprietary software. Public visibility of this repository does not grant an open-source licence or permission to redistribute, sell, republish, or distribute modified/derivative versions without written permission from the copyright holder.

See [LICENSE.md](LICENSE.md), [COPYRIGHT.md](COPYRIGHT.md), and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
