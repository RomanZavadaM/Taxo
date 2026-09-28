# PROJECT_STATE — Taxo

**Дата:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`  
**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Stable target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`  
**Previous stable / rollback:** Taxo 10.1 / `v10.1` / `fa5bbe0a5de733af1e227847ef9584daca57676e`  
**Latest published full checkpoint:** Taxo 10.4-r2 / `v10.4-r2` / `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`  
**Latest issued fast-test revision:** Taxo 10.5-r7 / issued code head `19a9f462993767a43ca3d5add8c7afabcbd39a96` — immutable  
**Latest fast-test START:** run `36396485974`, artifact `10958596374`, `476/476 OK`, SHA-256 `62bd734c82db132557376d5e6b01c37a84b5b358e32a0eedc7e1a4afd7f2c295`  
**Latest archive:** `Taxo_v10_5_candidate_r7_START.zip`  
**Checkpoint main merge:** `271d43c0912e24c95014ac2a92ba2fc1695f4a11` (full checkpoint 10.4-r2)  
**Live ledger:** Issue #61  
**Наступний кодовий крок:** тільки `10.5-r8`.

## Джерело істини

Перед будь-якою новою роботою читати в такому порядку:

1. `START_HERE.md` — recovery/start protocol.
2. `PROJECT_RULES.md` — постійні правила розробки та релізів.
3. `PROJECT_STATE.md` — цей поточний checkpoint.
4. `WORKLOG.md` — завершений/активний крок.
5. `VERSION.txt` + `main.APP_VERSION` — поточна кодова identity.
6. `docs/releases/RELEASE_INDEX.md` — checkpoints.
7. Issue #61 — live ledger рішень і публікацій.

`v10.3` лишається immutable stable. `v10.4-r2` лишається останнім full multi-platform checkpoint у `main`. Fast-test revisions `10.4-r3 … 10.5-r7` є окремими START-checkpoint-ами та не підміняють stable/full release без окремого рішення власника.

## Обов’язкове версіювання

- Кожен завершений крок = нова ревізія `r1 → … → r10`.
- Після `r10` автоматично підвищується minor і починається `r1`.
- Уже видану для тестування ревізію повторно не використовувати.
- Перший розряд версії змінюється тільки за прямим рішенням власника.
- Після виданого `10.5-r7` будь-яка нова кодова зміна має йти як **10.5-r8**.
- При інтенсивній розробці основний тестовий пакет — START; Portable/Setup формуються на рідших/повних checkpoints.
- «Злити у main» для релізного checkpoint означає: перевірки → пакети → tag/release → PR → merge → документація.

## Taxo 10.5-r7 — latest fast-test checkpoint

### Функціональний обсяг

`10.5-r7` завершує перехід персонального військового звіряння на новий електронний порядок 2026 року:

- додано окремий локальний цикл `отримання відомостей → актуалізація → фіксація`;
- в UI є точні переходи на офіційні сервіси Дії для отримання відомостей, актуалізації працівників та фінальної фіксації;
- Taxo показує ЄДРПОУ, останній імпорт державних відомостей і базову готовність даних працівників;
- локальний етап «відомості отримано» неможливо завершити без фактичного імпорту державного XLSX у Taxo;
- локальні етапи підготовки **не створюють** статус «офіційно звірено»;
- тільки після окремого підтвердження фактичного завершення «Фіксації відомостей персонального обліку» в Дії створюється `RECONCILIATION_DIIA` у наявному `military_official_reconciliations`;
- для завершеного факту зберігаються дата, номер/реквізит підтвердження та/або короткий фактичний результат;
- Taxo прямо повідомляє, що програма не відправляє дані до Дії / Реєстру «Оберіг» і не може самостійно підтвердити державну операцію;
- при технічній недоступності електронного способу або відсутності ЄДРПОУ UI не приховує резервний порядок за п. 46 Порядку №1487;
- `diia_reconciliation.py` зберігає лише локальний стан підготовки й не створює другого паралельного офіційного журналу.

### Перевірки та пакет

- issued code head: `19a9f462993767a43ca3d5add8c7afabcbd39a96`;
- source regression: **476/476 OK**;
- START run: `36396485974` — success;
- artifact: `10958596374` / `Taxo_v10_5_candidate_r7_START`;
- archive: `Taxo_v10_5_candidate_r7_START.zip`;
- size: `942091` bytes;
- SHA-256: `62bd734c82db132557376d5e6b01c37a84b5b358e32a0eedc7e1a4afd7f2c295`;
- START guard підтвердив r7 runtime і відсутність DB/SQLite/cache/development clutter.

## Fast-test checkpoint history 10.5

- `10.5-r6` — робочі редаговані дані працівників / Дія та ТЗ / «Шлях», immutable raw snapshots, Diia-first UI; issued head `5f6c7643ce63bffb8069de9775194322a71f13df`; `465/465 OK`; artifact `10957441841`.
- `10.5-r5` — сумісність XLSX «Шлях» з `ChildSheet/tabId` без зміни вихідного XLSX; issued head `23064b775087c9dfc05867dc65f27e6d6d87e9b4`; `456/456 OK`; artifact `10955647596`.
- `10.5-r4` — lossless імпорт двох фактичних форм державних XLSX працівників, raw snapshot усіх колонок; issued head `117b305b048c2588e21d7908f39a3bb1071f74aa`; artifact `10944963733`.
- `10.5-r3` — єдиний реєстр документів працівників поверх `employee_documents`; issued head `ca1a1288f915c3fa0eb57c82a3e91aea3b0887d1`; `440/440 OK`; artifact `10944184721`.
- `10.5-r2` — покомпонентна кольорова звірка ТЗ з «Шлях»; issued head `d9e7beefa52c7774e1b4bd6711dfc5907e06de37`; `425/425 OK`; artifact `10944042965`.
- `10.5-r1` — офіційна відомість військово-транспортного обліку по власному/балансовому транспорту; issued head `d7e5a730767ebc17e6935b2d3f25208a9f151c16`; `399/399 OK`; artifact `10943696206`.

Усі видані fast-test checkpoints immutable.

## Taxo 10.4-r2 — актуальний full checkpoint у main

- P0/P1/P2 UI-remediation;
- незалежний контроль документів ТЗ, кілька активних документів одного типу, необов’язкова ДЦВ;
- waybill readability + кутовий штамп;
- Windows 7 SP1 compatibility gate;
- modern Windows, Windows 7 SP1, macOS ARM64/Intel, START publishers;
- tag/release `v10.4-r2`, exact target `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`;
- PR #74 merged у `main` → `271d43c0912e24c95014ac2a92ba2fc1695f4a11`;
- stable `v10.3` не змінено.

## Постійні межі даних

- робочі БД, SQLite-файли, скани, кеші й персональні документи не публікуються;
- державні XLSX/CSV є зовнішнім джерелом звірки/доповнення, а не заміною робочої БД;
- оригінальні raw snapshots державних витягів не переписуються локальними змінами;
- порожнє/відсутнє у держреєстрі не видаляє й не очищає локальні дані;
- локальне редагування у Taxo не означає зміну даних у Дії, «Оберіг» або «Шлях»;
- імпорт державного XLSX сам по собі не означає офіційно завершене звіряння з ТЦК;
- локальний контроль документів ТЗ, «Шлях», персональний військовий облік і військово-транспортний обов’язок — окремі контури;
- планові дані не оголошуються фактом; шляхівка/графік = план, підтверджені фактичні дані ведуться окремо;
- START archive має бути чистим і переносимим;
- оновлення програми не повинно стирати або підміняти робочі дані.

## Windows 7 policy

Окрема compatibility line використовує CPython 3.8.10 x64 + PyInstaller 5.13.2 + pinned `requirements-win7.txt`; `Taxo_win7.spec` та PE compatibility gate `scripts/check_win7_pe.py` лишаються обов’язковими для повних checkpoints із заявленою підтримкою Windows 7.

## Право та власність

- Taxo — proprietary product.
- Правовласник: **Roman Zavada (Роман Завада), фізична особа**.
- Copyright © 2026 Roman Zavada. All rights reserved.
- Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Наступний крок

Fast-test checkpoint `10.5-r7` завершений і immutable. Не продовжувати код у r7. Наступна кодова ревізія — тільки **10.5-r8**, в окремій work-гілці після повторного читання `START_HERE.md`, цього файла, `WORKLOG.md` та Issue #61. `main` не змінювати без прямої команди власника на повний checkpoint.
