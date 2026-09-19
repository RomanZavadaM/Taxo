# NEW CHAT HANDOFF — Taxo 9.1 candidate r9.4

**Дата фіксації:** 19.09.2026  
**Repository:** `RomanZavadaM/Taxo`  
**Stable baseline:** `v9.0.1`  
**Current candidate:** `v9.1-r9.4`  
**Branch:** `work/v9.1-monthly-dispatch-waybill-ui`  
**PR:** #29 — `Taxo 9.1 candidate r9.4: аудит графіків і передетапна стабілізація`  
**Release target / head:** `3da975ff3dc30740aeaf300d9e3471415075dbe0`

## Release

Immutable pre-release:
- tag: `v9.1-r9.4`
- START: https://github.com/RomanZavadaM/Taxo/releases/download/v9.1-r9.4/Taxo_v9_1_candidate_r9_4_START.zip
- SHA-256: https://github.com/RomanZavadaM/Taxo/releases/download/v9.1-r9.4/SHA256SUMS_v9_1_candidate_r9_4.txt

Final CI at the release target:
- Windows source/regression: success;
- macOS ARM64: success;
- macOS Intel x86_64: success;
- START package: success;
- immutable source release publisher: success;
- total regression tests: 97.

Do **not** move or overwrite older candidate tags/releases.

## Current product state

### Driver schedules / audit
The old ambiguous button `Перевірити графіки` was replaced with **`Аудит графіків…`**.

The daily schedule now shows one of:
- `⚠ день: N помилк.`;
- `✓ день: помилок введення немає`;
- `○ день: записів для аудиту немає`;
- `○ день: є запис, але точний час не задано`.

Audit scopes:
- Поточний день;
- Весь місяць;
- Шаблони маршрутів;
- Місяць + маршрути.

Technical audit checks:
- overlapping work parts;
- overlapping driving intervals;
- incomplete start/end pairs;
- driving outside work interval;
- empty time parts;
- active routes without a time scenario;
- legacy worklog without work_segments when exact legacy times exist.

The audit does not rewrite history. Double-click opens the exact day/route for manual correction.

**Important:** technical input audit is separate from regulatory control under Regulation №340. The audit window has a separate explicit path to **Контроль №340 для водія**.

### Canonical intervals
Keep these invariants:
- exact work_segments are the source of truth when present;
- overlapping parts are counted by interval union, not raw sum;
- real overnight rollover through 00:00 must remain valid;
- same-day overlap must never become a fake next-day gap;
- duration-only values must never invent 08:00–16:00;
- new overlaps are blocked on save/copy/route save;
- old conflicting history is shown, never silently rewritten.

### Personnel / absences
- absence has display/accounting priority but does not delete historical worklog/segments;
- one employee may have several roles on one day if exact intervals do not overlap;
- linked driver role is not duplicated in employee_shifts;
- wording is now `План збережено; день позначено як відсутність`.

### P-5
Implemented standard form № P-5 based on Order of the State Statistics Committee of Ukraine 05.12.2008 №489:
- PDF and XLSX;
- legend codes 01–30;
- calendar 1–31;
- worked days/hours;
- overtime/night/evening/weekend-holiday hours;
- absence reason groups;
- sex field;
- salary/tariff rate;
- signature blocks.

If plan exists but fact is missing, before generation Taxo asks:
- Yes — substitute plan for missing fact;
- No — generate using entered fact only;
- Cancel — do not generate.

Plan substitution must remain explicit and visible:
- substituted cells are highlighted;
- PDF/XLSX includes a note with the count of substituted days.

### Confirmation-of-activities archive
r9.3/r9.4 state:
- newest forms first;
- optional `Тільки вибраний водій`;
- optional month/year filter;
- reset filters;
- edit by record ID, not list position.

### Monthly driver control
`Підсумки та контроль №340` is a dashboard:
- compact monthly metrics;
- `Дні місяця` tab;
- `Контроль №340` tab;
- day table includes schedule/parts, breaks, work, driving, overtime, route and result;
- double-click opens day editing;
- `Відкрити деталізацію` generates/opens the detailed PDF.

### Data / safety
- stable main remains Taxo 9.0.1;
- do not merge PR #29 until manual operational verification is complete;
- working SQLite DB, scans, cache and personal data are never shipped in source packages;
- migrations are additive; do not DROP working tables/columns;
- backups and restore safety were checked in the r9.4 audit;
- release policy: source/START candidate for minor candidate steps; executable Windows/macOS builds are not required for every minor candidate.

## Full audit document

Use as source of truth before starting the next functional stage:
`docs/maintenance/AUDIT_v9_1_r9_4.md`

Automatic part of the audit is complete. Remaining gate is manual operational verification on the real Windows workspace/database.

## Manual verification gate before next stage

Check on the real working Windows data:

1. `Аудит графіків…`: current day with no records, clean exact day, and old real error.
2. Whole month + route templates, including inactive-route option where applicable.
3. Double-click problem → correct day/route → rerun audit.
4. Explicit transition from selected problematic driver/day to `Контроль №340`.
5. Overnight shift through 00:00 and split shift.
6. Vacation/sick leave: Personnel → driver timesheet → monthly/weekly balance → P-5.
7. P-5 in both modes: fact only / confirmed plan substitution.
8. P-5 PDF/XLSX A4 readability, highlighting and substitution note.
9. Confirmation archive: selected driver, month filter, reset, newest first.
10. Monthly control: day table, double click, `Відкрити деталізацію`.
11. Backup → file validation → test restore on a copy of the workspace.
12. Start through `START.bat` on working Windows.

Only after these checks decide whether to merge PR #29 and create the next stable 9.1.

## Prompt for a new chat

Copy everything between the lines below into a new chat:

---

Продовжуємо проєкт **Taxo / Driver Worktime** з репозиторію `RomanZavadaM/Taxo`.

Починай не з припущень, а з файлів:
1. `PROJECT_STATE.md`
2. `docs/maintenance/AUDIT_v9_1_r9_4.md`
3. `docs/maintenance/NEW_CHAT_HANDOFF_v9_1_r9_4.md`
4. `VERSION.txt`
5. release notes для `v9.1-r9.4`.

Актуальний стан:
- stable baseline: **Taxo 9.0.1**;
- current candidate: **Taxo 9.1 candidate r9.4**;
- branch: `work/v9.1-monthly-dispatch-waybill-ui`;
- PR #29 відкритий;
- current head/release target: `3da975ff3dc30740aeaf300d9e3471415075dbe0`;
- immutable release: `v9.1-r9.4`;
- Windows/macOS ARM64/macOS Intel regression tests: **97 tests success**;
- START package/release publisher: success;
- **main не зливати**, поки я не підтверджу ручну експлуатаційну перевірку.

Що вже завершено:
- канонічні часові інтервали та захист від перекриттів;
- єдиний стан дня у Табелі/Графіку;
- відсутності без видалення історії;
- Персонал/режими/внутрішнє сумісництво;
- П-5 PDF/XLSX з явним вибором підстановки плану замість відсутнього факту;
- архів підтверджень діяльності: водій/місяць/новіші зверху;
- місячний контроль водія та PDF деталізація;
- центр **«Аудит графіків…»** з 4 областями перевірки;
- технічний аудит введення відділений від нормативного **Контролю №340**;
- build/release/version/documentation cleanup r9.4;
- immutable source/START pre-release r9.4.

Зараз наша задача — **не починати новий великий функціонал**, а пройти ручний gate з `AUDIT_v9_1_r9_4.md` на моїй реальній Windows-базі. Я буду надсилати скріншоти/результати; ти одразу аналізуй, виправляй код у робочій гілці, запускай CI, дописуй документацію і для кожної нової контрольної точки роби новий immutable release/tag. Старі теги не пересувати.

Критичні інваріанти:
- exact intervals > stored aggregates;
- overlap = union, без подвійного рахунку;
- duration-only не створює вигаданого інтервалу;
- історію автоматично не переписувати;
- відсутність не видаляє план;
- П-5 не підставляє план мовчки;
- stable 9.0.1 лишається rollback point;
- executables не робити на кожному дрібному candidate, source/START достатньо згідно поточної release policy.

Почни з короткого підтвердження фактичного стану репозиторію/release/CI, а потім веди мене по ручній перевірці пункт за пунктом, виправляючи знайдені проблеми.

---

