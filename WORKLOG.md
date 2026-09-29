# WORKLOG — Taxo

**Оновлено:** 29.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.6-r10** / `v10.6-r10`  
**Latest integrated code checkpoint in `main`:** Taxo **10.6-r10**  
**Main:** `109d3c64f2a54a29c5b88eb190a934f0a890245d`  
**Latest issued fast-test:** **10.7-r3** / `v10.7-r3` → `a51e336a31192fa7b82cb3bfe6db6c112dc70eae`  
**Candidate branch:** `work/v10.7-r3-order-appendices`  
**PR:** #92 → base `work/v10.7-r2-operations-orders`  
**Next code revision:** **10.7-r4**  
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
- PDF наказу за структурою наданих зразків;
- лише затверджене закріплення стає структурованим фактом;
- відповідальний за військово-транспортний обов'язок задається в `Експлуатація`;
- відомість ТЦК має внутрішнє затвердження з fingerprint даних;
- службові написи про Дію/реєстр/дату імпорту у форму для подання не друкуються;
- масове `Підтягнути всі реквізити з останнього імпорту` замість підтвердження кожного реквізиту окремо;
- immutable raw snapshot імпорту зберігається;
- exact-head regression + clean START verify: **607/607 OK**;
- Windows/macOS gates green;
- immutable `v10.7-r2` issued from `346d21aacaf6c40563b6c9430f466f14dafd3543`.

## DONE — 10.7-r3

Тема: **структуровані додатки до експлуатаційних наказів**.

Підстава: у наданих зразках є накази з окремими додатками / тематиками, а r2 підтримував тільки основний текст наказу та спеціальну таблицю закріплення.

Реалізовано:

- таблиця `operations_order_appendices` з номером, назвою, змістом, приміткою і прив'язкою до наказу;
- додатки мають стабільний порядок;
- створення / редагування / видалення дозволене лише для наказу у стані `Чернетка`;
- затверджений або скасований наказ разом з додатками не переписується;
- у `Експлуатація` додано вкладку `Додатки до наказів`;
- PDF наказу друкує кожен додаток окремою сторінкою з посиланням на дату і номер наказу;
- `main.APP_VERSION`, `VERSION.txt`, `taxo_app.py` синхронізовані на `10.7-r3`;
- START guard включає `v1073_features.py`;
- historical r2 test не заморожує поточний `VERSION.txt` на r2;
- release notes: `docs/releases/RELEASE_NOTES_v10.7-r3.md`.

### Verify / issue

Exact issued source: `a51e336a31192fa7b82cb3bfe6db6c112dc70eae`.

- exact-head source / START run `36544036092`: **613/613 OK**, clean START verify success;
- Windows PR gate `36544155945`: success;
- macOS PR gate `36544155999`: arm64 + x86_64 success;
- publisher run `36544340755`: success;
- immutable tag / prerelease: `v10.7-r3`;
- START asset: `Taxo_v10_7_candidate_r3_START.zip`;
- SHA-256: `48a6736c13b5626cfe21a4fa548e5971e00b5694f2649fa0f14b66dce9994727`;
- direct START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.7-r3/Taxo_v10_7_candidate_r3_START.zip
- release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.7-r3

Одноразові maintenance/publisher workflows після виконання прибрані. Branch head після release-closeout може бути новішим за issued tag; **tag не рухати і не перевидавати**.

## NEXT

1. Наступний кодовий крок — **10.7-r4**.
2. Форми ТО/ремонтів **не вигадувати** до отримання від власника реальних зразків.
3. Candidate line 10.7 не зливати у `main` без окремої команди власника.

## PRESERVED

- stable `v10.3` не пересувається;
- `v10.6-r10`, `v10.7-r1`, `v10.7-r2`, `v10.7-r3` та інші historical tags/releases immutable;
- plan/fact, табель, графіки й основний worklog цим кроком не переписуються;
- службова історія джерел імпорту зберігається всередині Taxo, але не друкується у затверджених формах для подання;
- робочі БД, персональні документи, скани і кеші не публікуються.

## BLOCKED

Немає.
