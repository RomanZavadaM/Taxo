# WORKLOG — Taxo

**Оновлено:** 30.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.8-r3** / `v10.8-r3`  
**Latest integrated code checkpoint:** **10.8-r3** — `main` `50db4b0de4d37260c2031aa96317fef61d93ea90`  
**Issued fast-test:** **10.8-r4** — immutable source `c68c8a18d5f3a7c236bb3c58b96fc15a8ba7bd08`; PR #107 лишається draft/unmerged  
**Active code revision:** **10.8-r5** — прогноз ТО / заявки на несправності / compact registry UX  
**Active branch:** `work/v10.8-r5-stoir-forecast-repair-requests`  
**Active PR:** #108 (draft), base = `work/v10.8-r4-stoir-maintenance`  
**Live ledger:** Issue #61

## ACTIVE — 10.8-r5

Тема: **розвиток окремого центру СТОІР після фундаменту r4; прогноз ТО, заявки на несправності та виправлення роздутих реєстрових таблиць**.

### Реалізовано

- додано прогноз ТО-1/ТО-2 за фактичним середнім пробігом за останні 60 днів;
- без достатньої історії одометра прогнозована дата не вигадується;
- створено `vehicle_repair_requests` зі статусами `open/in_progress/closed`, пріоритетами та полями виконавця/результату;
- у центр СТОІР додано вкладку «Заявки на несправності»;
- додано зведення по активних ТЗ: одометр, середній км/день, ТО-1, ТО-2, відкриті заявки;
- таблиці СТОІР переведено на компактний Treeview зі скролами; дії над заявкою виконуються над вибраним рядком, без кнопок у кожному рядку;
- у `v1085_features.py` базова висота рядка Treeview зафіксована 26 px як захист від роздутого UI зі скріншотів користувача;
- `VERSION.txt` і feature-layer піднято до `10.8-r5`;
- додано `tests/test_v10_8_r5.py` для forecast і lifecycle заявок.

### Verify

- head на момент створення PR #108: `2412d1b5b4db3c96c034669443bc845895342b60`;
- Windows workflow run `36767708364` — запущений;
- macOS workflow run `36767708479` — запущений;
- PR #108 навмисно базується на exact r4 branch, тому його diff містить лише r5.

## DOING

1. Дочекатися результату exact-head Windows/macOS gates і виправити тільки підтверджені failures.
2. Перевірити контрольні UI-вікна реєстру ТЗ/документів на compact-row acceptance criteria зі скріншотів.
3. Після green сформувати fast-test START archive для 10.8-r5 та записати SHA/asset у цей файл і Issue #61.

## NEXT

Після r5 не змішувати в цю ревізію шини/АКБ/агрегати та аудит планування персоналу. Наступна кодова зміна після виданого r5 — тільки **10.8-r6**.
