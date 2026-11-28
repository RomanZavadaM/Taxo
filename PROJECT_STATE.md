# PROJECT_STATE — Taxo

**Підтверджено GitHub 28.11.2026 після публікації v10.25-r7 Test.**

## Поточні випуски

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r7), exact source `76f2f7c8868154374457dc7c094a2c25ed2547d2`, 8 assets, prerelease=true.
- **Release-trigger main:** `d5ee59f84fbc3d1d28e835978ca3eff87ee9555a` before the r7 docs/recovery checkpoint.
- **Previous Test:** v10.25-r6 — TemplateLibrary/program-lines/event-addendum/DOCX acceptance fixes.

## Інструктажі 10.25 — r1→r7

- r1: immutable program revisions, planned/event sessions, frozen employees, honest planned/prepared/conducted, explicit evidence, full backup/restore.
- r2: live «На цей квартал…» — quarter navigation, БДР/ОП filter, exact revision, derived states, small-window control.
- r3: «Програми / план / друк…» — revisions, cumulative employee selection, planned session, exact PaperDocuments DOCX link via document_id/filename/SHA-256.
- r4: «За подією…» + explicit manual conducted fact with factual date/paper evidence; event does not close regular planned.
- r5: full synthetic end-to-end r1–r4 acceptance, reopen, full backup/restore, equality/SHA-256, post-restore idempotency.
- r6: real TemplateLibrary/CompanyTemplates program bases, human program lines, editable I–IV quarter working themes, event-specific addendum, improved DOCX approval header/exact revision.
- r7: existing company copy opens instead of error; direct fill/prepare workflow; human library kinds; company signer suggestion for new program; A4 DOCX; signature sheet uses position instead of internal number; human `rN` revision on new path.
- Реальна база власника для r1–r7 автоматичними тестами не використовувалась.

## Current Test 10.25-r7

- Candidate exact head `8498b91f794a402d13ef2b6c2f855e5694003730`: START #46149046990 — 1749 tests PASS; Windows #46149046880; Win7 #46149046913; macOS #46149046865 — SUCCESS; Defender/integrity PASS.
- Exact source `76f2f7c8868154374457dc7c094a2c25ed2547d2`: START #46149545768 — 1749 tests PASS; Windows #46149545770; Win7 #46149545728; macOS #46149545741 — SUCCESS; Defender/integrity PASS.
- Product PR #683 merged; release trigger #684 merged `d5ee59f84fbc3d1d28e835978ca3eff87ee9555a`; publisher #46150624080 SUCCESS.
- `v10.25-r7`: 8 canonical assets, prerelease=true, draft=false, exact target `76f2f7c8868154374457dc7c094a2c25ed2547d2`. Stable r9 unchanged.

## Next

Issue #237 remains OPEN until manual owner UI acceptance of r7. Focus: existing-copy open path; fill/prepare path and field guidance; human template kinds; approver suggestion; A4/signature-sheet/revision output; regression of r6/r5 briefing workflows. **Unified document storage remains not started.**

Maintenance remains separate: architecture #290, Feature Loss/UI #275/#556, docs-only CI #251. Draft #543/#395 remain open.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY and physical attachment purge remain blocked without explicit owner decision.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
