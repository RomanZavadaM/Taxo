# PROJECT_STATE — Taxo

**Дата:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## Поточний підтверджений стан

- **Stable:** Taxo 10.3 / `v10.3` — immutable; stable promotion не змінювався.
- **Stable tag target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
- **Latest integrated code checkpoint:** Taxo **10.9-r1**.
- **Latest full multi-platform checkpoint:** Taxo **10.9-r1** / `v10.9-r1`.
- **Main integration:** PR #118 merged у `main`.
- **Code merge commit:** `843a38243dd4eeeb02b40f8de59cc630ef4dce09`.
- **Documentation closeout:** PR #119 merged.
- **Current main after closeout:** `8f18a7ccf1588556f6f3d7dca81943f87d817935`.
- **Immutable issued 10.9-r1:** `v10.9-r1` → `b0eebbf88b22fbd7761544640d9804416a328acb`.
- **Latest issued fast-test:** **10.9-r2 / `v10.9-r2`** → `03ad7a01411c63aeb3d17eaebe0b1b59a27726ff` — immutable.
- **10.9-r2 START:** `Taxo_v10_9_candidate_r2_START.zip`, SHA-256 `81ee180c46e8b3d56002c275525a6e604257b27d6a925ad33823eb0a0ea4b716`.
- **10.9-r2 exact-source regression:** **734/734 OK**; publisher `36872542242`, source `36872542116`, Windows `36872548774`, macOS `36872548762` — success.
- **Active development:** **10.9-r3 — vehicle-document validity for the full trip**.
- **Active branch:** `work/v10.9-r3-vehicle-document-validity`.
- **Draft PR:** #122, based on frozen r2 branch; unmerged.
- **Live ledger:** Issue #61.

`v10.3` лишається stable до окремого рішення власника. `v10.9-r1` є актуальним інтегрованим повним checkpoint. `v10.9-r2` є виданою fast-test ревізією, але не інтегрована в `main` без окремої команди власника.

## Active slice — 10.9-r3

Мета r3: обов'язкові документи ТЗ повинні бути чинними протягом **усього планового рейсу**.

Реалізовано:

- оперативний контроль враховує `valid_from`;
- `valid_until` перевіряється до дати завершення рейсу;
- кілька активних документів одного типу можуть безперервно перекрити один багатоденний рейс;
- архівні документи не використовуються для нового рейсу;
- legacy записи без `valid_from` залишаються сумісними;
- тимчасовий реєстраційний документ стає обов'язковим лише для ТЗ з відповідною ознакою;
- ДЦВ лишається необов'язковим;
- ручне архівування і можливість мати кілька документів одного типу не змінені;
- шляхівка передає в документний контроль плановий діапазон `date` → `end_date`;
- новий layer `v1093-vehicle-document-validity` підключений після r2;
- START/source guards включають `vehicle_document_validity.py`;
- додані поведінкові SQLite-тести r3.

Перед issuance r3 обов'язкові повний regression/START та Windows/macOS gates на exact source, після чого immutable tag/prerelease/checksum. PR #122 не зливати без прямої команди власника.

## Що інтегровано від 10.8-r4 до 10.9-r1

### СТОІР

- модуль технічного обслуговування й ремонту ТЗ;
- профілі ТО та фактичний одометр;
- прогноз ТО-1/ТО-2 за наявною історією пробігу;
- заявки на несправності/ремонт і зведення по автопарку;
- компактний UI зі скролами та діями над вибраним рядком.

### Архітектурне розвантаження

Великий `main.py` поступово розвантажується без масового переписування бізнес-логіки:

- `output_files.py` — нейтральна file-output інфраструктура;
- `feature_layers.py` — централізований ordered registry runtime layers;
- `application_context.py` — explicit application/infrastructure services;
- `backup_migration.py` — backup/restore/legacy migration mechanics;
- `database_runtime.py` — єдина SQLite connection policy;
- `data_access.py` — доменно-нейтральний data-access/transaction boundary для нових модулів.

Нові великі можливості слід будувати в напрямку `domain → service → repository/data access → infrastructure`, а UI залишати зовнішнім шаром. `ApplicationServices` не є service locator для бізнес-правил.

## Full checkpoint 10.9-r1

Full-package run `36857771398` перевірив exact immutable source та успішно сформував повний комплект: Windows x64 Portable/Setup; Windows 7 SP1 x64 Portable/Setup + PE compatibility gate; macOS arm64/x86_64 Portable; START/source; platform/full SHA-256 manifests.

Windows 7 line зберігається на CPython 3.8.10 x64 + PyInstaller 5.13.2 з PE compatibility gate. БД, SQLite, кеші, скани та персональні документи в release не включаються.

## Чинні функціональні інваріанти

- plan і fact зберігаються окремо;
- факт не підміняється планом без явного підтвердження користувача там, де така підстановка дозволена;
- Бланки підтвердження діяльності є фактичними документами;
- ручний/некласифікований час не перетворюється автоматично на роботу чи відпочинок;
- роль водія має датовані періоди і не дорівнює факту працевлаштування;
- видана шляхівка та історично використаний номер захищені від тихого фізичного знищення/повторного використання r2;
- робочі БД, SQLite, скани, кеші та персональні документи не входять у repository/release;
- історичні tag/release checkpoints immutable;
- старі work/tmp branches не використовуються як джерело коду для нової розробки;
- виданий revision не перевидається; після `10.9-r2` наступна кодова ревізія — `10.9-r3`.

## Право та власність

Taxo — proprietary software.  
Правовласник: **Roman Zavada (Роман Завада), фізична особа**.  
**Copyright © 2026 Roman Zavada. All rights reserved.**

Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Джерело істини при новій сесії

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → live GitHub state → Issue #61.

При суперечності документації з live GitHub перемагає фактичний GitHub state. Нову кодову роботу починати від актуального інтегрованого baseline або exact immutable source попередньої stacked ревізії, якщо це явно зафіксовано в активному work slice.
