# HANDOFF_CURRENT — Taxo

**Live GitHub confirmed — 19.11.2026.**

- **10.23-r1 merged, tested and published.** Feature preservation PR #557 + release identity PR #558 + publisher trigger PR #559 merged.
- **Exact immutable source:** `84184bbbf6c26b681c04feaebee19910269bd25c`.
- Exact-source CI: START #44600058957, Windows #44600058914, Win7 #44600058737, macOS Intel/ARM #44600058736 — SUCCESS, Defender/integrity PASS. Publisher #44601093398 — SUCCESS.
- [v10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1): 6 files, 4 portable + START + SHA256, tag to exact source. **Stable/Latest: v10.21-r2, unchanged.**

## Зроблено

Існуюча система захисту функцій розширена: **32 строгі маршрути**, контроль зникнення кнопок/вкладок/меню і правильних обробників 10 команд наказів, 22 захищені документні/наказові дії. Живі перевірки каталогу папок, наскрізне збереження списку учасників/ТЗ та вивід у наказ. Безпечніше фонове читання каталогу на Windows 7.

## Що залишається

**Це не повний контроль усього Taxo.** Карта: `docs/maintenance/FUNCTION_PRESERVATION_FULL_COVERAGE_2026-11-19.md`. Не закривати #556 до повного покриття.
Issue #553 — механізм «Накази → Учасники / ТЗ» власником не прийнято; додавання/вилучення є, **редагування ролі та примітки збереженого учасника відсутнє**. Не закривати без ручного тесту.
PR #543 (архітектура бібліотеки готових документів/листування) і PR #395 (архітектура шаблонів) — окремі draft, не втручатися.

## Наступний безпечний крок

**10.23-r2:** додати явне редагування ролі/примітки вибраного учасника/ТЗ з історією та регресією save→reopen→preview. Після цього продовжувати #553 і захист інших функцій без нових паралельних систем.

Recovery: спочатку START_HERE.md; звірити main, HANDOFF, PROJECT_STATE, GitHub PR/branches/CI/releases, а не лише цю нотатку.
