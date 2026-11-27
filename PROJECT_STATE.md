# PROJECT_STATE — Taxo

**Підтверджено GitHub 27.11.2026 після публікації Test v10.24-r9.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, draft=false, GitHub Latest.

**Current Test:** [10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 assets, prerelease=true, draft=false. Publisher #46004721962 — SUCCESS.

## Test 10.24-r9

- Причина: виявлено, що старі копії документів ТЗ могли бути записані в БД, але фізичний файл уже був відсутній; UI раніше показував «Копія: Є» лише за непорожнім шляхом.
- Історичний root cause: механізм існував від 10.2-r1 (21.09.2026): Taxo зберігав workspace-шлях копії, але не source path; vehicle-document bytes у звичайному backup були optional.
- Нові/замінені копії: `Data/VehicleDocuments/<vehicle_id>/<doc_type>/...` + source path + size + SHA-256.
- UI/контроль показують реальний стан файла; відкриття перевіряє existence/integrity.
- Backup з позначкою документів ТЗ перевіряє всі зареєстровані копії, включно з архівованими; legacy external/source файл за наявності materialize-иться у staging backup без зміни live DB.
- Restore архіву з vehicle documents повторно перевіряє bytes.
- Архівування запису не видаляє копію.
- Якщо bytes уже відсутні у workspace, source і старих backup, автоматичне відновлення неможливе — це тепер видно явно.
- Product PR #643 merged у main; exact product source `e3770aa72b0744eee192979a2e569651bac4f257`.
- Exact-main START/Windows/Win7/macOS Intel+ARM — SUCCESS; Defender/integrity PASS.
- Release `v10.24-r9`: 8 canonical assets, prerelease=true, exact target `e3770aa72b0744eee192979a2e569651bac4f257`; publisher #46004721962 SUCCESS.
- Stable/Latest лишається `v10.24-r3`.

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

Recovery r9 is the current checkpoint: product PR #643, immutable Test release v10.24-r9, public recovery/current-page docs, private `profile/taxo`, Issue #61/#642 and Drive current-docs mirror belong to the same incident closure. The owner acceptance step is a real vehicle-document round trip: attach/replace → archive → selected vehicle-document backup → restore into a test workspace → open the restored copy. If historical bytes are absent from workspace, source and old full backups, they are not recoverable from SQLite alone.

Do not consume a new code revision for documentation or mirror cleanup. Start another code slice only after r9 acceptance or a newly identified defect and then follow the normal project plan. Do not automatically broaden work into e-mail/mailbox sync/external integrations. OCR/AI APPLY and physical attachment purge remain separately blocked.

Draft #543/#395 stay open.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
