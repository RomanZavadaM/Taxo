# Taxo / Driver Worktime

🇺🇦 [Українська](../../README.md) · 🇬🇧 [English](README.en.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇫🇷 [Français](README.fr.md) · 🇰🇷 [한국어](README.ko.md) · 🇯🇵 [日本語](README.ja.md)

Taxo is a desktop system for transport companies: staff and vehicles, schedules and work time, waybills, orders, documents, maintenance, reports and backups.

## Stable 10.23-r4

**10.23-r4 was manually accepted by the owner on 20 November 2026 and is Stable/Latest.** It includes document search/filtering/sorting, type/date trees and nested custom folders, controlled Word revisions, PDF/print, DocumentVault, optional paper scans and separate paper-signature status. Orders support explicit driver–vehicle pairs, editing existing pairs, participant role/note editing and persistent multi-selection while searching. Document work areas and catalog tree width are resizable. The order preview now keeps DOCX/PDF/JPG actions reachable in narrow windows, including 760×560.

Taxo currently has 37 strict live UI routes that check mapped, on-screen, usable and activatable controls. START, Windows, Windows 7 and macOS Intel/Apple Silicon checks passed; Windows/Win7 also passed Defender and package-integrity gates. Broader full-function coverage (#556) and the wider end-to-end orders audit (#553) remain open.

## Downloads

**Stable / Latest: [Taxo 10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4).** Previous stable checkpoint: [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1).

Windows 10/11 x64 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/SHA256SUMS_v10_23_r4.txt)

**Current Test:** [Taxo 10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), prerelease, 8 assets, exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`. The correspondence module now has a dedicated journal/card UI on top of the r1 registry and r2 controlled attachments: Incoming/Outgoing tabs, search, date/calendar controls, sortable tables, a selected-letter card, create/reply/attachments/open-document actions and unsaved-change protection. A blank sent date does not mark outgoing correspondence as sent, and attachments do not imply sent/received/delivered/signed. Stable/Latest remains 10.23-r4.

## Data and documentation

Keep databases and documents in a separate working folder and back it up before updating. [User guide (Ukrainian)](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

Development starts with [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved. [LICENSE](../../LICENSE.md).
