# Taxo — поточна контрольна точка

**Дата:** 02.10.2026  
**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Previous stable / rollback:** Taxo 10.1 / `v10.1`  
**Latest integrated checkpoint in `main`:** Taxo 10.9-r9 / `v10.9-r9`  
**Issued source:** `a368bf3bdfd4a16cc099844b830379c5e2646c2d`  
**Cumulative integration:** PR #128  
**Main code merge:** `3f59544b8737cd4715d84f786e32378d87d1dd99`  
**Documentation closeout:** PR #129 → `34a56e05133bedfc81e6273ea572f6e9757ddab7`  
**Exact-head Windows:** `36919102579` — success  
**Exact-head macOS:** `36919102540` — success  
**Packages:** modern Windows Setup/Portable + Windows 7 SP1 Setup/Portable + macOS ARM64/Intel + START + SHA-256  
**Next code revision:** `10.9-r10`  
**Recovery:** `START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9

## Gate result

10.9-r9 пройшов exact-head source gates до інтеграції:

- Windows: **success**;
- macOS: **success**;
- START package: опубліковано;
- cumulative PR #128: merged;
- public documentation closeout PR #129: merged;
- full multi-platform user packages: Windows x64, Windows 7 SP1 x64, macOS ARM64/Intel доповнені до release v10.9-r9.

## Основні зміни cumulative 10.9-r2 → r9

- незворотна історія виданих шляхівок і номерів;
- чинність документів ТЗ на весь рейс;
- work/rest compliance hardening;
- безпечніша семантика 60-денного activity register;
- historical employment/P-5 safety;
- надійніша хронологія одометра і STOIR forecast;
- immutable approved/signed orders та driver→vehicle assignment safety;
- explicit SQLite schema compatibility baseline через `PRAGMA user_version`.

## Політика

- `v10.3` лишається stable до окремого рішення власника;
- `v10.9-r9` — поточний integrated candidate/checkpoint і не перевидається як інший код;
- наступна кодова зміна — тільки `10.9-r10`;
- робочі БД, скани, кеші та персональні документи не входять у release;
- plan/fact, державні snapshots і робочі редаговані дані лишаються розділеними.

Канонічний стан: [../../PROJECT_STATE.md](../../PROJECT_STATE.md).  
Канонічні правила: [../../PROJECT_RULES.md](../../PROJECT_RULES.md).  
Release notes: [../releases/RELEASE_NOTES_v10.9-r9.md](../releases/RELEASE_NOTES_v10.9-r9.md).  
Release index: [../releases/RELEASE_INDEX.md](../releases/RELEASE_INDEX.md).

Правовласник: **Roman Zavada (Роман Завада)**. Copyright © 2026 Roman Zavada. All rights reserved.
