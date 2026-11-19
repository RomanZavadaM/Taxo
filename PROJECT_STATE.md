# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан GitHub: 19.11.2026.**

- **10.23-r1 завершена, інтегрована та опублікована як Test Portable.**
- Product protection PR #557 merged at `0e1cff52aa6b314809cc892b3e38e7a39fd559ef`. Release identity PR #558 merged at immutable **exact product source** `84184bbbf6c26b681c04feaebee19910269bd25c`.
- Exact-source CI: START #44600058957; Windows #44600058914; Windows 7 #44600058737; macOS Intel/ARM #44600058736 — **SUCCESS**. Windows та Win7 Defender/integrity gates PASS.
- Release trigger PR #559 merged at `213382a134faf50a6f694ca02803f70652f5c049`. Publisher #44601093398 SUCCESS.
- [v10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1): immutable Test Portable, 6 assets (4 portable, START, SHA256); tag points to exact product source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), unchanged.

## Підтверджені зміни 10.23-r1

Розширено старий Feature Loss механізм: 32 суворі UI-маршрути (замість 29), контроль зникнення кнопок, вкладок, пунктів меню; 22 документні/наказові дії, 10 команд наказів зі справжніми обробниками. Реальні перевірки каталогу, дерева й створення папки; наскрізне збереження учасників/ТЗ наказу, історії та виводу в друкований текст. Фонове читання каталогу більше не утримує весь стан Tk-вікна, що викликало ризик аварії на Windows 7.

## Межі й наступне

**Повний захист усіх функцій Taxo ще НЕ завершено.** Залишаються динамічні кнопки, end-to-end сценарії інших розділів, DPI/реальні платформні перевірки. Звіт/карта: `docs/maintenance/FUNCTION_PRESERVATION_FULL_COVERAGE_2026-11-19.md`.

[Issue #553](https://github.com/RomanZavadaM/Taxo/issues/553) залишається відкритою: незрозумілий механізм «Накази → Учасники / ТЗ», відсутня явна дія редагування збереженої ролі/примітки. Не закривати до ручного приймання власником. [Issue #556](https://github.com/RomanZavadaM/Taxo/issues/556): загальний аудит UI.

**Наступна кодова ревізія: 10.23-r2**. Один вузький крок: додати безпечне редагування ролі та примітки існуючого учасника/ТЗ наказу зі збереженням історичного snapshot, перевіркою після повторного відкриття й оновленням preview. PR #543 і PR #395 — незалежні проєктні напрацювання, не змінювати. Stable не просувати без прямого рішення власника.

## Історія

Попередній тестовий випуск: v10.22-r10 (точний код `56917daed4756dc4725cc58c43fcb900ce256f2c`). Детальні записи: WORKLOG.md, Issue #61 і приватний профіль `RomanZavadaM/dev-strategy` / `profile/taxo`.
