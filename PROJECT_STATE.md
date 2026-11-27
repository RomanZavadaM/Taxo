# PROJECT_STATE — Taxo

**Підтверджено GitHub 27.11.2026 після публікації v10.25-r2 Test.**

## Поточні випуски

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r2), exact source `f013e244ad42c9d5c101b5c5eacf4f55738fadbd`, 8 assets, prerelease=true.
- **Current main:** `460484945159ee3dc433c3f4f6b986a2c9872d73`.
- **Previous Test:** v10.25-r1 — Instructions planning core.
- **Earlier Test:** v10.24-r10 — Orders closeout.

## Current Test 10.25-r2 — «На цей квартал»

- Quarter service `briefing_quarter_view.py` over r1 immutable planning store.
- Live button/window «На цей квартал…».
- Quarter prev/next, direction filter, date/kind/mode/program/people/status table.
- Exact session → exact program revision view.
- Honest status semantics; prepared ≠ conducted; event does not close planned.
- Derived overdue does not write history.
- Idempotent explicit plan generation by planning_key; conflicts fail closed.
- Stable live hook to opened quarter window.
- Strict route `operations.instructions_quarter`; small-window activation at 780×540.
- Real owner workspace was not used.
- Candidate START: 1722/1722 PASS, 4/4 r2 scenarios.
- Candidate PR #662 CI: START #46035757012, Windows #46035757099, Win7 #46035757130, macOS #46035756981 — SUCCESS; Defender/integrity PASS.
- Exact source `f013e244ad42c9d5c101b5c5eacf4f55738fadbd`.
- Exact-source CI: START #46036612119, Windows #46036612155, Win7 #46036612125, macOS #46036612192 — SUCCESS.
- Trigger PR #663 merged `460484945159ee3dc433c3f4f6b986a2c9872d73`; publisher #46037622127 SUCCESS.
- `v10.25-r2`: 8 canonical assets, prerelease=true; Stable r9 unchanged.

## Next

**10.25-r3 — програми + працівники + масова підготовка до друку**:
- new immutable program revision UI;
- cumulative multi-select employees/groups from registries;
- create explicit planned sessions with frozen snapshots;
- prepare DOCX through PaperDocuments;
- prepared only, never automatic conducted;
- backup/restore of plan + output;
- virtual-only tests and separate Test release.

Maintenance окремо: architecture #290, Feature Loss/UI #275/#556, docs-only CI #251. Draft #543/#395 лишаються open.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY and physical attachment purge remain blocked without explicit owner decision.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
