# WORKLOG — Taxo

**Оновлено:** 29.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.6-r10** / `v10.6-r10`  
**Latest integrated code checkpoint in `main`:** Taxo **10.6-r10**  
**Main:** `109d3c64f2a54a29c5b88eb190a934f0a890245d`  
**Latest issued fast-test:** **10.7-r2** / `v10.7-r2` → `346d21aacaf6c40563b6c9430f466f14dafd3543`  
**Branch:** `work/v10.7-r2-operations-orders`  
**PR:** #91 → base `work/v10.7-r1-tachograph-safety`, not `main`  
**Next code revision:** **10.7-r3**  
**Live ledger:** Issue #61

## DONE — 10.7-r1

Тема: безпечне повторне розпізнавання аналогових тахографічних шайб.

- manual intervals preserved on re-recognition;
- new-disc-only auto-recognition after import;
- no hidden recognition on row selection;
- midnight circular/timeline cases fixed;
- regression 598/598 OK;
- START, Windows and macOS gates green;
- immutable fast-test `v10.7-r1` issued from `1a124bc8218aada5ab4b66f74376b02c7dc62481`.

## DONE — 10.7-r2

Тема: **«Експлуатація», накази, закріплення водіїв і контроль відомості ТЦК**.

Підстава: надані власником зразки наказів підприємства 2023 року та уточнення, що реквізити після підтвердженого імпорту з файлів Дії / державного реєстру є робочими даними Taxo, а затверджена форма для подання не повинна містити службових позначок про джерело.

Реалізовано:

- новий розділ `Експлуатація` у головній навігації;
- вкладки `Накази`, `Закріплення водіїв`, `Відповідальні`, резерв `ТО / ремонти`;
- структурований реєстр наказів зі станами `Чернетка / Затверджено / Скасовано`;
- групи наказів: закріплення ТЗ, зберігання ТЗ, робочий час, місця відпочинку, стажування, ОП/пожежна безпека, довільний експлуатаційний наказ;
- PDF наказу за структурою наданих зразків: підприємство → дата/№/місце → тема → вступ → `НАКАЗУЮ` → пункти/таблиця → контроль → підпис керівника;
- наказ про закріплення: таблиця ТЗ / держномер / водій + період чинності;
- лише затверджене закріплення стає структурованим фактом і використовується у відомості ТЦК на обрану дату;
- legacy-зв'язки збережено як fallback;
- відповідальний за військово-транспортний обов'язок задається у `Експлуатація → Відповідальні`;
- PDF/XLSX відомості ТЦК вимагає внутрішнього затвердження відповідальним;
- затвердження прив'язано до fingerprint: після зміни реквізитів/рядків потрібне повторне затвердження;
- службові написи про Дію/реєстр/дату імпорту у форму для подання не друкуються;
- у військовій робочій картці є масове `Підтягнути всі реквізити з останнього імпорту`; immutable raw snapshot зберігається;
- `main.APP_VERSION`, `VERSION.txt`, `taxo_app.py` синхронізовані на `10.7-r2`;
- START guard включає `operations_orders.py`, `operations_orders_ui.py`, `v1072_features.py`;
- historical r1 identity guard більше не заморожує поточний `VERSION.txt`;
- випадкову temp branch та одноразові maintenance/publisher workflows прибрано після використання.

## VERIFY / RELEASE

- exact-head pre-release regression + clean START verify: **607/607 OK**;
- Windows PR gate: run `36541858923` — success;
- macOS PR gate: run `36541858976` — arm64 + x86_64 success;
- PR #91 відкритий поверх issued r1 line;
- immutable fast-test `v10.7-r2` виданий з exact source `346d21aacaf6c40563b6c9430f466f14dafd3543`;
- publisher run `36542013509` — success;
- START: `Taxo_v10_7_candidate_r2_START.zip`;
- START SHA-256: `f8930a320010efbe6d63cba7d5fd249e8d0456d7f148aac24ddbbd1fbdd958cf`;
- checksum: `SHA256SUMS_v10_7_r2.txt`;
- release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.7-r2

`v10.7-r2` immutable: tag/source не пересувати й не перевидавати поверх іншого коду.

## NEXT

Наступна кодова ревізія — **10.7-r3**.

Майбутні форми ТО/ремонтів та інші експлуатаційні документи зводити у контур `Експлуатація`, а не множити окремі несистемні вікна.

## PRESERVED

- stable `v10.3` не пересувається;
- `v10.6-r10`, `v10.7-r1`, `v10.7-r2` та інші historical tags/releases immutable;
- plan/fact, табель, графіки й основний worklog цим кроком не переписуються;
- службова історія джерел імпорту зберігається всередині Taxo, але не друкується у затверджених формах для подання;
- робочі БД, персональні документи, скани і кеші не публікуються;
- у `main` 10.7-r2 не зливається без окремої команди власника.

## BLOCKED

Немає.
