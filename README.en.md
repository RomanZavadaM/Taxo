# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md)

Taxo is a desktop application for a single transport company: personnel and drivers, schedules, work-time accounting, waybills, activity confirmation forms, vehicles, document control, reports, and selective analogue tachograph processing.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Latest full checkpoint in `main`:** [Taxo 10.6-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3).  
> **Previous stable / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.6-r3` is a full candidate/checkpoint and does not become stable without a separate owner decision.

## 10.6-r3 downloads

[Windows x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Setup_Windows_x64.exe) · [Windows x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Windows7_x64_Portable.zip) · [macOS ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_macOS_arm64_Portable.zip) · [macOS Intel](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_macOS_x86_64_Portable.zip) · [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/SHA256SUMS_v10_6_r3_FULL.txt)

User databases, SQLite files, scans, caches, and personal documents are never bundled into GitHub releases.

## Main features

- personnel and driver registry with roles and history;
- individual and periodic driver schedules;
- work-time timesheets with split shifts and explicit plan/fact separation;
- work, driving, break and rest control;
- separate weekly balances for **60:00 work time** and **56:00 driving time**;
- vehicle registry, mileage history and document control;
- regular routes plus non-regular work such as orders, shuttle/employee transport, city, regional and interregional trips;
- waybills, activity confirmation forms and PDF/Excel reports;
- analogue tachograph scans and manual verification;
- configurable workspace, backups and transfer tools.

## 10.6-r3 checkpoint

The checkpoint includes the plan/fact audit correction, default hiding of inactive vehicles in the vehicle-document register, non-regular waybill issuance without requiring a catalogue `route_id`, and an adaptive About window. For non-regular trips Taxo keeps the route table blank while preserving doctor/mechanic, odometer and actual mileage fields when real source data exists. Missing facts are not invented from the plan.

Full notes: [10.6-r3 release notes](docs/releases/RELEASE_NOTES_v10_6_r3.md).

## Government registries and military accounting

Taxo supports vehicle reconciliation with Shlyakh data, editable working values separated from immutable government snapshots, an employee-document register, lossless government XLSX import, an enterprise military-transport statement, and a local Diia-first annual personnel reconciliation workflow.

Taxo does **not** pretend to be a government API. Local preparation is not treated as an official state fact, and the application does not claim automatic transmission to Diia, Oberih or Shlyakh.

## Documentation and development state

Canonical operational documentation is maintained in Ukrainian. Start a development/recovery session with `START_HERE.md`, then `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` and Issue #61. Issued revisions are immutable. After `10.6-r3`, the next code revision is **10.6-r4**.

See [Documentation index](docs/README.md) · [System overview](docs/SYSTEM_OVERVIEW.md) · [Quick start](docs/guides/QUICK_START.md) · [Release index](docs/releases/RELEASE_INDEX.md).

## Copyright and licence

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.**

Taxo is proprietary software. Public visibility of this repository does not grant an open-source licence or permission to redistribute, sell, republish, or distribute modified/derivative versions without written permission from the copyright holder.

See [LICENSE.md](LICENSE.md), [COPYRIGHT.md](COPYRIGHT.md), and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
