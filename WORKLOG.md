# WORKLOG — Taxo

**Оновлено:** 30.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Оновлено:** 30.09.2026  
**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.6-r10** / `v10.6-r10`  
**Latest issued fast-test:** **10.8-r3** / `v10.8-r3` → `d8ec901b9b80f74b5b85cd1bda202dd58c86a7bd`  
**Issued START:** `Taxo_v10_8_candidate_r3_START.zip` · SHA-256 `aa75661658194425f7dc95c353516a6f1c44f98040989f72d402985e2f023d00`  
**Active branch / PR:** `work/v10.8-r3-tck-statement-fix` / PR #105 — документаційне завершення issued r3; код r3 заморожений  
**Next code revision:** **10.8-r4**  
**Knowledge branch:** `knowledge/vehicle-operations`  
**Live ledger:** Issue #61; recovery дублюється у WORKLOG та PR

## ISSUED — 10.8-r3

Тема: **виправлення відомості ТЦК та необов'язкові реквізити ТЦК у картці транспортного засобу**.

Підтверджений користувачем production defect із `Taxo_errors(3).log`: дата відомості з UI передавалась як `30.09.2026`, тоді як старий `military_transport_statement._iso_day()` викликав `date.fromisoformat()` і очікував `YYYY-MM-DD`.

### Реалізовано

- `v1083_features.py` нормалізує `ДД.ММ.РРРР`, ISO, `date` та `datetime` у внутрішній `YYYY-MM-DD`;
- `30.09.2026` більше не проходить напряму в `date.fromisoformat()`;
- до стабільної панелі картки ТЗ додано **«Реквізити ТЦК»**;
- реквізити: належність до власного/балансового парку, тип ТЗ, технічний стан, залишкова/балансова вартість у тис. грн, примітка;
- реквізити необов'язкові для звичайної картки ТЗ;
- дані зберігаються у вже наявній `vehicle_military_transport_statement_data`, без дублювання сутностей;
- офіційна форма не отримує додаткових службових реквізитів про джерело даних;
- додано regression-тести на точний формат `30.09.2026`, помилкові дати та round-trip реквізитів ТЗ у рядок відомості;
- `main.APP_VERSION`, `VERSION.txt`, `taxo_app.py`, `START.bat` і START package guard синхронізовані на 10.8-r3;
- release notes: `docs/releases/RELEASE_NOTES_v10.8-r3.md`.

### Verify / immutable fast-test

Exact issued source: **`d8ec901b9b80f74b5b85cd1bda202dd58c86a7bd`**.  
Tag / prerelease: **`v10.8-r3`** — не рухати і не перевидавати.

- exact functional/source head `ba469191321bf18b6a36c6a85718fa02002381dd`: source/START run `36736687719` — success;
- publisher run `36737140249` — success;
- issued START asset: `Taxo_v10_8_candidate_r3_START.zip`;
- START SHA-256: **`aa75661658194425f7dc95c353516a6f1c44f98040989f72d402985e2f023d00`**;
- Windows exact-issued gate `36737147803` — success;
- macOS exact-issued gate `36737147699` — success;
- release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.8-r3
- START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.8-r3/Taxo_v10_8_candidate_r3_START.zip
- PR #105: https://github.com/RomanZavadaM/Taxo/pull/105

Після issuance код r3 заморожений. Будь-яка наступна зміна коду = **10.8-r4**.

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
- GUI-редактор наказу використовує `ops.update_order(...)`, а не прямий `UPDATE`;
- для додатків виправлено історичне блокування редагування після затвердження;
- full regression: **622/622 OK**;
- Windows/macOS gates — success;
- immutable source/tag: `a214eccc95a00d229f28e52865a5ec37b6f61bba` / `v10.7-r4`;
- START SHA-256: `0301eb76d23585dc42f245fdf309947cd52ed7ecff76bd720b5c32caaea78cc7`.

## RECOVERY RULE

Перед продовженням: `START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → цей `WORKLOG.md` → actual GitHub / PR / CI → Issue #61. Видані теги не рухати; наступну кодову зміну після `v10.8-r3` починати тільки як **10.8-r4**.
