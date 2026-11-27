# PROJECT_STATE — Taxo

**Підтверджено GitHub 27.11.2026 після публікації v10.24-r10 Test.**

## Поточні випуски

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, draft=false, GitHub Latest.
- **Current Test:** [v10.24-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r10), exact issued source `2e35cea72b46ac9c032966e9def195fc306834a5`, 8 canonical assets, prerelease=true, draft=false.
- **Current main:** `71fe07ed0920cfe94e27d41de53f07e92cccc795`; post-source changes are release/CI maintenance only.
- **Previous Stable:** v10.24-r3.

## Stable 10.24-r9

- Нові/замінені копії документів ТЗ є Taxo-owned files у `Data/VehicleDocuments` із source path, size та SHA-256.
- UI/open перевіряють фактичний файл; selected backup/restore перевіряє bytes, включно з archived records.
- Історичні bytes, яких уже немає у workspace/source/old backup, із SQLite не відновлюються.
- Issue #642 closed completed після isolated virtual acceptance: 1712/1712 PASS; 6/6 dedicated vehicle-document scenarios PASS.

## Current Test 10.24-r10 — Orders closeout

- Roadmap: `docs/planning/ROADMAP_AFTER_10_24_R9_2026-11-27.md`.
- r10 не додає нових бізнес-правил наказів; він збирає попередні гарантії в один synthetic end-to-end gate.
- Перевірено: ordinary order participants/vehicles; edit role/note preserving frozen snapshot; remove/re-add; assignment bulk/edit/delete/re-add; DB reopen; Draft→Active; DOCX/PDF/JPG; full backup with Output; restore to clean workspace; DB equality; file SHA-256 equality.
- Final exact-source START: 1714/1714 PASS.
- Exact-source CI: START #46021196420, Windows #46021196370, Win7 #46021196472, macOS Intel/ARM #46021196428 — SUCCESS; Defender/integrity PASS.
- Candidate PR #654 → exact issued source `2e35cea72b46ac9c032966e9def195fc306834a5`.
- Trigger PR #655 merged `71fe07ed0920cfe94e27d41de53f07e92cccc795`; publisher #46023586194 SUCCESS.
- `v10.24-r10`: 8 canonical assets, prerelease=true; Stable r9 unchanged.
- #553 remains OPEN until owner UI acceptance. #556/#562 remain open.

## Next product line

**10.25-r1 — Instructions foundation** (Issue #237):
- versioned briefing/program definitions;
- planned vs event briefing records;
- duplicate prevention and immutable history;
- honest states: print/prepared ≠ conducted/signed;
- target employees/groups from shared registries;
- synthetic backup/restore from the first slice;
- virtual-only tests and separate Test release at stage completion.

Maintenance is separate: architecture #290, Feature Loss/UI #275/#556, docs-only CI #251. Do not mix these into business revisions unless required to keep the release path safe.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY and physical attachment purge remain blocked without explicit owner decision. Draft #543/#395 remain open.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
