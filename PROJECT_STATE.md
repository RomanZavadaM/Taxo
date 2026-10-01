# PROJECT_STATE — Taxo

**Дата:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## Поточний підтверджений стан

- **Stable:** Taxo 10.3 / `v10.3` — immutable; stable promotion не змінювався.
- **Stable tag target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
- **Latest integrated code checkpoint:** Taxo **10.9-r1**.
- **Latest full multi-platform checkpoint:** Taxo **10.9-r1** / `v10.9-r1`.
- **Main integration:** PR #118 merged у `main`.
- **Main merge commit:** `843a38243dd4eeeb02b40f8de59cc630ef4dce09`.
- **Immutable issued source/tag:** `v10.9-r1` → `b0eebbf88b22fbd7761544640d9804416a328acb` — не пересувати.
- **START:** `Taxo_v10_9_candidate_r1_START.zip`.
- **START SHA-256:** `0c819f9f3e4b31f58e6b86e2b4f1d72086901c0bd2a26a499e4c17f6de9c1766`.
- **Exact-source regression:** **730/730 OK**.
- **Full-package run:** `36857771398` — success.
- **Published packages:** Windows x64 Setup/Portable; Windows 7 SP1 x64 Setup/Portable + PE compatibility gate; macOS arm64/x86_64 Portable; START; platform/full SHA-256 manifests.
- **Open PRs after cleanup:** none before documentation closeout PR.
- **Next code revision:** **10.9-r2**.
- **Live ledger:** Issue #61.

`v10.3` лишається stable до окремого рішення власника. `v10.9-r1` є актуальним інтегрованим повним checkpoint для тестування і розвитку, але не є автоматичним stable promotion.

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

Full-package run `36857771398` перевірив exact immutable source та успішно сформував повний комплект:

- Windows x64 Portable;
- Windows x64 Setup;
- Windows 7 SP1 x64 Portable;
- Windows 7 SP1 x64 Setup;
- macOS arm64 Portable;
- macOS x86_64 Portable;
- START/source;
- окремі platform SHA-256 і загальний `SHA256SUMS_v10_9_r1_ALL.txt`.

Windows 7 line зберігається на CPython 3.8.10 x64 + PyInstaller 5.13.2 з PE compatibility gate. БД, SQLite, кеші, скани та персональні документи в release не включаються.

## Cleanup після інтеграції

Кумулятивний PR #118 замінив потребу в окремому злитті старих stacked PR. Закриті як проміжні/тупикові хвости: #108–#113, #103, #94, #93, #91; #107 був закритий після кумулятивної інтеграції. Їхні immutable tags/releases і Git history зберігаються як історичні checkpoints, але ці PR/гілки не використовуються як кодова база нової розробки.

Remote branch refs можуть залишатися як історичні refs, але не є джерелом актуального коду. Нова робота починається тільки від поточного `main`.

## Чинні функціональні інваріанти

- plan і fact зберігаються окремо;
- факт не підміняється планом без явного підтвердження користувача там, де така підстановка дозволена;
- Бланки підтвердження діяльності є фактичними документами;
- ручний/некласифікований час не перетворюється автоматично на роботу чи відпочинок;
- роль водія має датовані періоди і не дорівнює факту працевлаштування;
- робочі БД, SQLite, скани, кеші та персональні документи не входять у repository/release;
- історичні tag/release checkpoints immutable;
- старі work/tmp branches не використовуються як джерело коду для нової розробки;
- виданий revision не перевидається; після `10.9-r1` наступна кодова зміна — `10.9-r2`.

## Право та власність

Taxo — proprietary software.  
Правовласник: **Roman Zavada (Роман Завада), фізична особа**.  
**Copyright © 2026 Roman Zavada. All rights reserved.**

Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Джерело істини при новій сесії

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → live GitHub state → Issue #61.

При суперечності документації з live GitHub перемагає фактичний GitHub state. Нову кодову роботу починати від актуального `main`, а не від historical work/candidate/tmp branches.