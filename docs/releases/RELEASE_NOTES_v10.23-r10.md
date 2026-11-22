# Taxo 10.23-r10 — REVIEW decisions без APPLY

**Робочий Test-кандидат. Stable/Latest залишається 10.23-r4; поточний опублікований Test — 10.23-r9.**

10.23-r10 завершує безпечний перед-APPLY цикл старого архіву документів: r6 INVENTORY → r7 batch store → r8 verified preview → r9 ANALYZE/PROPOSE → r10 REVIEW.

## Що додано

- versioned review format `taxo.document-import-review.v1`;
- окреме сховище `Data/DocumentLibrary/import_reviews/<batch_id>/review.json`, не всередині immutable import batch;
- явні рішення `confirm`, `reject`, `needs_review`;
- підтвердження звичайної proposal дозволяє тільки точне запропоноване значення;
- для ambiguity `confirm` вимагає явного вибору одного з відомих кандидатів;
- review прив'язаний до `import_batch_id + candidate_id + sha256 + proposal_sha256`;
- при зміні proposal/ruleset/identity/hash/field set старі рішення не підхоплюються;
- tampered confirmed value fail-closed;
- рішення атомарно зберігаються і відновлюються після restart;
- batch summary показує reviewed/needs_review та confirm/reject counts.

## Межі безпеки

- `applies_changes=false`;
- source-файли не відкриваються і не змінюються;
- `inventory.json` / `report.json` не переписуються;
- DocumentVault/БД і паперовий підпис не змінюються;
- немає OCR, зовнішнього AI/model API або APPLY;
- немає move/rename/delete/copy або фізичного сортування архіву.

## Перевірки prep

Prep PR #603 на фінальній голові `1ea4586e2e2b84b52b9485d1b680c7b0ce96d153` пройшов START, Windows, Windows 7 і macOS Intel/ARM; Windows/Win7 також пройшли Defender та integrity. Один початковий macOS regression виявив лише некоректне порівняння `/var` і `/private/var` у тесті; тест виправлено через canonical resolved path без послаблення production-логіки.

Stable/Latest змінюється тільки окремим рішенням власника. Після r10 наступний запланований модуль — вхідна/вихідна кореспонденція. APPLY імпортних пропозицій не починати без окремого рішення власника.
