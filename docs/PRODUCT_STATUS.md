# Taxo — стан продукту

## Поточний статус

**Taxo 10.1 — stable promotion approved 21.09.2026.**

Попередня stable / rollback — **Taxo 10.0**. Перевірений кандидат перед stable — **v10.1-r5**.

## Що входить у 10.1

- новий application shell із затвердженим text-free логотипом;
- динамічна назва підприємства;
- реєстр працівників із KPI, пошуком і впорядкованими діями;
- коректне розділення працевлаштування та ролі «Водій»;
- завершена роль водія не відновлюється після restart;
- «Звіти» відкриваються в основному workspace;
- детальний табель single-instance без дубльованого application sidebar;
- PDF/Excel, П-5, місячний баланс, контроль та папка звітів;
- оформлені «Про програму» і F1-довідка;
- весь функціонал stable 10.0: графіки, точні інтервали, шляхівки, тахограф, підтвердження діяльності, резервування.

## Перевірка

v10.1-r5:
- source/START — 157 tests / OK;
- Windows — 157 tests / OK + START preflight;
- macOS ARM64 — 157 tests / OK;
- macOS Intel x86_64 — 157 tests / OK;
- ручний Windows UI/navigation gate — підтверджено.

Stable publisher повторно перевіряє source і формує всі пакети вже з `Version: 10.1`.

## Пакети

GitHub Release `v10.1` міститиме:
- Windows x64 Setup;
- Windows x64 Portable;
- macOS ARM64 Portable;
- macOS Intel x86_64 Portable;
- START/source;
- per-platform і combined SHA-256.

## Дані й сумісність

- 10.1 використовує наявне робоче сховище;
- схема БД не змінюється;
- повторно вводити дані не потрібно;
- робочі БД, скани, кеші та персональні документи не публікуються;
- перед оновленням рекомендована резервна копія.

## Релізна політика

- після успішного publisher `main` + `v10.1` = stable source of truth;
- `v10.0` = previous stable / rollback;
- `v10.1-r1` … `v10.1-r5` = historical immutable candidates;
- старі tags/releases не пересуваються.

Документи:
- [Release notes 10.1](releases/RELEASE_NOTES_v10_1.md)
- [Фінальний аудит 10.1](maintenance/AUDIT_v10_1_STABLE.md)
- [Індекс релізів](releases/RELEASE_INDEX.md)


## Завершений candidate 10.2-r4

Stable 10.1 не змінюється. Candidate 10.2-r4 прийнятий, PR #40 злитий у `main`, prerelease `v10.2-r4` опублікований.

Політика розробки:
- кожен завершений крок піднімає ревізію;
- `r1 ... r10`, після `r10` — наступна minor-версія з `r1`;
- кожен крок завершується готовим START-архівом із прямим посиланням для ручного тестування;
- уже видані ревізії не перевикористовуються.

Джерело правила: [maintenance/DEVELOPMENT_RULES.md](maintenance/DEVELOPMENT_RULES.md).

Наступний кодовий крок — `10.2-r5`.
