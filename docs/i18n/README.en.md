# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo is a desktop system for a single transport company: personnel and drivers, schedules, work-time accounting, waybills, activity confirmation forms, vehicles, document control, maintenance, reports, and analogue tachograph checks.

> **Stable:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10) — approved by the owner as stable; exact r10 checkpoint verified on Windows 10/11, Windows 7, macOS Intel and Apple Silicon
> **Superseded:** [Taxo 10.10-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r4) — not recommended for macOS because of a confirmed startup failure
> **Previous stable / rollback:** [Taxo 10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5)
> **Older rollback:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10)
> **Older rollback:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)

## Downloads — Taxo 10.9-r10 (previous stable / rollback)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/SHA256SUMS_v10_9_r10.txt) · [Release notes 10.9-r10 (Ukrainian)](../releases/RELEASE_NOTES_v10.9-r10.md) · [Release index](../releases/RELEASE_INDEX.md)

## Downloads — Taxo 10.12-r10 (stable)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/SHA256SUMS_v10_12_r10.txt) · [Release notes 10.12-r10 (Ukrainian)](../releases/RELEASE_NOTES_v10.12-r10.md)

User databases, SQLite files, scans, caches, and personal documents are not included in GitHub releases. Updating does not require re-entering working data.

## What previous stable 10.9-r10 contains

- permanent history of issued waybills and numbers; retention never deletes linked facts
- vehicle document validity for the whole planned trip
- stronger work/rest control: overlaps, 3+9, weekly and two-week rest
- 60-day register without invented rest; factual sources take priority
- personnel balance / P-5, 2/2 and 3/3 regimes
- maintenance: odometer chronology and service forecast
- approved/signed orders and driver→vehicle assignments are immutable
- SQLite schema compatibility control
- structured code layout without business-logic changes

## 10.10 line

[10.10-r1 … r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) are earlier prereleases. [**10.10-r5**](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) fixed the macOS startup issue and is now the previous stable / rollback. **10.12-r10 is the current stable release**.

## Development

Canonical operational documentation is maintained in Ukrainian. Start with [`START_HERE.md`](../../START_HERE.md). The current stable is `10.12-r10`; newer `10.13-r1` is integrated in `main` but is not stable. The next code revision is `10.13-r2`.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo is proprietary software.
