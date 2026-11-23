# PROJECT_STATE — Taxo

**Підтверджено GitHub 23.11.2026 після публікації Test v10.24-r4.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, draft=false, GitHub Latest.

**Current Test:** [10.24-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r4), exact source `e1616ea0063575b2c989d684934364f38f995966`, 8 assets, prerelease=true, draft=false. Publisher #45162074730 — SUCCESS.

## Test 10.24-r4

- explicit actual received/sent with mandatory action date;
- registration/attachment do not imply actual delivery facts;
- guarded forward state transitions + append-only immutable history;
- state-history integrity validation fails closed;
- legacy v1 registry migration preserves numbering;
- due/overdue is computed from explicit due date for open records only;
- UI actions for actual fact, legal status transition and history;
- minimum viewport 760×520 keeps all state actions mapped after moving them outside the resizable card pane.

Prep: #619; START #45157632285, Windows #45157632313, Win7 #45157632280, macOS #45157632297 — SUCCESS.
Candidate: #622; START #45159393780, Windows #45159393870, Win7 #45159393814, macOS #45159393725 — SUCCESS.
Exact source: START #45160194606, Windows #45160194713, Win7 #45160194576, macOS #45160194864 — SUCCESS; Windows/Win7 Defender + integrity PASS.
Release trigger #623 merged `ee4958f3cf1470f120e3b28f853640fea272c803`; publisher #45162074730 — SUCCESS.

## Open boundaries

Stable remains 10.24-r3. No automatic e-mail in r4.
Cases/threads, OCR/AI APPLY and physical attachment purge remain later separate slices.
#553/#556/#562 remain open; draft #543/#395 stay open.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
