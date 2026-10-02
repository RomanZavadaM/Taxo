# Taxo — стан продукту

**Актуально:** 02.10.2026

## Поточний статус

- **Stable:** Taxo 10.3 / `v10.3` — immutable.
- **Previous stable / rollback:** Taxo 10.1 / `v10.1`.
- **Latest integrated checkpoint in `main`:** **Taxo 10.9-r10**.
- **Structural cleanup PR:** #132.
- **Exact r10 source:** `ff56519da35e03204bdaf77f7187cddd692f79d4`.
- **Main merge:** `5e179eabccc35afa984be04208e2e4d96094a2fb`.
- **Exact-head gates:** Windows `37018721703` — success; Windows 7 `37018721695` — success; macOS `37018722335` — success.
- **Latest full multi-platform published checkpoint:** Taxo 10.9-r9 / `v10.9-r9`.
- **Next code revision:** `10.10-r1`.

Release з готовими пакетами для тестування: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9

`10.9-r10` — актуальний integrated code checkpoint; stable лишається `v10.3` до окремого рішення власника.

## Що змінилося в 10.9-r10

- runtime/support Python modules перенесені в `src/taxo/`;
- runtime templates перенесені в `assets/`;
- active PyInstaller/Inno Setup definitions перенесені в `packaging/`;
- historical packaging specs винесені в `packaging/history/`;
- START/Windows/Windows 7/macOS build paths адаптовані до нової структури;
- flat-import compatibility збережена bootstrap-механізмом;
- робочі БД та користувацькі дані не мігрують і не переміщуються цією ревізією.

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

## Дані й сумісність

- робочі БД, SQLite, скани, кеші та персональні документи не входять до release;
- програма й робочі дані розділені;
- оновлення не повинно вимагати повторного введення робочої бази;
- raw snapshots державних витягів не переписуються локальними змінами;
- порожні державні значення не очищають локальні дані автоматично;
- plan не оголошується fact без явного підтвердження;
- future SQLite schema, новіша за підтримувану збіркою, блокується від відкриття r9+;
- для Windows 7 використовується окрема CPython 3.8.10 / PyInstaller 5.13.2 compatibility line.

## Recovery / джерело істини

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61.

Додатково:
- [Індекс релізів](releases/RELEASE_INDEX.md)
- [Release notes 10.9-r10](releases/RELEASE_NOTES_v10.9-r10.md)
- [Поточна контрольна точка](maintenance/CHECKPOINT_CURRENT.md)

## Право та власність

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.**

Taxo — proprietary software. Публічна видимість репозиторію не створює open-source ліцензії.

Документи: [LICENSE.md](../LICENSE.md) · [COPYRIGHT.md](../COPYRIGHT.md) · [Авторські права та ліцензія](LEGAL_AND_COPYRIGHT.md)
