# PROJECT_STATE — Taxo

**Підтверджено GitHub 27.11.2026 після публікації v10.25-r1 Test.**

## Поточні випуски

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r1), exact source `2e0a0df392b5b79b6e2efbf1793df470bf6623f8`, 8 assets, prerelease=true.
- **Current main:** `44e20e7bac1803afb1b9853a821c60e6154780db`.
- **Previous Test:** v10.24-r10 — Orders closeout.

## Current Test 10.25-r1 — Instructions planning core

- `Data/BriefingPlanning/planning.json`, format `taxo.briefing-planning.v1`.
- Immutable versioned programs; planned/event sessions; frozen participant snapshots.
- Unique planned `planning_key`; event reason required.
- Honest states: prepared/print ≠ conducted.
- Conducted requires explicit factual date + paper evidence note.
- Event does not close regular planned session.
- Overdue is derived state, not an automatic historical write.
- Fail-closed JSON validation and program-revision references.
- Full workspace backup/restore preserves the store.
- Real owner workspace was not used.
- Candidate START: 1718/1718 PASS, 4/4 r1 scenarios.
- Candidate PR #658 CI: START #46027162850, Windows #46027162761, Win7 #46027162706, macOS #46027162770 — SUCCESS; Defender/integrity PASS.
- Exact source `2e0a0df392b5b79b6e2efbf1793df470bf6623f8`.
- Exact-source CI: START #46028063211, Windows #46028063203, Win7 #46028063190, macOS #46028062948 — SUCCESS.
- Trigger PR #659 merged `44e20e7bac1803afb1b9853a821c60e6154780db`; publisher #46032557836 SUCCESS.
- `v10.25-r1`: 8 canonical assets, prerelease=true; Stable r9 unchanged.

## Next

**10.25-r2 — «На цей квартал»**: quarter selector; planned/prepared/overdue/conducted; БДР/ОП filter; exact program revision; idempotent plan generation; small-window/live-route checks; virtual-only tests; separate Test release.

Maintenance окремо: architecture #290, Feature Loss/UI #275/#556, docs-only CI #251. Draft #543/#395 лишаються open.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY and physical attachment purge remain blocked without explicit owner decision.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
