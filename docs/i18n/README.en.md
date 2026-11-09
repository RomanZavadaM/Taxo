# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

> **Stable release:** [Taxo 10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4) · 09.11.2026 · Windows 10/11, Windows 7, macOS Intel / Apple Silicon, START verified.
> **Previous stable / rollback:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10).

## Downloads — 10.14-r4

**Windows 10/11 x64:** [Installer](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Installer](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_macOS_x86_64_Portable.zip)

**Source archive / checksums:** [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/SHA256SUMS_v10_14_r4.txt) · [Release notes (UK)](../releases/RELEASE_NOTES_v10.14-r4.md).

## What changed since 10.12-r10

Operations and maintenance navigation, bulk driver–vehicle assignments, separate personnel/work order numbering, order preview, editable Word documents and PDF/JPG, and matching document tables and headers.

Orders are working documents in Taxo: their status or paper-signature marker does not prevent corrections or deletion. Official paper originals remain under the operator's control.

Work databases, scans, personal documents and caches are excluded from release files. Back up your work folder before updating.

## Documentation and development

The canonical operational documentation is in Ukrainian. Read the quick start and the operations/maintenance guide. The next planned code revision after 10.15-r3 is 10.15-r4.

[Quick Start / Швидкий старт](../guides/QUICK_START.md) · [Operations & Maintenance / Експлуатація](../guides/OPERATIONS_STOIR_GUIDE.md) · [Release Index](../releases/RELEASE_INDEX.md) · [Current State](../../PROJECT_STATE.md).

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo is proprietary software.

## Test candidate 10.15-r3 — briefing and internship documents

Operations → Briefings now produces an editable DOCX with the full program and a separate paper signature sheet, rather than a loose CSV as the primary output. Operations also offers a driver's internship/training sheet and a searchable catalog of saved Word documents inside the workspace (included in full backup). Generating a file never confirms attendance, a signature, or authorization to drive. The optional scanned originals and hierarchical catalog are planned separately (#289); modular Python restructuring for 2–3× growth is #290. Stable release remains 10.14-r4.
