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
- **Latest issued fast-test:** **10.9-r6 / `v10.9-r6`** → `531723c1b7e9cb9c3d0258d085819381981de14c` — immutable.
- **10.9-r6 START:** `Taxo_v10_9_candidate_r6_START.zip`, SHA-256 `fc003b71347a65e3ee5fa998392e254903f19af6e899a2cec9d3ef2155da9882`.
- **10.9-r6 exact-source regression:** **761/761 OK**; publisher `36914902396`, source `36914019199`, Windows `36914025872`, macOS `36914025948` — success.
- **Active development:** **10.9-r7 — СТОІР / одометр і прогноз ТО**.
- **Active branch:** `work/v10.9-r7-stoir-odometer-safety`, based on frozen r6 source; unmerged.
- **Live ledger:** Issue #61.

`v10.3` лишається stable до окремого рішення власника. `v10.9-r1` є актуальним інтегрованим повним checkpoint. `v10.9-r2` … `v10.9-r6` є виданими stacked fast-test ревізіями, але не інтегровані в `main` без окремої команди власника.

## Issued stacked fast-test line 10.9-r2 … r6

- `v10.9-r2` — захист історії шляхівок/номерів і retention guards;
- `v10.9-r3` — чинність документів ТЗ протягом усього планового рейсу;
- `v10.9-r4` — контроль робочого часу/відпочинку, boundary gaps, overlaps, 3+9 і двотижневий контроль;
- `v10.9-r5` — 60-денний реєстр не вигадує відпочинок із невідомих хвилин; безпечний пріоритет тахографа;
- `v10.9-r6` — персонал/баланс/П-5: вихідний не зменшує норму як неявка, історичний employment-aware mapping, тести 2/2 і 3/3.

Усі ці checkpoints immutable; відповідні PR лишаються stacked draft/unmerged до прямої команди власника про інтеграцію.

## Active slice — 10.9-r7

Мета r7: перевірити й виправити підтверджені ризики СТОІР навколо одометра та прогнозування ТО:

- fallback `work_date`, коли `reading_at` відсутній;
- вибір справді останнього фактичного показника, включно зі шляхівкою;
- коректні точки для середнього добового пробігу;
- прогноз від дати останньої надійної точки, а не автоматично від сьогодні;
- захист середнього від одиничного очевидного викиду;
- чинне правило взаємодії ТО-1/ТО-2 спершу перевірити і не міняти без підтвердженої необхідності.

Перед змінами — поведінкові тести на тимчасовій SQLite-БД. PR r7 не зливати без прямої команди власника.

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
- видана шляхівка та історично використаний номер захищені від тихого фізичного знищення/повторного використання;
- робочі БД, SQLite, скани, кеші та персональні документи не входять у repository/release;
- історичні tag/release checkpoints immutable;
- старі work/tmp branches не використовуються як джерело коду для нової розробки;
- виданий revision не перевидається; після `10.9-r6` наступна кодова ревізія — `10.9-r7`.

## Право та власність

Taxo — proprietary software.  
Правовласник: **Roman Zavada (Роман Завада), фізична особа**.  
**Copyright © 2026 Roman Zavada. All rights reserved.**

Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Джерело істини при новій сесії

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → live GitHub state → Issue #61.

При суперечності документації з live GitHub перемагає фактичний GitHub state. Нову кодову роботу починати від актуального інтегрованого baseline або exact immutable source попередньої stacked ревізії, якщо це явно зафіксовано в активному work slice.
