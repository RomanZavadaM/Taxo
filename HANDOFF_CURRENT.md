# HANDOFF_CURRENT — Taxo

**27.11.2026 — Stable/Latest = 10.24-r9; Current Test = 10.24-r10.**

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.24-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r10), exact issued source `2e35cea72b46ac9c032966e9def195fc306834a5`, 8 canonical assets, prerelease=true.
- Current main after release-maintenance: `71fe07ed0920cfe94e27d41de53f07e92cccc795`. The two commits after the issued r10 source only pin reproducible CI dependencies/runtime and arm the publisher; they are not the r10 release source.

## 10.24-r10 — завершено

- Власник затвердив правило: усі наступні етапи тестуються тільки на virtual/synthetic workspace; після кожного завершеного етапу публікується окремий GitHub Test release.
- Зафіксовано roadmap: `docs/planning/ROADMAP_AFTER_10_24_R9_2026-11-27.md`.
- r10 закриває віртуальне наскрізне приймання контуру «Накази / Учасники / ТЗ»: ordinary order + employees/vehicles, role/note edit із незмінним frozen snapshot, remove/re-add; assignment order + bulk/edit/delete/re-add; DB reopen; Draft→Active; DOCX/PDF/JPG; full backup з Output → restore у чистий workspace → DB equality + SHA-256 готових файлів.
- Prep isolated gate: 1713/1713 PASS.
- Final candidate/exact-source gate: **1714/1714 PASS**.
- Exact-source CI: START #46021196420, Windows #46021196370, Win7 #46021196472, macOS Intel/ARM #46021196428 — SUCCESS; Defender/integrity PASS.
- Candidate PR #654 merged; exact issued source `2e35cea72b46ac9c032966e9def195fc306834a5`.
- Release trigger PR #655 merged `71fe07ed0920cfe94e27d41de53f07e92cccc795`; publisher #46023586194 SUCCESS.
- Release `v10.24-r10`: 8 assets, prerelease=true, draft=false, target = exact issued source.
- #553 лишається OPEN до ручного owner acceptance UI; автоматичний Test release не підміняє ручне приймання.
- #556 і #562 лишаються окремими відкритими acceptance/audit задачами.
- Під час release-maintenance прибрано випадковість CI: main тепер pin-ить `lxml==6.1.3`, а START CI явно використовує Python 3.13. Це сталося після exact r10 source і не змінює виданий r10.

## Що далі

**Наступний продуктовий етап — 10.25-r1: фундамент системи Інструктажів БДР / охорони праці / стажування.**

Почати з Issue #237 та окремого execution plan. Перший slice: versioned programs + planned/event briefing records + dedup/history/status semantics + synthetic backup/restore. Друк не означає «проведено», позаплановий не закриває плановий, паперові підписи лишаються фактичним підтвердженням.

Після завершення 10.25-r1: virtual/synthetic acceptance → full CI → окремий GitHub Test release. Stable 10.24-r9 не змінювати без окремого прямого рішення власника.

Draft #543/#395 не закривати автоматично. Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не починати без окремого рішення власника.

Recovery: `START_HERE.md → HANDOFF_CURRENT.md → PROJECT_STATE.md → private profile/taxo → live GitHub → ROADMAP_AFTER_10_24_R9_2026-11-27.md`.
