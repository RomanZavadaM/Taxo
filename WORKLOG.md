# WORKLOG — Taxo

**Оновлено:** 29.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.6-r10** / `v10.6-r10`  
**Latest integrated code checkpoint in `main`:** Taxo **10.6-r10**  
**Main:** `109d3c64f2a54a29c5b88eb190a934f0a890245d`  
**Latest issued fast-test:** **10.7-r4** / `v10.7-r4` → `a214eccc95a00d229f28e52865a5ec37b6f61bba`  
**Active code branch:** `work/v10.7-r5-historical-personnel-reports`  
**Base checkpoint:** issued `v10.7-r4`; r5 не зливати у `main` без окремої команди власника  
**Current code revision:** **10.7-r5 — IN PROGRESS**  
**Knowledge branch:** `knowledge/vehicle-operations`  
**Live ledger:** Issue #61

## DONE — 10.7-r4

Тема: **редагування наказів у «Експлуатації», коректна модель виправлень і повна історія змін**.

### Реалізовано

- `operations_orders.py` переведено на `APP_VERSION = 10.7-r4`;
- `update_order(...)` дозволяє коригувати реквізити й текст наказу після створення;
- внутрішній стан `Чернетка / Затверджено / Скасовано` не використовується як технічний lock робочого запису;
- додано `paper_original_signed` і `paper_original_signed_at`;
- додано append-only `operations_change_log`;
- create/update/approve/cancel/paper-original зміни наказу пишуться в історію;
- `update_vehicle_assignment(...)` та add/update/delete закріплення ТЗ/водія протоколюються;
- `order_history(...)` повертає історію наказу і пов'язаних змін;
- міграція r2/r3 → r4 additive, без видалення існуючих записів;
- `operations_orders_ui.py` є єдиним робочим UI для «Експлуатації»;
- редагування наказу в UI йде через `ops.update_order(...)`, а не прямий SQL;
- для вже позначеного підписаного паперового оригіналу показується попередження про звірку/повторний друк після зміни;
- у реєстрі видно стан паперового оригіналу;
- закріплення ТЗ/водія має створення, редагування і видалення;
- є прямий сценарій `Створити наказ про закріплення`;
- додатки r3 можна коригувати після внутрішнього затвердження; create/update/delete додатка пишуться в `operations_change_log` через `v1074_appendix_history.py`;
- дублюючий зовнішній UI patch прибрано; `v1074_features.py` лишено тонким runtime identity layer;
- `main.APP_VERSION`, `VERSION.txt`, `operations_orders.APP_VERSION` синхронізовані на `10.7-r4`;
- START guard вимагає `v1074_features.py` і `v1074_appendix_history.py`;
- release notes: `docs/releases/RELEASE_NOTES_v10.7-r4.md`.

### Виявлений regression і виправлення

Перший regression після додавання history для додатків дав **621/622 OK**: ізольований r4-тест усе ще натрапляв на r3 `_require_draft(...)`. Це виправлено: r4-layer самостійно замінює старий guard на перевірку існування наказу, тож корекція затвердженого додатка працює і протоколюється.

Окремо виявлено, що ранній `v1074_features.py` дублював UI поверх повного `operations_orders_ui.py` і містив raw SQL update. Дублювання видалене до issuance; історія змін більше не обходиться через цей шлях.

### Immutable fast-test

Exact issued source: **`a214eccc95a00d229f28e52865a5ec37b6f61bba`**.  
Tag / prerelease: **`v10.7-r4`** — не рухати і не перевидавати.

- full regression + clean START run `36594472548`: **success**, **622/622 OK**;
- publisher run `36594472671`: **success**;
- Windows gate `36594481605`: **success**;
- macOS gate `36594481622`: **success**;
- release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.7-r4
- START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.7-r4/Taxo_v10_7_candidate_r4_START.zip
- START SHA-256: **`0301eb76d23585dc42f245fdf309947cd52ed7ecff76bd720b5c32caaea78cc7`**;
- checksum asset: `SHA256SUMS_v10_7_r4.txt`.

Після цього issuance **код r4 заморожений**. Будь-яка наступна зміна коду = **10.7-r5**.

## DONE — 10.7-r3

Тема: **структуровані додатки до експлуатаційних наказів**.

- `operations_order_appendices` з номером, назвою, змістом, приміткою і порядком;
- вкладка `Додатки до наказів`;
- PDF наказу друкує кожен додаток окремою сторінкою;
- exact source `a51e336a31192fa7b82cb3bfe6db6c112dc70eae`;
- regression **613/613 OK**;
- Windows/macOS gates green;
- immutable `v10.7-r3`;
- START SHA-256 `48a6736c13b5626cfe21a4fa548e5971e00b5694f2649fa0f14b66dce9994727`.

## DONE — 10.7-r2

Тема: **«Експлуатація», накази, закріплення водіїв і контроль відомості ТЦК**.

- новий розділ `Експлуатація`;
- структурований реєстр наказів;
- закріплення ТЗ/водіїв як структурований факт;
- відповідальні особи;
- внутрішнє затвердження відомості ТЦК з fingerprint;
- підтягування реквізитів з останнього підтвердженого імпорту без друку службової provenance у форму для подання;
- immutable raw import snapshot;
- exact source `346d21aacaf6c40563b6c9430f466f14dafd3543`;
- regression **607/607 OK**;
- Windows/macOS green;
- immutable `v10.7-r2`.

## DONE — 10.7-r1

Тема: **безпечне повторне розпізнавання аналогових тахографічних шайб**.

- manual intervals preserved on re-recognition;
- recognize only newly imported discs;
- no hidden recognition on selection;
- midnight circular/timeline cases fixed;
- exact source `1a124bc8218aada5ab4b66f74376b02c7dc62481`;
- regression **598/598 OK**;
- START, Windows, macOS green;
- immutable `v10.7-r1`.

## PREVIOUS FULL CHECKPOINT — 10.6-r10

- exact source `0baad010d0c0d4f29db62f26c29d512c71058928`;
- P-5 EDRPOU positional/keyword duplicate fixed;
- 588/588 OK;
- full Windows x64, Windows 7 SP1 x64, macOS ARM64, macOS Intel package set;
- immutable `v10.6-r10`;
- stable `v10.3` remains unchanged.

## IN PROGRESS — 10.7-r5

Підтверджено E2: історичні кадрові звіти при `active_only=True` спочатку застосовували `employees.active=1`, а вже потім `employee_employed_on(...)`. Через це звільнений сьогодні працівник зникав зі звіту за місяць, коли він ще працював.

Рішення r5: report-only compatibility layer `v1075_features.py` прибирає storage-level current-active prefilter для тижневого балансу, аудиту табеля та П-5; період визначається датами `employment_date` / `dismissal_date`. Current-active UI selector не патчиться.

## NEXT

1. Пройти full regression + clean START verify для r5.
2. Перевірити Windows/macOS gates на exact head.
3. Після зелених gate видати immutable fast-test `v10.7-r5` і прямий START archive.
4. Далі перейти до E3 — можливий подвійний план `водій + зміна персоналу`; потім E4 — `purge_old()` / backup.

Перший блок після r4 — продовження перевірки зовнішнього аудиту як **гіпотез**, а не автоматичної істини:

1. E2 — чи правильно історичні звіти включають працівників, які на дату звіту ще працювали, але зараз звільнені.
2. E3 — чи може один день отримати подвійний план через `водій + зміна персоналу`; знайти реальний writer/source конфлікту до виправлення.
3. E4 — перевірити порядок `purge_old()` / backup і виключити сценарій, де дані видаляються до резервного копіювання.
4. Після цього повернутися до решти аудиту: межі тижня/режимів, activity register plan/fact, waybill та інші підтверджені дефекти.

Форми ТО/ремонтів не вигадувати: спиратися на реальні матеріали в `knowledge/vehicle-operations` і, якщо потрібні нормативні твердження, перевіряти чинне авторитетне джерело.

## PRESERVED

- stable `v10.3` не пересувається;
- `v10.6-r10`, `v10.7-r1`, `v10.7-r2`, `v10.7-r3`, `v10.7-r4` та інші issued tags immutable;
- candidate line 10.7 не зливати у `main` без окремої команди власника;
- plan/fact, табель, графіки й основний worklog не переписуються побічно;
- паперовий підпис не перетворює електронний запис на незмінний: виправлення дозволене з історією і попередженням про звірку паперового примірника;
- робочі БД, персональні документи, скани та кеші не публікуються.

## BLOCKED

Немає.
