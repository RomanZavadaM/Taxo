# Taxo / Driver Worktime

🇺🇦 [Українська](../../README.md) · 🇬🇧 [English](README.en.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇫🇷 [Français](README.fr.md) · 🇰🇷 [한국어](README.ko.md) · 🇯🇵 [日本語](README.ja.md)

Taxo is a desktop system for transport companies: staff and vehicles, schedules and work time, waybills, orders, documents, maintenance, reports and backups.

## Previous Stable 10.24-r3

**10.24-r3 was promoted to Stable/Latest by the owner's explicit decision on 23 November 2026.** It contains all accepted 10.23-r4 document/order functionality plus the completed r1–r3 correspondence line: separate Incoming/Outgoing journals, safe numbering, controlled attachments, search/date/calendar, sortable tables, a letter card, create/reply/attachments/open-document actions and unsaved-change protection. A blank sent date does not mean the outgoing letter was actually sent.

Taxo currently has 37 strict live UI routes that check mapped, on-screen, usable and activatable controls. START, Windows, Windows 7 and macOS Intel/Apple Silicon checks passed; Windows/Win7 also passed Defender and package-integrity gates. Broader full-function coverage (#556) and the wider end-to-end orders audit (#553) remain open.

## Downloads

**Stable / Latest: [Taxo 10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9).** Previous stable checkpoint: [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3).

Windows 10/11 x64 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.24-r9/Taxo_v10_24_candidate_r9_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.24-r9/SHA256SUMS_v10_24_r9.txt)

**Stable / Latest:** [Taxo 10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), 8 assets, exact source `e3770aa72b0744eee192979a2e569651bac4f257`. The vehicle-document persistence and backup/restore protections described here are now the stable release.


**Current Test:** [Taxo 10.25-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r5), 8 assets, exact source `70bc3c6bf88f6edfd9f1ae1865c1efb3249ec2f3`. It is the full synthetic end-to-end acceptance of the Instructions line r1–r4: exact program revisions, planned/event sessions, prepared DOCX links and SHA-256, explicit conducted evidence, overdue control, and full backup/restore. Stable remains 10.24-r9.

## Data and documentation

Keep databases and documents in a separate working folder and back it up before updating. [User guide (Ukrainian)](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

Development starts with [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved. [LICENSE](../../LICENSE.md).
