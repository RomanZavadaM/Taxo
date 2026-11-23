# PROJECT_STATE — Taxo

**Підтверджено GitHub 23.11.2026 після публікації Test v10.24-r7.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, draft=false, GitHub Latest.

**Current Test:** [10.24-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r7), exact source `4221b8baaeae4fad6ca8b6ebf4640a4a34050e2d`, 8 assets, prerelease=true, draft=false. Publisher #45220620129 — SUCCESS.

## Test 10.24-r7

- control-oriented revision over the existing order participant model; no new order business rules;
- 58 strict live routes total;
- the r6 correspondence contract remains exactly 17 routes;
- order participant live control covers search/select, edit role/note, add vehicle, remove selected and preview synchronization;
- add/edit/remove changes propagate into an already-open preview;
- DOCX and PDF are verified against the same frozen participant snapshot;
- history and full backup/restore preserve participant identity, role, note, snapshot and sequence.

Prep #630: START #45213479378, Windows #45213479658, Win7 #45213479371, macOS #45213479464 — SUCCESS; Defender/integrity PASS.

Candidate #634: START #45216365054, Windows #45216364728, Win7 #45216364723, macOS #45216364729 — SUCCESS.

Exact issued source `4221b8baaeae4fad6ca8b6ebf4640a4a34050e2d`: START #45217452473, Windows #45217452461, Win7 #45217452456, macOS #45217452990 — SUCCESS; Defender/integrity PASS.

Release trigger #635 merged `ee7bdbb5e50e3b47e42da46fc7b47eee2991523e`: START #45218698014, Windows #45218698050, macOS #45218698263 — SUCCESS. Win7 #45218698024 first attempt had a non-reproducible legacy catalog-reader timing failure; rerun on the same unchanged head passed regression/build/Defender/integrity. Publisher #45220620129 — SUCCESS.

## Open boundaries / next package

Stable remains 10.24-r3.

After r7 recovery, reconcile #553/#556 and choose one bounded next control slice. Do not automatically broaden r8 into e-mail/mailbox sync/external integrations. OCR/AI APPLY and physical attachment purge remain separately blocked.

Draft #543/#395 stay open.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
