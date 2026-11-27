# PROJECT_STATE — Taxo

**Підтверджено GitHub 27.11.2026 після публікації v10.25-r5 Test.**

## Поточні випуски

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r5), exact source `70bc3c6bf88f6edfd9f1ae1865c1efb3249ec2f3`, 8 assets, prerelease=true.
- **Current main:** `2627a57d8d63313f9eaf500ef17c123d4b700f35`.
- **Previous Test:** v10.25-r4 — event briefing + explicit conducted fact.

## Інструктажі 10.25 — r1→r5

- r1: `Data/BriefingPlanning` — immutable program revisions, planned/event sessions, frozen employees, honest planned/prepared/conducted, explicit evidence, full backup/restore.
- r2: live «На цей квартал…» — quarter navigation, БДР/ОП filter, exact revision, honest derived states, small-window live control.
- r3: «Програми / план / друк…» — immutable revision UI, cumulative employee selection, deterministic planned session, exact PaperDocuments DOCX link via document_id/filename/SHA-256, prepared only.
- r4: «За подією…» — mandatory reason, exact program revision + frozen employees, optional prepared DOCX; explicit manual «Зафіксувати проведення…» with factual date + paper evidence note; immutable fact; read-only history/audit; event does not close regular planned.
- r5: full synthetic end-to-end acceptance across r1–r4, reopen, full backup/restore, state equality and file SHA-256 integrity.
- Реальна база власника для r1–r5 не використовувалась.

## Current Test 10.25-r5

- Prep START #46063110841: 1734/1734 PASS.
- Candidate START #46064508828: **1735/1735 PASS**, 3/3 r5 controls.
- Candidate #674: Windows #46064508796, Win7 #46064508832, macOS #46064508804 — SUCCESS; Defender/integrity PASS.
- Exact source `70bc3c6bf88f6edfd9f1ae1865c1efb3249ec2f3`.
- Exact-source CI: START #46065219246, Windows #46065219433, Win7 #46065219339, macOS #46065219355 — SUCCESS.
- Trigger #675 merged `2627a57d8d63313f9eaf500ef17c123d4b700f35`; publisher #46065911225 SUCCESS.
- `v10.25-r5`: 8 canonical assets, prerelease=true; Stable r9 unchanged.

## Next

Issue #237 remains OPEN until manual owner UI acceptance. After owner acceptance decide whether to close #237 and move to the next major block: unified document storage.

Maintenance remains separate: architecture #290, Feature Loss/UI #275/#556, docs-only CI #251. Draft #543/#395 remain open.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY and physical attachment purge remain blocked without explicit owner decision.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
