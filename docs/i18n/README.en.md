# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo is a desktop system for a single transport company: personnel and drivers, schedules, work-time accounting, waybills, activity confirmation forms, vehicles, document control, maintenance, reports, and analogue tachograph checks.

> **Stable:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10) — verified on real data
> **Previous stable / rollback:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)
> **Current candidate:** **10.10-r4** — successfully built for Windows 10/11, Windows 7, macOS Intel and Apple Silicon; not published yet

## Downloads — Taxo 10.9-r10 (stable)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/SHA256SUMS_v10_9_r10.txt) · [Release notes 10.9-r10 (Ukrainian)](../releases/RELEASE_NOTES_v10.9-r10.md) · [Release index](../releases/RELEASE_INDEX.md)

User databases, SQLite files, scans, caches, and personal documents are not included in GitHub releases. Updating does not require re-entering working data.

## What stable 10.9-r10 contains

- permanent history of issued waybills and numbers; retention never deletes linked facts
- vehicle document validity for the whole planned trip
- stronger work/rest control: overlaps, 3+9, weekly and two-week rest
- 60-day register without invented rest; factual sources take priority
- personnel balance / P-5, 2/2 and 3/3 regimes
- maintenance: odometer chronology and service forecast
- approved/signed orders and driver→vehicle assignments are immutable
- SQLite schema compatibility control
- structured code layout without business-logic changes

## Test versions (not stable)

[10.10-r1 … r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) are published prereleases. **10.10-r4** fixes stale version numbers across all application windows and restores the Windows 7 installer. Windows, Win7, macOS Intel and macOS ARM builds all pass. Publication is still pending.

## Development

Canonical operational documentation is maintained in Ukrainian. Start with [`START_HERE.md`](../../START_HERE.md). After 10.10-r4 is merged, `main` will contain the current 10.10 test line; the next code revision will be `10.10-r5`.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo is proprietary software.
