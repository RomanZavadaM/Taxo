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

Перевірено й реалізовано:

1. `work_date` тепер fallback-дата, якщо `reading_at` порожній/непридатний;
2. новіший waybill-факт більше не програє старішому ручному показнику тільки через порожній `reading_at`;
3. `average_daily_mileage` використовує ті самі валідні ефективні дати та historical lookback від останньої точки;
4. прогноз ТО відраховується від дати останнього надійного показника, не від `date.today()`;
5. при достатній історії одиничний очевидний стрибок відсікається робастним сегментним фільтром;
6. ТО-1 і ТО-2 лишаються окремими циклами — r7 не вводить неузгоджене правило скидання ТО-1 після ТО-2.

Технічно:

- додано additive runtime layer `v1097_stoir_odometer.py` без зміни схеми БД;
- додано `tests/test_v10_9_r7.py` з поведінковими SQLite-сценаріями;
- machine identity = `10.9-r7`;
- layer зареєстрований як `v1097-stoir-odometer` у maintenance domain;
- START.bat і source package guard вимагають r7 runtime;
- аудит: `docs/maintenance/AUDIT_STOIR_ODOMETER_v10.9-r7.md`;
- release notes: `docs/releases/RELEASE_NOTES_v10.9-r7.md`.

## NEXT

1. Прибрати тимчасовий integration workflow із кандидатної гілки.
2. Відкрити draft PR r7 поверх frozen r6.
3. Прогнати exact-head regression/START + Windows/macOS gates.
4. Якщо gates зелені — видати immutable `v10.9-r7` START+checksum.
5. Зафіксувати SHA/run IDs/checksum у PR та Issue #61.
6. Не зливати в `main` без прямої команди власника.
