# PROJECT_STATE — Taxo

**Підтверджено GitHub 27.11.2026 після публікації v10.25-r4 Test.**

## Поточні випуски

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r4), exact source `ed3b79a96659aa011f60fa7912092fbc15157cdb`, 8 assets, prerelease=true.
- **Current main:** `f1f4724910ffc1935a7f08bc4e9e27fff3224ad6`.
- **Previous Test:** v10.25-r3 — program revisions + employees + prepared DOCX.

## Current Test 10.25-r4 — event briefing + explicit conducted fact

- Separate «За подією…» action with mandatory reason.
- Shared-registry cumulative employee selection; exact program revision + frozen employee snapshots.
- Event session is independent from regular planned session.
- Optional prepared DOCX never implies conducted.
- Manual «Зафіксувати проведення…» requires factual date + paper evidence note.
- Existing conducted fact cannot be silently rewritten with another date/evidence.
- Read-only history/audit includes reason, exact program revision, frozen people, timestamps, evidence and prepared DOCX/SHA-256.
- Full backup/restore preserves event + evidence + prepared output.
- Strict live routes: open event, create event, save conducted fact, history.
- Real owner workspace was not used.
- Candidate START: 1732/1732 PASS; 4/4 r4 scenarios.
- Candidate PR #670: START #46060419818, Windows #46060419824, Win7 #46060419944, macOS #46060419876 — SUCCESS; Defender/integrity PASS.
- Exact source `ed3b79a96659aa011f60fa7912092fbc15157cdb`.
- Exact-source START #46061028041, Windows #46061028147, Win7 #46061028060, macOS #46061028199 — SUCCESS.
- Trigger PR #671 merged `f1f4724910ffc1935a7f08bc4e9e27fff3224ad6`; trigger Win7 #46061090608 attempt 2 SUCCESS after attempt 1 failed only on Defender signature-update timeout `0x80072ee2`.
- Publisher #46062424737 SUCCESS.
- `v10.25-r4`: 8 canonical assets, prerelease=true; Stable r9 unchanged.

## Next

**10.25-r5 — full Instructions end-to-end acceptance**:
- program revision;
- quarter plan;
- shared employees;
- prepared DOCX and exact output link;
- close/reopen persisted stores;
- event briefing;
- explicit manual conducted fact;
- overdue derived control;
- full backup/restore;
- state and file integrity equality;
- virtual/synthetic only; separate Test release.

Maintenance окремо: architecture #290, Feature Loss/UI #275/#556, docs-only CI #251. Draft #543/#395 лишаються open.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY and physical attachment purge remain blocked without explicit owner decision.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
