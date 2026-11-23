# HANDOFF_CURRENT — Taxo

**23.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r8 опублікована й перевірена.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, GitHub Latest.

**Current Test:** [10.24-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r8), exact source `d24b1bc96115de52d6088813992aca3b410fe243`, 8 assets, prerelease=true, draft=false. Publisher #45237831016 — SUCCESS. Stable/Latest лишається v10.24-r3.

## Що зроблено у 10.24-r8

r8 не змінює бізнес-правила наказів, схему БД чи формати документів. Це вузький control-only крок поверх r7: перевірка повного закриття й повторного відкриття UI наказу з повторним читанням даних із робочої SQLite-БД.

- у Taxo лишається **58 strict live routes** загалом;
- correspondence-contract r6 лишається точним набором із **17 correspondence routes**;
- після fresh UI reopen зберігаються номер, дата, тема і стан наказу;
- роль, примітка та рядок учасника/ТЗ не губляться після повторного відкриття;
- перехід наказу **«Чернетка» → «Діє в Taxo»** не переписує participant data;
- refresh того самого наказу зберігає вибраний рядок учасника;
- frozen `snapshot_json` і `sequence_no` не змінюються;
- r7 add/edit/remove, live preview sync, DOCX/PDF і backup/restore guards не послаблені.

## Перевірки 10.24-r8

Prep PR #638 final head `f95aac5ef1344b5c851411dd2bc6d1ea1f9ddf50`: START #45231841871, Windows #45231841838, Win7 #45231842010, macOS Intel/ARM #45231841929 — SUCCESS; Windows/Win7 Defender + integrity PASS. Prep merged у main як `06189dc472d6ca8c3063defb9c0b20c20626fda4`.

Candidate PR #639 exact head `f8ef99d7cfe07e2d8064878e41da5d09657930fe`: START #45234694758, Windows #45234694250, Win7 #45234694546, macOS Intel/ARM #45234694225 — SUCCESS; Windows/Win7 Defender + integrity PASS.

Merged candidate / exact issued source `d24b1bc96115de52d6088813992aca3b410fe243`: START #45235704945, Windows #45235704686, Win7 #45235704998, macOS Intel/ARM #45235705102 — SUCCESS; Windows/Win7 Defender + integrity PASS.

Release-trigger PR #640 head `c3a205ec8ccdea3a17a8badb13d2644651e963ea`: START #45236768940, Windows #45236768934, Win7 #45236769035, macOS Intel/ARM #45236768791 — SUCCESS; Defender/integrity PASS. PR merged as `411c1e496ccddcd4ed0f9fd754743dfdf9ef8986`. Publisher #45237831016 — SUCCESS.

GitHub Release `v10.24-r8`: exact target `d24b1bc96115de52d6088813992aca3b410fe243`, 8 canonical assets, prerelease=true, draft=false. Stable/Latest remains `v10.24-r3`.

## Що далі

- Recovery r8 має бути закритий у public docs, private `profile/taxo`, Issue #61 і Google Drive current-docs комплекті.
- **Одна наступна дія:** звірити ручне приймання #553/#556/#562; якщо нових дефектів немає — вибрати один bounded control slice для r9.
- Automatic e-mail, mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не починати автоматично.
- Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF_CURRENT → PROJECT_STATE → private `profile/taxo` → live GitHub.
