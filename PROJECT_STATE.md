# PROJECT_STATE — Taxo

**Підтверджено GitHub 27.11.2026 після публікації v10.25-r3 Test.**

## Поточні випуски

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r3), exact source `0c76b38b3aa3970245f430bee2bde7b5c062c5dd`, 8 assets, prerelease=true.
- **Current main:** `8f8dc5ef52db6bdecba4adee7d9ab4f7d77dc4a6`.
- **Previous Test:** v10.25-r2 — «На цей квартал».
- **Earlier Test:** v10.25-r1 — Instructions planning core.

## Current Test 10.25-r3 — program revisions + employees + prepared DOCX

- `briefing_planning_ui.py`: create program, append immutable revision, read-only history.
- Employee source = shared active employee registry; cumulative search/multi-select preserves identity.
- Planned session stores frozen employee snapshots.
- Deterministic plan identity prevents same program/revision/date/people set from duplicating.
- Exact program revision is rendered through existing PaperDocuments DOCX path.
- `Data/BriefingPreparedOutputs` links session → exact document_id / filename / SHA-256 without changing r1/r2 planning.json format.
- Repeated prepare reuses the linked verified DOCX; missing/tampered DOCX fails closed.
- Successful preparation records only `prepared`; never automatic `conducted`, signature or paper fact.
- Full backup/restore preserves planning + links + DOCX bytes.
- Strict live routes: planning window, new revision, prepare planned DOCX.
- Real owner workspace was not used.
- Prep final START: 1727/1727 PASS; candidate START: 1728/1728 PASS.
- Candidate PR #666: START #46052184007, Windows #46052183718, Win7 #46052183685, macOS #46052183788 — SUCCESS; Defender/integrity PASS.
- Exact source `0c76b38b3aa3970245f430bee2bde7b5c062c5dd`.
- Exact-source START #46052986259, Windows #46052986192, macOS #46052986186 — SUCCESS.
- Exact Win7 #46052986213 attempt 2 — SUCCESS after attempt 1 failed only on Defender signature-update network timeout `0x80072ee2`; no malware detection.
- Trigger PR #667 merged `8f8dc5ef52db6bdecba4adee7d9ab4f7d77dc4a6`; publisher #46054871091 SUCCESS.
- `v10.25-r3`: 8 canonical assets, prerelease=true; Stable r9 unchanged.

## Next

**10.25-r4 — event briefing + explicit conducted fact**:
- separate «За подією» action;
- required factual reason;
- event does not close regular planned session;
- explicit manual «Зафіксувати проведення» with factual date + evidence note;
- history/audit and strict live controls;
- never infer conducted from prepared DOCX, scan or signature flag;
- virtual-only tests and separate Test release.

Maintenance окремо: architecture #290, Feature Loss/UI #275/#556, docs-only CI #251. Draft #543/#395 лишаються open.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY and physical attachment purge remain blocked without explicit owner decision.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
