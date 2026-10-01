# PROJECT_STATE — Taxo

**Дата:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## Поточний підтверджений стан

- **Stable:** Taxo 10.3 / `v10.3` — immutable; stable promotion не змінювався.
- **Stable tag target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
- **Latest integrated code checkpoint:** Taxo **10.9-r1**.
- **Latest full multi-platform checkpoint:** Taxo **10.9-r1** / `v10.9-r1`.
- **Current main after closeout:** `8f18a7ccf1588556f6f3d7dca81943f87d817935`.
- **Latest issued fast-test:** **10.9-r7 / `v10.9-r7`** → `88fcfb20e8632178b095a99ef9b09c86701a072e` — immutable.
- **10.9-r7 START:** `Taxo_v10_9_candidate_r7_START.zip`, SHA-256 `8d35d2e8af76af1a90e9a6600b5d637d80fb80a28cb4d2331e85f9a336e88222`.
- **10.9-r7 exact-source regression:** **769/769 OK**; source `36916227610`, Windows `36916259871`, macOS `36916259785`, publisher `36916515063` — success.
- **Active development:** **10.9-r8 — накази / незмінність і закріплення**.
- **Active branch:** `work/v10.9-r8-orders-immutability`, based on frozen r7 source; unmerged.
- **Live ledger:** Issue #61.

`v10.3` лишається stable до окремого рішення власника. `v10.9-r1` є актуальним інтегрованим повним checkpoint. `v10.9-r2` … `v10.9-r7` є виданими stacked fast-test ревізіями, але не інтегровані в `main` без окремої команди власника.

## Issued stacked fast-test line 10.9-r2 … r7

- `v10.9-r2` — захист історії шляхівок/номерів і retention guards;
- `v10.9-r3` — чинність документів ТЗ протягом усього планового рейсу;
- `v10.9-r4` — контроль робочого часу/відпочинку, boundary gaps, overlaps, 3+9 і двотижневий контроль;
- `v10.9-r5` — 60-денний реєстр не вигадує відпочинок із невідомих хвилин; безпечний пріоритет тахографа;
- `v10.9-r6` — персонал/баланс/П-5: вихідний не зменшує норму як неявка, employment-aware history, тести 2/2 і 3/3;
- `v10.9-r7` — СТОІР: надійна хронологія одометра, fallback `work_date`, newest-fact forecast anchor і outlier guard.

Усі ці checkpoints immutable; відповідні PR лишаються stacked draft/unmerged до прямої команди власника про інтеграцію.

## Active slice — 10.9-r8

Мета r8: зробити юридично/операційно значущі накази незмінними після затвердження/підпису та прибрати неоднозначність закріплень водія за ТЗ.

Підтверджені й реалізовані правила:

- approved/signed наказ не редагується як чернетка;
- cancelled наказ не можна повторно затвердити;
- непереданий `control_employee_id` не очищає відповідального;
- assignments під approved/signed наказом незмінні;
- конфліктні одночасні закріплення одного водія за різними ТЗ у новому наказі блокують approval;
- одне однозначне попереднє закріплення завершується новим наказом окремим фактом, без переписування старого затвердженого наказу;
- runtime layer: `v1098_orders_immutability.py`;
- behavioral tests: `tests/test_v10_9_r8.py`;
- audit: `docs/maintenance/AUDIT_OPERATIONS_ORDERS_v10.9-r8.md`;
- release notes: `docs/releases/RELEASE_NOTES_v10.9-r8.md`.

## Архітектурний напрямок

Великий `main.py` поступово розвантажується без масового переписування бізнес-логіки:

- `output_files.py` — нейтральна file-output інфраструктура;
- `feature_layers.py` — централізований ordered registry runtime layers;
- `application_context.py` — explicit application/infrastructure services;
- `backup_migration.py` — backup/restore/legacy migration mechanics;
- `database_runtime.py` — єдина SQLite connection policy;
- `data_access.py` — доменно-нейтральний data-access/transaction boundary для нових модулів.

Нові великі можливості слід будувати в напрямку `domain → service → repository/data access → infrastructure`, а UI залишати зовнішнім шаром.

## Full checkpoint 10.9-r1

Full-package run `36857771398` перевірив exact immutable source та сформував Windows x64 Portable/Setup, Windows 7 SP1 x64 Portable/Setup + PE compatibility gate, macOS arm64/x86_64 Portable, START/source і checksum manifests.

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
- виданий revision не перевидається; після `10.9-r7` наступна кодова ревізія — `10.9-r8`.

## Право та власність

Taxo — proprietary software.  
Правовласник: **Roman Zavada (Роман Завада), фізична особа**.  
**Copyright © 2026 Roman Zavada. All rights reserved.**

Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Джерело істини при новій сесії

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → live GitHub state → Issue #61.

При суперечності документації з live GitHub перемагає фактичний GitHub state. Нову кодову роботу починати від exact immutable source попередньої stacked ревізії, якщо це явно зафіксовано в активному work slice.
