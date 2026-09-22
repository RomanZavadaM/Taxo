# Taxo — стан продукту

## Актуальний стан на 22.09.2026

- **Stable:** Taxo 10.3 (`v10.3`) — опублікований latest stable; target `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
- **Previous stable / rollback:** Taxo 10.1 (`v10.1`).
- **Verified candidate:** Taxo 10.3-r6; `v10.3-r6` published and immutable.
- **Правовласник:** Roman Zavada (Роман Завада).
- **Ліцензія:** proprietary / all rights reserved; сторонні компоненти зберігають власні ліцензії.
- **Recovery protocol:** `START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61.

Документи: [LICENSE.md](../LICENSE.md) · [COPYRIGHT.md](../COPYRIGHT.md) · [Авторські права та ліцензія](LEGAL_AND_COPYRIGHT.md)

**Наступний кодовий крок після stable:** `10.3-r7` — ще не розпочатий.

---

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


## Активний candidate 10.2-r5

Інфраструктурне виправлення: historical publisher stable 10.1 більше не запускається автоматично при нових merge у `main`. Це прибирає хибні failure-повідомлення GitHub Actions; функціонал Taxo та immutable stable `v10.1` не змінюються.

Після завершення r5 наступний кодовий крок — `10.2-r6`.


## Active candidate 10.2-r6

UI consistency checkpoint: великі secondary windows оформлюються у стилі stable 10.1 з text-free logo та динамічною назвою підприємства. Бізнес-логіка, БД та моделі розрахунку не змінюються.


## Active candidate 10.2-r7

Packaging correction після r6: UI-зміни secondary windows збережені, але тестовий START archive тепер має канонічну назву 10.2-r7. Historical r6 не переписується.


## Completed candidate 10.2-r7

`10.2-r7` опублікований і злитий у `main`. Він завершує secondary-window UI checkpoint та виправлення START-пакування. Stable release `v10.1` лишається незмінним.

Наступний кодовий крок — `10.2-r8`, ще не розпочатий. Перед ним зафіксовано окремий аудит трьох пов'язаних областей: графік водіїв, загальне планування персоналу та зміни персоналу випуску (лікар / механік / диспетчер). Це **не є частиною 10.2-r7**.
