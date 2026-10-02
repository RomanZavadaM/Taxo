# WORKLOG — Taxo

**Оновлено:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated code checkpoint:** **10.9-r1**  
**Latest full multi-platform checkpoint:** **10.9-r1 / `v10.9-r1`**  
**Latest issued fast-test:** **10.9-r8 / `v10.9-r8`**  
**Current active slice:** **10.9-r9 — сумісність схеми SQLite**  
**Integrated main baseline:** `8f18a7ccf1588556f6f3d7dca81943f87d817935`  
**Active branch:** `work/v10.9-r9-schema-compatibility`  
**Base:** immutable `v10.9-r8` → `b8c3fb2d19323e8c9564eedc2f0540250dd51b29`  
**Stable remains:** `v10.3`  
**Live ledger:** Issue #61

## DONE — 10.9-r8 immutable issuance

10.9-r8 закрив ризики наказів і закріплень:

- approved/signed наказ незмінний;
- cancelled наказ не можна повторно approve;
- omitted `control_employee_id` не очищає відповідального;
- assignments під approved/signed наказом незмінні;
- конфліктні simultaneous driver→vehicle assignments блокують approval;
- одне однозначне попереднє закріплення завершується новим наказом окремим фактом без переписування старого наказу.

Immutable source: `b8c3fb2d19323e8c9564eedc2f0540250dd51b29`.  
Exact-source regression: **777/777 OK**.  
Gates: source `36917874768`, Windows `36917897671`, macOS `36917897612`, publisher `36918132266` — success.  
Release: `v10.9-r8` / https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r8  
START: `Taxo_v10_9_candidate_r8_START.zip`  
SHA-256: `01698663d3bb01e4461bf49479bce46fb3688d72ea23854cd9557370473a6775`.

PR #127 лишається draft/unmerged. `main` не змінено.

## DOING — 10.9-r9

Ціль: **ввести explicit SQLite schema compatibility baseline без ризикованого переписування historical `init_db()`**.

Реалізовано:

1. `database_runtime.py` використовує `PRAGMA user_version`;
2. schema numbering незалежний від версії програми: legacy=`0`, r9 baseline=`1`;
3. legacy DB `user_version=0` відкривається без неявного stamp;
4. DB із schema version `>1` відхиляється через `SchemaTooNewError` до доменної роботи;
5. baseline `1` ставиться тільки після успішного чинного `init_db()`;
6. failed `init_db()` не оголошує частково змінену базу успішно мігрованою;
7. schema version helper не дозволяє downgrade.

Технічно:

- compatibility helpers у `database_runtime.py`;
- additive runtime layer `v1099_schema_compatibility.py`;
- `tests/test_v10_9_r9.py` — поведінкові SQLite-сценарії;
- machine identity = `10.9-r9`;
- feature layer `v1099-schema-compatibility` у domain `infrastructure`;
- START/source package guards вимагають r9 runtime;
- аудит: `docs/maintenance/AUDIT_SCHEMA_COMPATIBILITY_v10.9-r9.md`;
- release notes: `docs/releases/RELEASE_NOTES_v10.9-r9.md`.

Обмеження: binaries до r9 не знають про `user_version`, тому future-schema guard гарантований від r9 і далі, а не ретроспективно.

## NEXT

1. Отримати результат full source regression для r9 та виправити тільки фактичні regression failures, якщо вони є.
2. Прибрати тимчасовий integration workflow із кандидатної гілки.
3. Синхронізувати `PROJECT_STATE.md` через issued r8 / active r9.
4. Відкрити draft PR r9 поверх frozen r8.
5. Прогнати exact-head source/START + Windows/macOS gates.
6. Якщо gates зелені — видати immutable `v10.9-r9` START+checksum і зафіксувати в PR/Issue #61.
7. Не зливати в `main` без прямої команди власника.
