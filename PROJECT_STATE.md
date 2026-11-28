# PROJECT_STATE — Taxo

**Підтверджено GitHub 28.11.2026 після публікації v10.25-r6 Test.**

## Поточні випуски

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r6), exact source `f4950ddb7efcada08f8fe73a5bc9470776163462`, 8 assets, prerelease=true.
- **Current main:** `64d664b67f84ebfb5676d45b79c37bd155191687` before the r6 docs/recovery checkpoint.
- **Previous Test:** v10.25-r5 — full synthetic Instructions r1–r4 acceptance.

## Інструктажі 10.25 — r1→r6

- r1: immutable program revisions, planned/event sessions, frozen employees, honest planned/prepared/conducted, explicit evidence, full backup/restore.
- r2: live «На цей квартал…» — quarter navigation, БДР/ОП filter, exact revision, derived states, small-window control.
- r3: «Програми / план / друк…» — revisions, cumulative employee selection, planned session, exact PaperDocuments DOCX link via document_id/filename/SHA-256.
- r4: «За подією…» + explicit manual conducted fact with factual date/paper evidence; event does not close regular planned.
- r5: full synthetic end-to-end r1–r4 acceptance, reopen, full backup/restore, equality/SHA-256, post-restore idempotency.
- r6: manual-acceptance fixes — real TemplateLibrary/CompanyTemplates program bases, human-readable program lines, editable I–IV quarter working themes, event-specific addendum, improved DOCX approval header/exact revision.
- Реальна база власника для r1–r6 не використовувалась.

## Current Test 10.25-r6

- Prep: START #46126867841; Windows #46126867911; Win7 #46126867844; macOS #46126867862 — SUCCESS.
- Candidate: START #46127530499 — 1743 tests PASS; Windows #46127530498; Win7 #46127530508; macOS #46127530503 — SUCCESS.
- Exact source `f4950ddb7efcada08f8fe73a5bc9470776163462`.
- Exact-source CI: START #46127933006; Windows #46127933023; Win7 #46127933027; macOS #46127932975 — SUCCESS; Defender/integrity PASS.
- Release trigger #679 merged `64d664b67f84ebfb5676d45b79c37bd155191687`; publisher #46128959017 SUCCESS.
- `v10.25-r6`: 8 canonical assets, prerelease=true; Stable r9 unchanged.

## Next

Issue #237 remains OPEN until repeated manual owner UI acceptance of r6. Focus: real library template → program basis; annual/quarter lines; event addendum; approval-quality DOCX; previous r5 workflows and reopen/small-window behavior. After owner acceptance decide whether to close #237 and move to unified document storage.

Maintenance remains separate: architecture #290, Feature Loss/UI #275/#556, docs-only CI #251. Draft #543/#395 remain open.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY and physical attachment purge remain blocked without explicit owner decision.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
