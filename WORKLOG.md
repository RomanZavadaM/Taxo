# WORKLOG — Taxo

**Оновлено:** 29.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Оновлено:** 30.09.2026  
**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.6-r10** / `v10.6-r10`  
**Latest issued fast-test:** **10.7-r10** / `v10.7-r10` → `78acf4bf1c4d74c0e6797cb3bd6d60ba10fc6a1a`  
**Active candidate:** **10.8-r1** — відновлення та контрактне тестування функцій інтерфейсу  
**Active branch:** `work/v10.8-r1-interface-functionality-guard`  
**Active PR:** буде відкрито після green exact-head gate; не зливати у `main` без окремої команди власника  
**Next code revision after issuance:** **10.8-r2**  
**Knowledge branch:** `knowledge/vehicle-operations`  
**Live ledger:** Issue #61

## ACTIVE — 10.8-r1

Тема: **збереження функціональності інтерфейсу та повернення дій документів ТЗ**.

- підтверджено, що предметний функціонал документів ТЗ не видалений;
- знайдено реальну UI-регресію: історичний responsive layer змішував `grid` з уже наявним `pack` у спільному контейнері, після чого базові кнопки лишалися прихованими;
- додано окрему адаптивну панель «Картка транспортного засобу»;
- повернуто видимі входи «Нове авто», «Редагувати», «Документи ТЗ», «Контроль документів», «Вивести з експлуатації», «Оновити» та фільтр неактивних авто;
- реєстр «Шлях», ТЦК та інші нові дії збережені;
- додано functionality-contract тести для транспортної панелі, документів ТЗ, шляхових листів, Центру документів, sidebar та START package;
- історичні 10.7 identity tests переведено у режим regression anchors, щоб законний rollover 10.7-r10 → 10.8-r1 не ламав suite;
- pre-release regression: **664/664 OK**;
- аудит: `docs/maintenance/AUDIT_10.8-r1_INTERFACE_FUNCTIONALITY.md`;
- release notes: `docs/releases/RELEASE_NOTES_v10.8-r1.md`.

## DONE — 10.7-r5

Тема: **історичні кадрові звіти за датою працевлаштування**.

Підтверджено реальний дефект E2: historical report path при `active_only=True` спочатку застосовував SQL-фільтр `employees.active=1`, а вже потім date-aware `employee_employed_on(...)`. Через це працівник, який зараз звільнений, міг зникнути зі старого П-5, аудиту табеля або тижневого балансу, хоча у відповідному звітному періоді ще працював.

### Реалізовано

- додано report-only compatibility layer `v1075_features.py`;
- `collect_personnel_week_balance`, `collect_personnel_timesheet_audit` і `collect_p5_data` завантажують активні й неактивні кадрові записи перед перевіркою періоду;
- належність до звітного періоду визначає існуюча `employee_employed_on(...)` за `employment_date` / `dismissal_date`;
- після дати звільнення працівник у наступні періоди не потрапляє;
- current-active UI helper `_all_employee_rows(..., active_only=True)` не патчиться, тому звільнені працівники не повертаються у звичайні активні списки;
- P-5 PDF/XLSX використовує виправлений `collect_p5_data`;
- `main.APP_VERSION`, `VERSION.txt`, `taxo_app.py` синхронізовані на `10.7-r5`;
- START guard вимагає `v1075_features.py`;
- додано `tests/test_v10_7_r5.py`;
- історичні r4 identity-тести виправлено так, щоб вони зберігали r4 як regression anchor, але не заморожували поточну версію назавжди;
- release notes: `docs/releases/RELEASE_NOTES_v10.7-r5.md`.

### Verify / immutable fast-test

Exact issued source: **`ed223e8af88216167b7db4d70413608d66bea9af`**.  
Tag / prerelease: **`v10.7-r5`** — не рухати і не перевидавати.

- pre-publish exact functional head `b00f582345cbc04d8ccadc767d8619befa6379a2`: source/START run `36601170527`, **627/627 OK**;
- issued-head source/START run `36601420811`: success;
- publisher run `36601420863`: success;
- Windows issued-head gate `36601428908`: success;
- macOS issued-head gate `36601428971`: success (ARM64 + Intel);
- release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.7-r5
- START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.7-r5/Taxo_v10_7_candidate_r5_START.zip
- START SHA-256: **`abe2ddd269c24a5e0aef3e4f4f607b6f573e749675a9d40daae67d7ffcd1ef48`**;
- checksum asset: `SHA256SUMS_v10_7_r5.txt`.

Після issuance код r5 заморожений. Будь-яка наступна зміна коду = **10.7-r6**.

## DONE — 10.7-r4

Тема: **редагування наказів у «Експлуатації», коректна модель виправлень і повна історія змін**.

- `update_order(...)` дозволяє коригувати реквізити й текст наказу після створення;
- внутрішній стан не використовується як технічний lock;
- `paper_original_signed` / `paper_original_signed_at`;
- append-only `operations_change_log`;
- add/update/delete закріплень і додатків протоколюються;
- є прямий сценарій `Створити наказ про закріплення`;
- дублюючий raw-SQL UI patch прибрано;
- exact source `a214eccc95a00d229f28e52865a5ec37b6f61bba`;
- regression **622/622 OK**;
- Windows/macOS green;
- immutable `v10.7-r4`;
- START SHA-256 `0301eb76d23585dc42f245fdf309947cd52ed7ecff76bd720b5c32caaea78cc7`.

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

## NEXT — 10.7-r6

1. E3 — перевірити, чи може один день отримати подвійний план через `водій + зміна персоналу`; спочатку знайти реальний writer/source конфлікту, не виправляти навмання.
2. E4 — перевірити порядок `purge_old()` / backup і виключити сценарій, де дані видаляються до резервного копіювання.
3. Далі повернутися до решти аудиту: межі тижня/режимів, activity register plan/fact, waybill та інші підтверджені дефекти.
4. Форми ТО/ремонтів не вигадувати: спиратися на `knowledge/vehicle-operations` і, якщо потрібні нормативні твердження, перевіряти чинне авторитетне джерело.

## PRESERVED

- stable `v10.3` не пересувається;
- `v10.6-r10`, `v10.7-r1`…`v10.7-r5` та інші issued tags immutable;
- candidate line 10.7 не зливати у `main` без окремої команди власника;
- plan/fact, табель, графіки й основний worklog не переписуються побічно;
- паперовий підпис не перетворює електронний запис на незмінний: виправлення дозволене з історією і попередженням про звірку паперового примірника;
- робочі БД, персональні документи, скани та кеші не публікуються.

## BLOCKED

Немає.
