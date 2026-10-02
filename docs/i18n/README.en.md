# Taxo / Driver Worktime

[Українська](../../README.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo is a desktop system for a single transport company: personnel and drivers, schedules, work-time accounting, waybills, activity confirmation forms, vehicles, document control, maintenance, reports, and analogue tachograph checks.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)  
> **Latest integrated checkpoint in `main`:** **Taxo 10.9-r10**  
> **Latest full multi-platform published release:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)  
> **Next code revision:** `10.10-r1`

`10.9-r10` is already integrated into `main`, but it has not been published as a separate full public multi-platform release. For ready Windows/macOS packages, use `v10.9-r9`.

## Downloads — 10.9-r9

**Windows 10/11:** [x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows_x64.exe) · [x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows_x64_Portable.zip)

**Windows 7 SP1:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_x86_64_Portable.zip)

**Testing/source:** [START 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [10.9-r10 release notes](../releases/RELEASE_NOTES_v10.9-r10.md) · [Release index](../releases/RELEASE_INDEX.md)

User databases, SQLite files, scans, caches, and personal documents are not included in GitHub releases.

## What changed in 10.9-r10

The repository was structurally cleaned up without changing business logic: runtime modules moved to `src/taxo/`, templates to `assets/`, and active packaging definitions to `packaging/`. No user-data migration was introduced.

## Main capabilities

Personnel and driver history; individual and periodic schedules; plan/fact work time and split shifts; work/driving/break/rest control; 60-day activity register; vehicles, mileage, maintenance and documents; regular and non-regular waybills; activity confirmation forms; analogue tachograph checks; protected orders and driver→vehicle assignments; PDF/Excel reports; backups and SQLite compatibility control.

## Development

Canonical operational documentation is maintained in Ukrainian. Start with [`START_HERE.md`](../../START_HERE.md). After `10.9-r10`, new code starts at `10.10-r1` from current `main`. Issued revisions are immutable.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo is proprietary software.
