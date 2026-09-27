# PROJECT_STATE — Taxo

**Дата:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`  
**Stable:** Taxo 10.3 / `v10.3`  
**Stable target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`  
**Previous stable / rollback:** Taxo 10.1 / `v10.1` / `fa5bbe0a5de733af1e227847ef9584daca57676e`  
**Latest published full checkpoint:** Taxo 10.4-r2 / `v10.4-r2` / `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`  
**Latest issued fast-test revision:** Taxo 10.5-r2 / `d9e7beefa52c7774e1b4bd6711dfc5907e06de37` — immutable  
**Latest fast-test START:** run `36356444031`, artifact `10944042965`, `425/425 OK`, SHA-256 `c88c806c9deb4821080f63adea46001cbd4a885b9dc7702d80e0b9dcbd675c26`  
**Checkpoint PR:** #74 — merged  
**Checkpoint main merge:** `271d43c0912e24c95014ac2a92ba2fc1695f4a11`  
**Full publisher:** run `36275440403` — success  
**Final PR gates:** Windows `36275442986`; macOS ARM64/Intel `36275442988` — success  
**Live ledger:** Issue #61  
**Наступний кодовий крок:** тільки `10.5-r3`.

## Джерело істини

Перед будь-якою новою роботою читати в такому порядку:

1. `START_HERE.md` — recovery/start protocol.
2. `PROJECT_RULES.md` — постійні правила розробки та релізів.
3. `PROJECT_STATE.md` — цей поточний checkpoint.
4. `WORKLOG.md` — завершений/активний крок.
5. `VERSION.txt` + `main.APP_VERSION` — поточна кодова identity.
6. `docs/releases/RELEASE_INDEX.md` — опубліковані checkpoints.
7. Issue #61 — live ledger рішень і публікацій.

`v10.3` лишається immutable stable. `v10.4-r2` лишається останнім full multi-platform checkpoint у `main`. Fast-test revisions після нього є окремими START-checkpoint-ами і не підміняють stable/full release без окремого рішення власника. Уже видані candidate/checkpoint-и не пересуваються і не перевикористовуються.

## Обов’язкове версіювання

- Кожен завершений крок = нова ревізія `r1 → … → r10`.
- Після `r10` автоматично підвищується minor і починається `r1`.
- Уже видану для тестування ревізію повторно не використовувати.
- Перший розряд версії змінюється тільки за прямим рішенням власника.
- Після виданого `10.5-r2` будь-яка нова кодова зміна має йти як **10.5-r3**.
- При інтенсивній розробці основний тестовий пакет — START; Portable/Setup формуються на рідших/повних checkpoints.
- «Злити у main» для релізного checkpoint означає: перевірки → пакети → tag/release → PR → merge → документація.

## Taxo 10.5-r2 — latest fast-test checkpoint

### Функціональний обсяг

- ліцензійний реєстр «Шлях» звіряється з Taxo покомпонентно, а не лише на рівні цілого ТЗ;
- для кожного поля зберігаються локальне значення, значення реєстру, стан, джерело й історія рішень;
- кольорові стани: відповідає / можна доповнити / розбіжність / критичний конфлікт / немає у витягу;
- рішення: прийняти реєстр / залишити Taxo / виправити у реєстрі / відкласти;
- активне `виправити у реєстрі` автоматично закривається, якщо наступний квартальний витяг уже відповідає Taxo;
- VIN і держномер є критичними ідентифікаційними полями;
- порожні або відсутні значення реєстру не очищають локальні дані;
- локальні ТЗ, яких немає у витягу, не видаляються й не деактивуються;
- збережено режими лише звірити / доповнити / оновити + доповнити та створення нової картки після підтвердження;
- «Шлях», локальний контроль документів ТЗ та військово-транспортний облік лишаються окремими контурами.

### Перевірки та пакет

- issued code head: `d9e7beefa52c7774e1b4bd6711dfc5907e06de37`;
- source regression: **425/425 OK**;
- START run: `36356444031` — success;
- artifact: `10944042965` / `Taxo_v10_5_candidate_r2_START`;
- SHA-256: `c88c806c9deb4821080f63adea46001cbd4a885b9dc7702d80e0b9dcbd675c26`;
- START guard підтвердив r1/r2 runtime-файли й відсутність DB/SQLite/cache/development clutter.

## Taxo 10.4-r2 — актуальний full checkpoint

### Функціональний обсяг

- виконано P0/P1/P2 UI-remediation після аудиту 10.4-r1;
- виправлено перекриття елементів у формі точки маршруту;
- secondary/document windows зроблено адаптивнішими для вузьких екранів і DPI scaling;
- додано/вирівняно scrollbars та перегруповано переповнені toolbars;
- покращено Win7-friendly підписи та UI;
- у документах ТЗ додано необов’язковий тип **«ДЦВ страхування»**;
- новий документ того самого типу більше не архівує попередній автоматично;
- архівування попередніх активних документів стало явною опцією;
- дозволено кілька активних документів одного типу, зокрема кілька тимчасових талонів;
- у шляховому листі збільшено приблизно на 20% шрифт даних, що підставляються при виписці;
- верхній лівий блок шляхового листа оформлено як кутовий штамп підприємства з фактичних реквізитів.

### Перевірки

- source regression: **300 tests / OK**;
- Windows 7 / Python 3.8 regression: **300 tests / OK**;
- sample waybill: дві A4-сторінки, без перекриття штампа та внесених даних;
- Windows 7 PE scan: **success**; заборонений Win8+ import `api-ms-win-core-path-l1-1-0.dll` у bundle не виявлено;
- modern Windows publisher: success;
- Windows 7 SP1 publisher: success;
- macOS ARM64 publisher: success;
- macOS Intel x86_64 publisher: success;
- START/source package: success;
- combined SHA-256 manifest: success.

### Публікація

- tag/prerelease: `v10.4-r2`;
- exact release target: `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`;
- full publisher: `36275440403` — success;
- final Windows PR gate: `36275442986` — success;
- final macOS ARM64/Intel PR gate: `36275442988` — success;
- PR #74 merged у `main` → `271d43c0912e24c95014ac2a92ba2fc1695f4a11`;
- release містить modern Windows Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel Portable, START/source та per-platform/combined SHA-256 manifests;
- stable `v10.3` не змінено.

## Windows 7 policy

- окрема compatibility line використовує CPython 3.8.10 x64 + PyInstaller 5.13.2 + pinned `requirements-win7.txt`;
- `Taxo_win7.spec` і Windows 7 installer зберігаються окремо від modern Windows packaging;
- PE compatibility gate є обов’язковим для повних checkpoints із заявленою підтримкою Windows 7;
- перевірку винесено у `scripts/check_win7_pe.py`, щоб уникнути помилок embedded CI-script і повторно використовувати її далі;
- раніше власник підтвердив реальний запуск 10.3-r10 Portable на Windows 7 x64; для 10.4-r2 автоматичний PE/build gate пройдено.

## Дані та сумісність

- робочі БД, SQLite-файли, скани, кеші й персональні документи не публікуються;
- державні XLSX/CSV є зовнішнім джерелом звірки/доповнення, а не заміною робочої БД;
- порожнє/відсутнє у держреєстрі не видаляє й не очищає локальні дані;
- START archive має бути чистим і переносимим;
- оновлення програми не повинно стирати або підміняти робочі дані;
- історичні candidate/stable releases лишаються immutable.

## Право та власність

- Taxo — proprietary product.
- Правовласник: **Roman Zavada (Роман Завада), фізична особа**.
- Copyright © 2026 Roman Zavada. All rights reserved.
- Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Історія checkpoint

Для детальної історії використовувати `docs/releases/RELEASE_INDEX.md` та відповідні `RELEASE_NOTES_*.md`. Ключові точки:

- `10.5-r2` — latest fast-test: покомпонентна звірка ТЗ з «Шлях»;
- `10.5-r1` — відомість військово-транспортного обліку по власному/балансовому транспорту;
- `10.4-r10` — військово-транспортний облік ТЗ;
- `10.4-r9` — покомпонентна звірка працівників і військовий облік 2026;
- `v10.4-r2` — останній full multi-platform checkpoint;
- `v10.3-r10` — Windows 7 compatibility checkpoint, manual Portable gate прийнято власником;
- `v10.3` — поточний immutable stable;
- `v10.1` — previous stable / rollback.

## Наступний крок

Fast-test checkpoint `10.5-r2` завершений і immutable. Не продовжувати код у r2. Для наступного кроку створити окрему work-гілку під **10.5-r3**, спочатку прочитавши `START_HERE.md`, цей файл і `WORKLOG.md`.
