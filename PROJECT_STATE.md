# PROJECT_STATE — Taxo

**Підтверджено GitHub 23.11.2026 після публікації Test v10.24-r8.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, draft=false, GitHub Latest.

**Current Test:** [10.24-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r8), exact source `d24b1bc96115de52d6088813992aca3b410fe243`, 8 assets, prerelease=true, draft=false. Publisher #45237831016 — SUCCESS.

## Test 10.24-r8

- control-only revision over the existing r7 order participant model; no new order business rules or schema changes;
- 58 strict live routes total; the r6 correspondence contract remains exactly 17 routes;
- fresh UI reopen reloads the same order from persisted SQLite and preserves number/date/subject/status;
- participant role/note and row data survive reopen;
- Draft → Active changes the order status without mutating participant identity, frozen snapshot or sequence;
- same-order refresh preserves the selected participant row;
- r7 add/edit/remove, preview synchronization, DOCX/PDF and full backup/restore guards remain active.

Prep #638: START #45231841871, Windows #45231841838, Win7 #45231842010, macOS #45231841929 — SUCCESS; Defender/integrity PASS.

Candidate #639: START #45234694758, Windows #45234694250, Win7 #45234694546, macOS #45234694225 — SUCCESS; Defender/integrity PASS.

Exact issued source `d24b1bc96115de52d6088813992aca3b410fe243`: START #45235704945, Windows #45235704686, Win7 #45235704998, macOS #45235705102 — SUCCESS; Defender/integrity PASS.

Release trigger #640 merged `411c1e496ccddcd4ed0f9fd754743dfdf9ef8986`; trigger START #45236768940, Windows #45236768934, Win7 #45236769035, macOS #45236768791 — SUCCESS; Defender/integrity PASS. Publisher #45237831016 — SUCCESS.

## Open boundaries / next package

Stable remains 10.24-r3.

r8 recovery must be synchronized across public docs, private profile, Issue #61 and Drive. Next action after recovery: reconcile manual acceptance for #553/#556/#562; if no new defects are found, choose one bounded r9 control slice. Do not automatically broaden r9 into e-mail/mailbox sync/external integrations. OCR/AI APPLY and physical attachment purge remain separately blocked.

Draft #543/#395 stay open.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
