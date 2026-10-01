# PROJECT_STATE — Taxo

**Дата:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## Поточний підтверджений стан

- **Stable:** Taxo 10.3 / `v10.3` — immutable; stable promotion не змінювався.
- **Stable tag target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
- **Latest integrated code checkpoint:** Taxo **10.9-r1**.
- **Latest full multi-platform checkpoint:** Taxo **10.9-r1** / `v10.9-r1`.
- **Current main after closeout:** `8f18a7ccf1588556f6f3d7dca81943f87d817935`.
- **Latest issued fast-test:** **10.9-r8 / `v10.9-r8`** → `b8c3fb2d19323e8c9564eedc2f0540250dd51b29` — immutable.
- **10.9-r8 START:** `Taxo_v10_9_candidate_r8_START.zip`, SHA-256 `01698663d3bb01e4461bf49479bce46fb3688d72ea23854cd9557370473a6775`.
- **10.9-r8 exact-source regression:** **777/777 OK**; source `36917874768`, Windows `36917897671`, macOS `36917897612`, publisher `36918132266` — success.
- **Active development:** **10.9-r9 — сумісність схеми SQLite**.
- **Active branch:** `work/v10.9-r9-schema-compatibility`, based on frozen r8 source; unmerged.
- **Live ledger:** Issue #61.

`v10.3` лишається stable до окремого рішення власника. `v10.9-r1` є актуальним інтегрованим повним checkpoint. `v10.9-r2` … `v10.9-r8` є виданими stacked fast-test ревізіями, але не інтегровані в `main` без окремої команди власника.

## Issued stacked fast-test line 10.9-r2 … r8

- `v10.9-r2` — захист історії шляхівок/номерів і retention guards;
- `v10.9-r3` — чинність документів ТЗ протягом усього планового рейсу;
- `v10.9-r4` — контроль робочого часу/відпочинку, boundary gaps, overlaps, 3+9 і двотижневий контроль;
- `v10.9-r5` — 60-денний реєстр не вигадує відпочинок із невідомих хвилин; безпечний пріоритет тахографа;
- `v10.9-r6` — персонал/баланс/П-5: вихідний не зменшує норму як неявка, employment-aware history, тести 2/2 і 3/3;
- `v10.9-r7` — СТОІР: надійна хронологія одометра, fallback `work_date`, newest-fact forecast anchor і outlier guard;
- `v10.9-r8` — накази: immutable approved/signed documents, безпечний controller update та взаємовиключні driver→vehicle assignments.

Усі ці checkpoints immutable; відповідні PR лишаються stacked draft/unmerged до прямої команди власника про інтеграцію.

## Active slice — 10.9-r9

Мета r9: ввести explicit SQLite schema compatibility baseline без ризикованого переписування historical `init_db()`.

- schema numbering незалежний від application version;
- legacy DB = `user_version=0`;
- r9 baseline = `SUPPORTED_SCHEMA_VERSION=1`;
- simple open legacy DB не змінює її version;
- r9 відмовляється відкривати DB із `user_version > 1`;
- baseline 1 ставиться тільки після успішного historical `init_db()`;
- failed `init_db()` не ставить schema stamp;
- schema helper не дозволяє downgrade;
- runtime layer: `v1099_schema_compatibility.py`;
- behavioral tests: `tests/test_v10_9_r9.py`;
- audit: `docs/maintenance/AUDIT_SCHEMA_COMPATIBILITY_v10.9-r9.md`;
- release notes: `docs/releases/RELEASE_NOTES_v10.9-r9.md`.

Обмеження: binaries до r9 не знають про `user_version`; future-schema guard гарантований від r9 і наступних версій.

## Архітектурний напрямок

Нові великі можливості слід будувати в напрямку `domain → service → repository/data access → infrastructure`, а UI залишати зовнішнім шаром. Чинні інфраструктурні точки: `application_context.py`, `feature_layers.py`, `database_runtime.py`, `data_access.py`, `backup_migration.py`, `output_files.py`.

## Чинні інваріанти

- plan і fact зберігаються окремо;
- факт не підміняється планом без явного підтвердження там, де така підстановка дозволена;
- Бланки підтвердження діяльності є фактичними документами;
- невідомий час не перетворюється автоматично на роботу чи відпочинок;
- роль водія має датовані періоди і не дорівнює факту працевлаштування;
- видана шляхівка та історично використаний номер захищені від тихого фізичного знищення/повторного використання;
- робочі БД, SQLite, скани, кеші та персональні документи не входять у repository/release;
- historical tag/release checkpoints immutable;
- виданий revision не перевидається; після `10.9-r8` наступна кодова ревізія — `10.9-r9`.

## Право та власність

Taxo — proprietary software.  
Правовласник: **Roman Zavada (Роман Завада), фізична особа**.  
**Copyright © 2026 Roman Zavada. All rights reserved.**

Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Джерело істини при новій сесії

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → live GitHub state → Issue #61.

При суперечності документації з live GitHub перемагає фактичний GitHub state.
