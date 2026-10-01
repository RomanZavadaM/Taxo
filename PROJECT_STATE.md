# PROJECT_STATE — Taxo

**Дата:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## Поточний підтверджений стан

- **Stable:** Taxo 10.3 / `v10.3` — immutable.
- **Stable tag target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
- **Latest full multi-platform checkpoint:** Taxo **10.8-r3** / `v10.8-r3`.
- **Latest integrated code checkpoint in `main`:** Taxo **10.8-r3**.
- **Current `main`:** `50db4b0de4d37260c2031aa96317fef61d93ea90`.
- **Main merge for r3:** PR #105 → `db444a37ead421c8083558cfcf81ee97adc241f6`.
- **Issued r3 tag/source:** `v10.8-r3` → `d8ec901b9b80f74b5b85cd1bda202dd58c86a7bd` — не пересувати.
- **Latest issued fast-test:** Taxo **10.8-r9** / `v10.8-r9`.
- **r9 exact source:** `d8d29c79b82b53a0ad07df18dbbe19cf5f5d00c1`.
- **r9 START:** `Taxo_v10_8_candidate_r9_START.zip`.
- **r9 START SHA-256:** `f1d37e4111ff780f46dc3736bdec093ee31e95ba896437d9902b87967113b0ac`.
- **r9 regression:** 719/719 OK.
- **r9 Windows/macOS gates:** success.
- **Active code revision:** **10.8-r10**.
- **Active branch:** `work/v10.8-r10-database-runtime-infrastructure`.
- **Active draft PR:** #113, base `work/v10.8-r9-backup-migration-infrastructure`.
- **Live ledger:** Issue #61.

`v10.3` залишається stable до окремого рішення власника. `10.8-r4`…`10.8-r9` — послідовні fast-test/architecture slices, які не інтегруються у `main` без прямої команди власника.

## Повний multi-platform checkpoint 10.8-r3

У `v10.8-r3` опубліковано й перевірено START, Windows x64 Portable+Setup, Windows 7 SP1 x64 Portable+Setup, macOS arm64+x86_64 Portable та checksums. Windows 7 line зберігається на CPython 3.8.10 x64 + PyInstaller 5.13.2 з PE compatibility gate.

## Видані fast-test checkpoints після r3

Послідовність r4→r9 ведеться як chained draft PRs без злиття у `main`. Уже видані revisions immutable; наступна зміна не робиться під уже виданим номером.

Останній виданий checkpoint — `10.8-r9`:

- PR #112 draft/open;
- exact source `d8d29c79b82b53a0ad07df18dbbe19cf5f5d00c1`;
- tag/prerelease `v10.8-r9`;
- publisher `36823663607` — success;
- source package `36823663413` — success;
- Windows gate `36823668396` — success;
- macOS gate `36823668394` — success;
- regression 719/719 OK;
- `backup_migration.py` із low-level backup/restore/legacy migration mechanics;
- `main.py` зберігає compatibility wrappers;
- r9 заморожений.

## Active 10.8-r10

Мета r10 — ще один малий infrastructure slice: винесення SQLite connection policy з `main.py` у `database_runtime.py`.

Реалізовано:

- `database_runtime.connect_database(path)`;
- збережено чинні timeout/row factory/PRAGMA налаштування;
- `main.db()` лишено compatibility wrapper;
- поточний `DB_PATH` передається при кожному відкритті, тому workspace switching не змінює semantics;
- `START.bat` вимагає новий модуль;
- додано `tests/test_v10_8_r10.py`;
- додано audit і release notes;
- PR #113 створено draft/open;
- `main` не змінювався.

Перед issuance r10 обов'язкові exact-head regression, START package verification, Windows/macOS gates, immutable tag/prerelease та запис exact source/SHA у Issue #61 і PR #113. Після issuance r10 наступна кодова зміна — **10.9-r1**.

## Чинні функціональні інваріанти

- plan і fact зберігаються окремо;
- факт не підміняється планом без явного підтвердження користувача там, де така підстановка дозволена;
- Бланки підтвердження діяльності є фактичними документами;
- ручний/некласифікований час не перетворюється автоматично на роботу чи відпочинок;
- роль водія має датовані періоди і не дорівнює факту працевлаштування;
- робочі БД, SQLite, скани, кеші та персональні документи не входять у repository/release;
- історичні tag/release checkpoints immutable;
- старі work/tmp branches не використовуються як джерело коду для нової розробки;
- кожен виданий revision не перевидається; після r10 наступний revision — r1 наступної minor version.

## Право та власність

Taxo — proprietary software.  
Правовласник: **Roman Zavada (Роман Завада), фізична особа**.  
**Copyright © 2026 Roman Zavada. All rights reserved.**

Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Джерело істини при новій сесії

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → live GitHub state → Issue #61.

При суперечності документації з live GitHub перемагає фактичний GitHub state; документи синхронізуються у поточній незамороженій ревізії.
