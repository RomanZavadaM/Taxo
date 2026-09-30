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

Тема: **розвиток окремого центру СТОІР після фундаменту r4; прогноз ТО, заявки на несправності та виправлення реєстрового UI**.

### Реалізовано

- додано прогноз ТО-1/ТО-2 за фактичним середнім пробігом за останні 60 днів;
- без достатньої історії одометра прогнозована дата не вигадується;
- створено `vehicle_repair_requests` зі статусами `open/in_progress/closed`, пріоритетами та полями виконавця/результату;
- у центр СТОІР додано вкладку «Заявки на несправності»;
- додано зведення по активних ТЗ: одометр, середній км/день, ТО-1, ТО-2, відкриті заявки;
- таблиці СТОІР переведено на компактний Treeview зі скролами; дії над заявкою виконуються над вибраним рядком, без кнопок у кожному рядку;
- у `v1085_features.py` базова висота рядка Treeview зафіксована 26 px як захист від роздутого UI зі скріншотів користувача;
- виправлено реальну помилку зі скріншота `no such column: worklog_id`: `latest_odometer()` більше не вимагає необов'язкову колонку `worklog_id` від історичних робочих баз;
- regression r5 тепер навмисно перевіряє `vehicle_odometer_readings` без `worklog_id`;
- r4 identity-test переведено в historical-anchor режим, щоб виданий r4 не блокував наступні ревізії;
- `main.APP_VERSION`, `VERSION.txt` та `v1085_features.APP_VERSION` синхронізовані на `10.8-r5`;
- одноразовий workflow для безпечної точкової зміни великого `main.py` виконав заміну одного version marker і сам видалився з branch head.

### Verify / recovery

- перший r5 regression: нові функціональні тести пройшли, але виявили 20 identity failures через `main.APP_VERSION=10.8-r4` при `VERSION.txt=10.8-r5`;
- exact причина підтверджена на macOS arm64 у run `36767809692`;
- version marker виправлено без переписування великого `main.py`; commit, створений one-shot workflow: `05c76f7db50b545fb0d6ed0e09ee59bac9953f17`;
- PR #108 залишається draft і навмисно базується на exact r4 branch;
- bot-authored exact-head PR checks отримали `action_required` без jobs, тому цей WORKLOG commit створює новий owner-authored head для штатного повторного Windows/macOS gate.

## DOING

1. Перевірити exact-head Windows/macOS gates після owner-authored documentation commit.
2. Перевірити контрольні UI-вікна реєстру ТЗ/документів на compact-row acceptance criteria зі скріншотів.
3. Після green сформувати fast-test START archive для 10.8-r5 та записати SHA/asset у цей файл і Issue #61.

## NEXT

Після видачі r5 будь-яка нова кодова зміна — тільки **10.8-r6**. Шини/АКБ/агрегати та аудит планування персоналу не змішувати в r5.
