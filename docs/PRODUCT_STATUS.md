# Taxo — стан продукту

## Поточний статус

**Taxo 10.1 — stable і повністю опублікований.**

Release target: `fa5bbe0a5de733af1e227847ef9584daca57676e`.  
Previous stable / rollback: **Taxo 10.0**.  
Verified candidate before stable: **v10.1-r5**.

## Що входить у 10.1

- новий application shell із затвердженим text-free логотипом;
- динамічна назва підприємства;
- реєстр працівників із KPI, пошуком і впорядкованими діями;
- коректне розділення працевлаштування та ролі «Водій»;
- «Звіти» у головному workspace;
- single-instance детальний табель без дубльованого sidebar;
- PDF/Excel, П-5, баланс, контроль і папка звітів;
- «Про програму» та F1-довідка;
- функціонал 10.0: графіки, точні інтервали, шляхівки, тахограф, підтвердження діяльності, резервування.

## Stable verification

- source — 162 tests / OK;
- Windows — 162 tests / OK + START preflight;
- macOS ARM64 — 162 tests / OK;
- macOS Intel x86_64 — 162 tests / OK;
- 10 official release assets published.

## Дані

- 10.1 використовує наявне робоче сховище;
- схема БД не змінюється;
- повторно вводити дані не потрібно;
- БД/скани/кеші/персональні документи не публікуються.

## Release policy

- `main` + `v10.1` = current stable;
- `v10.0` = rollback;
- `v10.1-r1` … `v10.1-r5` = historical immutable candidates;
- old releases are never moved or overwritten.

Документи:
- [Release notes 10.1](releases/RELEASE_NOTES_v10_1.md)
- [Фінальний аудит 10.1](maintenance/AUDIT_v10_1_STABLE.md)
- [Індекс релізів](releases/RELEASE_INDEX.md)
