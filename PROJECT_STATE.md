# PROJECT_STATE — Taxo

**Дата:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`  
**Stable:** Taxo 10.3 / `v10.3`  
**Stable target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`  
**Previous stable / rollback:** Taxo 10.1 / `v10.1` / `fa5bbe0a5de733af1e227847ef9584daca57676e`  
**Latest published full checkpoint:** Taxo 10.4-r2 / `v10.4-r2` / `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`  
**Latest issued fast-test revision:** Taxo 10.5-r3 / `ca1a1288f915c3fa0eb57c82a3e91aea3b0887d1` — immutable  
**Latest fast-test START:** run `36359285033`, artifact `10944184721`, `440/440 OK`, SHA-256 `c48fbc67a40dddfd91da8e52d0a947633e403c7ca61508f3ab2525e1ca6020ee`  
**Checkpoint PR:** #74 — merged  
**Checkpoint main merge:** `271d43c0912e24c95014ac2a92ba2fc1695f4a11`  
**Full publisher:** run `36275440403` — success  
**Live ledger:** Issue #61  
**Наступний кодовий крок:** тільки `10.5-r4`.

## Джерело істини

Перед будь-якою новою роботою читати в такому порядку:

1. `START_HERE.md` — recovery/start protocol.
2. `PROJECT_RULES.md` — постійні правила розробки та релізів.
3. `PROJECT_STATE.md` — цей поточний checkpoint.
4. `WORKLOG.md` — завершений/активний крок.
5. `VERSION.txt` + `main.APP_VERSION` — поточна кодова identity.
6. `docs/releases/RELEASE_INDEX.md` — checkpoints.
7. Issue #61 — live ledger рішень і публікацій.

`v10.3` лишається immutable stable. `v10.4-r2` лишається останнім full multi-platform checkpoint у `main`. Fast-test revisions після нього є окремими START-checkpoint-ами і не підміняють stable/full release без окремого рішення власника.

## Обов’язкове версіювання

- Кожен завершений крок = нова ревізія `r1 → … → r10`.
- Після `r10` автоматично підвищується minor і починається `r1`.
- Уже видану для тестування ревізію повторно не використовувати.
- Перший розряд версії змінюється тільки за прямим рішенням власника.
- Після виданого `10.5-r3` будь-яка нова кодова зміна має йти як **10.5-r4**.
- При інтенсивній розробці основний тестовий пакет — START; Portable/Setup формуються на рідших/повних checkpoints.
- «Злити у main» для релізного checkpoint означає: перевірки → пакети → tag/release → PR → merge → документація.

## Taxo 10.5-r3 — latest fast-test checkpoint

### Функціональний обсяг

- створено єдиний реєстр документів працівників поверх вже існуючої таблиці `employee_documents`;
- друга таблиця/паралельний реєстр не створювались;
- ручні документи й документи, отримані з державних XLSX, показуються разом із видимим джерелом;
- реєстр містить ПІБ, тип, серію/номер, дату видачі, строк, орган видачі, джерело й стан;
- є пошук і фільтри за типом, станом, джерелом та архівністю;
- інформаційні стани: чинний / закінчується ≤30 днів / прострочений / строк не вказано або безстроковий / перевірити дату / архів;
- кольорова індикація не змінює документ автоматично;
- редагування використовує існуючий редактор документа в картці працівника;
- доступні відкриття файла, перехід до картки працівника та явне архівування;
- відсутність документа у свіжому державному витягу не видаляє, не очищає й не архівує локальні дані.

### Перевірки та пакет

- issued code head: `ca1a1288f915c3fa0eb57c82a3e91aea3b0887d1`;
- source regression: **440/440 OK**;
- START run: `36359285033` — success;
- artifact: `10944184721` / `Taxo_v10_5_candidate_r3_START`;
- size: `891392` bytes;
- SHA-256: `c48fbc67a40dddfd91da8e52d0a947633e403c7ca61508f3ab2525e1ca6020ee`;
- START guard підтвердив r1/r2/r3 runtime-файли й відсутність DB/SQLite/cache/development clutter.

## Попередні fast-test checkpoints

- `10.5-r2` — покомпонентна кольорова звірка ТЗ з «Шлях»; issued head `d9e7beefa52c7774e1b4bd6711dfc5907e06de37`; `425/425 OK`; artifact `10944042965`.
- `10.5-r1` — відомість військово-транспортного обліку по власному/балансовому транспорту; issued head `d7e5a730767ebc17e6935b2d3f25208a9f151c16`; `399/399 OK`; artifact `10943696206`.
- `10.4-r10` — військово-транспортний облік ТЗ; issued head `0f7944ad3f86bb6ee8ad19b40cfb2b38d924b934`; `388/388 OK`.
- `10.4-r9` — покомпонентна звірка працівників і військовий облік 2026.
- `10.4-r8` — імпорт/звірка ТЗ «Шлях» і нагадування про дні народження.

Усі видані fast-test checkpoints immutable.

## Taxo 10.4-r2 — актуальний full checkpoint

- P0/P1/P2 UI-remediation;
- незалежний контроль документів ТЗ, кілька активних документів одного типу, необов’язкова ДЦВ;
- waybill readability + кутовий штамп;
- source regression 300/300; Win7 Python 3.8 regression 300/300;
- Windows 7 PE scan success;
- modern Windows, Windows 7 SP1, macOS ARM64/Intel, START publishers success;
- tag/release `v10.4-r2`, exact target `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`;
- PR #74 merged у `main` → `271d43c0912e24c95014ac2a92ba2fc1695f4a11`;
- stable `v10.3` не змінено.

## Постійні межі даних

- робочі БД, SQLite-файли, скани, кеші й персональні документи не публікуються;
- державні XLSX/CSV є зовнішнім джерелом звірки/доповнення, а не заміною робочої БД;
- реєстрові дані можуть заповнювати порожні поля та створювати нові картки після підтвердження;
- порожнє/відсутнє у держреєстрі не видаляє й не очищає локальні дані;
- квартальна звірка реєстрів = один раз на календарний квартал; ручний свіжий імпорт дозволений будь-коли;
- локальний контроль документів ТЗ, «Шлях» і військово-транспортний облік — окремі контури;
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

Fast-test checkpoint `10.5-r3` завершений і immutable. Не продовжувати код у r3. Наступна кодова ревізія — тільки **10.5-r4**, в окремій work-гілці після повторного читання `START_HERE.md`, цього файла, `WORKLOG.md` та Issue #61.
