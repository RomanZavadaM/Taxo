# PROJECT_STATE — Taxo

**Підтверджено GitHub 28.11.2026 після публікації v10.25-r6 Test.**

## Поточні випуски

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r6), exact source `f4950ddb7efcada08f8fe73a5bc9470776163462`, 8 assets, prerelease=true.
- **Current main:** `376569e8fc23b77e927892d346c35b6d6480ed87`.
- **Previous Test:** v10.25-r5 — synthetic end-to-end acceptance of Instructions r1–r4.

## Інструктажі 10.25 — r1→r6

- r1: `Data/BriefingPlanning` — immutable program revisions, planned/event sessions, frozen employees, honest planned/prepared/conducted, explicit evidence, full backup/restore.
- r2: live «На цей квартал…» — quarter navigation, БДР/ОП filter, exact revision, honest derived states, small-window live control.
- r3: «Програми / план / друк…» — immutable revision UI, cumulative employee selection, deterministic planned session, exact PaperDocuments DOCX link via document_id/filename/SHA-256, prepared only.
- r4: «За подією…» — mandatory reason, exact program revision + frozen employees, optional prepared DOCX; explicit manual conducted fact with factual date + paper evidence; immutable audit.
- r5: full synthetic end-to-end acceptance across r1–r4, reopen, full backup/restore, state equality and file SHA-256 integrity.
- r6: owner-acceptance corrections — real TemplateLibrary/CompanyTemplates → program basis, human program lines, quarterly working topics, separate event addendum, DOCX approval header/exact revision.
- Реальна база власника для r1–r6 не використовувалась автоматично.

## Current Test 10.25-r6

- Prep exact SHA `639329d8aff54020b2b1bf09be709edd13beeeaa`: START #46126867841, Windows #46126867911, Win7 #46126867844, macOS #46126867862 — SUCCESS.
- Candidate #678: START #46127530499, Windows #46127530498, Win7 #46127530508, macOS #46127530503 — SUCCESS.
- Exact product source `f4950ddb7efcada08f8fe73a5bc9470776163462`.
- Exact-source CI: START #46127933006, Windows #46127933023, Win7 #46127933027, macOS #46127932975 — SUCCESS; Defender/integrity PASS.
- Trigger #679 merged `64d664b67f84ebfb5676d45b79c37bd155191687`; publisher #46128959017 SUCCESS.
- `v10.25-r6`: 8 canonical assets, prerelease=true; Stable r9 unchanged.
- Recovery duplicate PR #680 did not create a second release; current main is its maintenance merge `376569e8fc23b77e927892d346c35b6d6480ed87`.

## Next

Issue #237 remains OPEN until repeat manual owner UI acceptance of v10.25-r6. The acceptance must cover library/company template basis, quarterly/initial/event lines, event-specific addendum, generated DOCX approval/header/revision and the prepared ≠ conducted boundary.

After owner acceptance decide whether to close #237 and move to the next major block: unified document storage.

Maintenance remains separate: architecture #290, Feature Loss/UI #275/#556, docs-only CI #251. Draft #543/#395 remain open.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY and physical attachment purge remain blocked without explicit owner decision.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
