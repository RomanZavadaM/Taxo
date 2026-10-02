# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo is a desktop application for a single transport company: personnel and drivers, schedules, work-time accounting, waybills, activity confirmation forms, vehicles, document control, reports, maintenance tracking, and selective analogue tachograph processing.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Latest integrated checkpoint in `main`:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9).  
> **Latest full multi-platform checkpoint:** [Taxo 10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1).  
> **Previous stable / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.9-r9` does not become stable automatically; stable promotion is a separate owner decision.

## Downloads

### Latest integrated checkpoint — 10.9-r9

[START 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/SHA256SUMS_v10_9_r9.txt) · [Release 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)

10.9-r9 is the latest integrated code checkpoint. It has a START package; a separate full executable set was not republished for r9.

### Latest full multi-platform checkpoint — 10.9-r1

[Release 10.9-r1 with Windows/macOS packages](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1) · [Combined SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r1/SHA256SUMS_v10_9_r1_ALL.txt)

Use a ready Windows/macOS package from `v10.9-r1` for normal operation. `START.bat` is mainly for testing and technical diagnostics; extract the START ZIP completely before running it.

User databases, SQLite files, scans, caches, and personal documents are never bundled into GitHub releases.

## Main features

- personnel and driver registry with roles and history;
- individual and periodic driver schedules;
- work-time timesheets with split shifts and explicit plan/fact separation;
- work, driving, break and rest control;
- 60-day minute-level activity register without inventing rest from unknown time;
- vehicle registry, mileage, maintenance tracking and vehicle-document control;
- regular and non-regular waybills;
- activity confirmation forms with revision history;
- analogue tachograph scans and manual verification;
- approved/signed operational orders and driver→vehicle assignment history protection;
- PDF/Excel reports;
- backups, workspace transfer, and SQLite schema compatibility control.

## Integrated in 10.9-r2 → 10.9-r9

The integrated line adds immutable waybill-number history, whole-trip vehicle-document validity checks, stronger work/rest compliance, safer activity-source priority, historical personnel/P-5 fixes, odometer and maintenance-forecast hardening, immutable approved/signed orders, and the first explicit SQLite schema baseline via `PRAGMA user_version`.

Full notes: [10.9-r9 release notes](docs/releases/RELEASE_NOTES_v10.9-r9.md) · [release index](docs/releases/RELEASE_INDEX.md).

## Government registries and military accounting

Taxo supports vehicle reconciliation with Shlyakh data, editable working values separated from immutable government snapshots, an employee-document register, lossless government XLSX import, an enterprise military-transport statement, and a local Diia-first annual personnel reconciliation workflow.

Taxo does **not** pretend to be a government API and does not claim automatic transmission to Diia, Oberih or Shlyakh.

## Documentation and development state

Canonical operational documentation is maintained in Ukrainian. Start a development/recovery session with `START_HERE.md`, then `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` and Issue #61. Issued revisions are immutable. After `10.9-r9`, the next code revision is **10.9-r10**.

See [Documentation index](docs/README.md) · [System overview](docs/SYSTEM_OVERVIEW.md) · [Product status](docs/PRODUCT_STATUS.md) · [Quick start](docs/guides/QUICK_START.md) · [Release index](docs/releases/RELEASE_INDEX.md).

## Copyright and licence

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.**

Taxo is proprietary software. Public visibility of this repository does not grant an open-source licence or permission to redistribute, sell, republish, or distribute modified/derivative versions without written permission from the copyright holder.

See [LICENSE.md](LICENSE.md), [COPYRIGHT.md](COPYRIGHT.md), and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
