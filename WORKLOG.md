# WORKLOG — Taxo

**Оновлено:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated code checkpoint:** **10.9-r1**  
**Latest full multi-platform checkpoint:** **10.9-r1 / `v10.9-r1`**  
**Latest issued fast-test:** **10.9-r6 / `v10.9-r6`**  
**Current active slice:** **10.9-r7 — СТОІР / одометр і прогноз ТО**  
**Integrated main baseline:** `8f18a7ccf1588556f6f3d7dca81943f87d817935`  
**Active branch:** `work/v10.9-r7-stoir-odometer-safety`  
**Base:** immutable `v10.9-r6` → `531723c1b7e9cb9c3d0258d085819381981de14c`  
**Stable remains:** `v10.3`  
**Live ledger:** Issue #61

## DONE — 10.9-r6 immutable issuance

10.9-r6 закрив перевірені ризики персоналу, місячного балансу та П-5:

- планові `Вихідний` / `Відпочинок` не зменшують норму як відпустка або лікарняний;
- історичні неявки накладаються за датою працевлаштування без lossy `{driver_id: employee_id}` mapping;
- поточний `active` не використовується як критерій історичної неявки;
- поведінка режимів 2/2 і довільного 3/3 покрита тестами;
- r6 підключений окремим runtime layer без зміни схеми БД.

Immutable issued source: `531723c1b7e9cb9c3d0258d085819381981de14c`.
Exact-source regression: **761/761 OK**.
Gates: START/source `36914019199`, Windows `36914025872`, macOS `36914025948`, publisher `36914902396` — success.

Release: `v10.9-r6` / https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r6  
START: `Taxo_v10_9_candidate_r6_START.zip`  
SHA-256: `fc003b71347a65e3ee5fa998392e254903f19af6e899a2cec9d3ef2155da9882`.

PR #125 лишається draft/unmerged. `main` не змінено.

## DOING — 10.9-r7

Ціль: **зробити показники одометра й прогноз СТОІР достовірними без вигаданих дат або ігнорування новішого факту**.

Перед зміною коду перевірити на актуальному runtime кожен пункт зовнішнього аудиту:

1. `work_date` як fallback-дата показника, якщо `reading_at` порожній;
2. `latest_odometer` повинен бачити новіший фактичний показник зі шляхівки;
3. `average_daily_mileage` має використовувати валідні точки з fallback-датою;
4. прогноз має відштовхуватись від дати останньої надійної точки, а не сліпо від `date.today()`;
5. середній пробіг треба захистити від одиничних очевидних викидів;
6. окремо перевірити чинне бізнес-правило щодо ТО-2 і циклу ТО-1; не змінювати його без підтвердженої необхідності.

## NEXT

1. Провести кодовий аудит СТОІР і зафіксувати, які з шести ризиків реально підтверджуються.
2. Реалізувати тільки підтверджені виправлення в окремому r7 layer/domain helper з поведінковими тестами на SQLite.
3. Підняти machine identity до `10.9-r7`, оновити аудит/release notes/START guards.
4. Прогнати exact-head regression/START + Windows/macOS gates.
5. Видати immutable `v10.9-r7` START+checksum, зафіксувати в PR та Issue #61.
6. Не зливати в `main` без прямої команди власника.
