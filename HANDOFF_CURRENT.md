# HANDOFF_CURRENT — Taxo

**27.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r9 опублікована й перевірена.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, GitHub Latest.

**Current Test:** [10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 assets, prerelease=true, draft=false. Publisher #46004721962 — SUCCESS. Stable/Latest лишається v10.24-r3.

## Що зроблено у 10.24-r9

- Issue #642 відкрита до ручного приймання; product PR #643 завершено: копії документів ТЗ більше не вважаються наявними лише через текстовий шлях у БД.
- Root cause існував від 10.2-r1 (21.09.2026): workspace copy була, але source path не зберігався; vehicle docs у manual backup додавались окремою галочкою.
- Новий/замінений файл отримує Taxo-owned copy у `Data/VehicleDocuments`, source path, size та SHA-256.
- UI показує реальні стани «Є / Файл втрачено / Копія пошкоджена / Зовнішній файл / Немає».
- selected backup з документами ТЗ перевіряє DB→file; legacy external/source за наявності забирається в staging backup; restore повторно перевіряє bytes.
- Архівування запису не видаляє файл; archived record → backup → restore → open має regression.
- Непоправно відсутні старі bytes не вигадуються: backup із vehicle documents не проходить як «повний».
- Exact product source: `e3770aa72b0744eee192979a2e569651bac4f257`; release `v10.24-r9` має 8 canonical assets, prerelease=true.
- Stable/Latest не змінено: `v10.24-r3`.

## Перевірки 10.24-r9

- 1712 regression tests у START suite — PASS.
- Windows — SUCCESS; Defender/integrity PASS.
- Windows 7 / Python 3.8 — SUCCESS; Defender/integrity PASS.
- macOS Intel + Apple Silicon — SUCCESS.
- Publisher #46004721962 — SUCCESS; exact release target `e3770aa72b0744eee192979a2e569651bac4f257`.

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

- Recovery 10.24-r9 закриває кодову й релізну частину інциденту; Issue #642 залишається відкритою до ручної перевірки реального робочого сховища.
- **Одна наступна дія для власника:** на 10.24-r9 додати або замінити тестову копію документа ТЗ, заархівувати запис, створити backup із позначкою «Копії документів транспортних засобів», відновити його в тестову папку й перевірити відкриття файла. Для старих зниклих протоколів шукати bytes у старому workspace/повних backup/початкових файлах; із самої SQLite їх відновити неможливо.
- Якщо ручна перевірка r9 виявить новий дефект, наступна кодова ревізія — **10.24-r10**; якщо ні — після приймання повернутися до загального плану проєкту.
- Automatic e-mail, mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не починати автоматично.
- Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF_CURRENT → PROJECT_STATE → private `profile/taxo` → live GitHub.
