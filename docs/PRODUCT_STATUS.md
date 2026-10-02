# Taxo — стан продукту

**Актуально:** 02.10.2026

## Поточний статус

- **Stable:** Taxo 10.3 / `v10.3` — immutable.
- **Previous stable / rollback:** Taxo 10.1 / `v10.1`.
- **Latest integrated checkpoint in `main`:** Taxo 10.9-r9 / `v10.9-r9`.
- **Issued source:** `a368bf3bdfd4a16cc099844b830379c5e2646c2d`.
- **Cumulative integration:** PR #128 merged 10.9-r2 → 10.9-r9.
- **Main code merge:** `3f59544b8737cd4715d84f786e32378d87d1dd99`.
- **Documentation closeout:** PR #129 → `34a56e05133bedfc81e6273ea572f6e9757ddab7`.
- **Exact-head gates:** Windows `36919102579` — success; macOS `36919102540` — success.
- **Packages:** Windows x64 Setup/Portable, Windows 7 SP1 x64 Setup/Portable, macOS ARM64/Intel Portable, START/source, SHA-256 manifests.
- **Next code revision:** `10.9-r10`.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9

`v10.9-r9` — актуальний integrated candidate/checkpoint, але stable лишається `v10.3` до окремого рішення власника.

## Функціональний стан

Taxo — настільна система для одного автотранспортного підприємства. Поточна інтегрована лінія охоплює:

- працівників, водіїв, ролі та історію;
- графіки водіїв і планування персоналу;
- табель робочого часу, plan/fact, поділені зміни;
- маршрути, шляхові листи, пробіг;
- бланки підтвердження діяльності з ревізіями;
- транспортні засоби, документи ТЗ та СТОІР;
- страхування, ДЦВ, техконтроль, техпаспорти, тимчасову реєстрацію, протоколи тахографа;
- аналогові тахокарти, інтервали та протоколи;
- PDF/Excel звіти;
- резервування і переносиме робоче сховище;
- звірку ТЗ з «Шлях»;
- робочі редаговані registry-значення окремо від immutable державних snapshots;
- єдиний реєстр документів працівників;
- військово-транспортну відомість підприємства;
- локальний Diia-first цикл щорічного персонального військового звіряння без імітації державного API;
- захист історії виданих шляхівок і номерів;
- контроль чинності документів ТЗ на весь плановий період рейсу;
- посилений контроль work/rest, overlaps, boundary gaps, 3+9 і двотижневих меж;
- коректний пріоритет фактичних джерел у 60-денному реєстрі;
- historical employment/P-5 safety і цикли 2/2, 3/3;
- захист затверджених/підписаних наказів та закріплень водій→ТЗ;
- explicit SQLite schema baseline і future-schema guard.

## 10.9-r2 → 10.9-r9

- **r2:** незворотна історія виданих шляхівок і номерів.
- **r3:** vehicle-document validity на весь рейс.
- **r4:** work/rest compliance hardening.
- **r5:** safer 60-day activity source priority.
- **r6:** personnel balance / P-5 / employment-aware history.
- **r7:** odometer chronology / STOIR forecast safety.
- **r8:** immutable approved/signed orders і assignment safety.
- **r9:** SQLite `PRAGMA user_version` baseline та future-schema guard.

## Дані й сумісність

- робочі БД, SQLite, скани, кеші та персональні документи не входять до release;
- програма й робочі дані розділені;
- оновлення не повинно вимагати повторного введення робочої бази;
- raw snapshots державних витягів не переписуються локальними змінами;
- порожні державні значення не очищають локальні дані автоматично;
- план не оголошується фактом без явного підтвердження;
- future SQLite schema, новіша за підтримувану збіркою, блокується від відкриття r9+;
- для Windows 7 використовується окрема CPython 3.8.10 / PyInstaller 5.13.2 compatibility line.

## Recovery / джерело істини

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61.

Додатково:
- [Індекс релізів](releases/RELEASE_INDEX.md)
- [Release notes 10.9-r9](releases/RELEASE_NOTES_v10.9-r9.md)
- [Поточна контрольна точка](maintenance/CHECKPOINT_CURRENT.md)

## Право та власність

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.**

Taxo — proprietary software. Публічна видимість репозиторію не створює open-source ліцензії.

Документи: [LICENSE.md](../LICENSE.md) · [COPYRIGHT.md](../COPYRIGHT.md) · [Авторські права та ліцензія](LEGAL_AND_COPYRIGHT.md)
