# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo is a desktop system for a single transport company: personnel and drivers, schedules, work-time accounting, waybills, activity confirmation forms, vehicles, document control, maintenance, reports, and analogue tachograph checks.

> **Stable:** [Taxo 10.10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10) — 2026-10-05
> **Previous stable / rollback:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)
> **Next code revision:** `10.10-r4`

## Downloads — Taxo 10.10 (stable)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/SHA256SUMS_v10_10.txt) · [Release notes 10.10 (Ukrainian)](../releases/RELEASE_NOTES_v10_10.md) · [Release index](../releases/RELEASE_INDEX.md)

User databases, SQLite files, scans, caches, and personal documents are not included in GitHub releases. Updating does not require re-entering working data.

## What is new in 10.10

- **No PyMuPDF.** The activity confirmation form (PDF/JPG), the No. 340 report date stamp and PDF viewing/printing now use permissively licensed libraries (pypdfium2, reportlab, pypdf); output is pixel-identical to the previous version.
- **Correct version shown in the application** — window title, About dialog, PDF headers and backup manifest.
- **Backups** explicitly warn when they contain databases only.
- **Infrastructure:** obsolete publishing workflows disabled, tests isolated from working storage, license gate in every build.
- Includes the whole 10.4 … 10.9 line: vehicle document validity for the whole trip, protection of issued waybills and numbers, stronger work/rest control, 60-day register, personnel balance, maintenance, immutable signed orders, SQLite schema compatibility.

## Main capabilities

Personnel and driver history; individual and periodic schedules; plan/fact work time and split shifts; work/driving/break/rest control; 60-day activity register; vehicles, mileage, maintenance and documents; regular and non-regular waybills; activity confirmation forms; analogue tachograph checks; protected orders and driver→vehicle assignments; PDF/Excel reports; backups and SQLite compatibility control.

## Development

Canonical operational documentation is maintained in Ukrainian. Start with [`START_HERE.md`](../../START_HERE.md). After stable 10.10, new code starts at `10.10-r4` from current `main`. Issued revisions are immutable.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo is proprietary software.
