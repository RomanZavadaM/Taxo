# Taxo — поточна контрольна точка

**Дата:** 02.10.2026  
**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Previous stable / rollback:** Taxo 10.1 / `v10.1`  
**Latest integrated checkpoint in `main`:** **Taxo 10.9-r10**  
**Structural cleanup PR:** #132  
**Exact r10 source:** `ff56519da35e03204bdaf77f7187cddd692f79d4`  
**Main merge:** `5e179eabccc35afa984be04208e2e4d96094a2fb`  
**Exact-head Windows:** `37018721703` — success  
**Exact-head Windows 7:** `37018721695` — success  
**Exact-head macOS:** `37018722335` — success  
**Latest full multi-platform published checkpoint:** `10.9-r9 / v10.9-r9`  
**Next code revision:** `10.10-r1`  
**Recovery:** `START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61

## Gate result

10.9-r10 пройшов exact-head platform gates до інтеграції:

- Windows — **success**;
- Windows 7 compatibility — **success**;
- macOS ARM64/Intel source/build — **success**;
- PR #132 merged у `main`.

## Зміст 10.9-r10

- `src/taxo/` — runtime/support Python modules;
- `assets/` — runtime templates;
- `packaging/` — active build and installer definitions;
- `packaging/history/` — historical packaging specs;
- START/Windows/Win7/macOS paths приведені до нового layout;
- business logic і user-data contracts не змінювалися;
- database/workspace/backup migration не вводилась.

## Політика

- `v10.3` лишається stable до окремого рішення власника;
- `10.9-r10` — поточний integrated code checkpoint;
- latest already published full multi-platform checkpoint — `v10.9-r9`;
- цикл 10.9 закрито на r10;
- наступна кодова зміна — тільки `10.10-r1` від актуального `main`;
- `11.x` — тільки за прямим рішенням власника;
- робочі БД, скани, кеші та персональні документи не входять у release.

Канонічний стан: [../../PROJECT_STATE.md](../../PROJECT_STATE.md).  
Канонічні правила: [../../PROJECT_RULES.md](../../PROJECT_RULES.md).  
Release notes: [../releases/RELEASE_NOTES_v10.9-r10.md](../releases/RELEASE_NOTES_v10.9-r10.md).  
Release index: [../releases/RELEASE_INDEX.md](../releases/RELEASE_INDEX.md).

Правовласник: **Roman Zavada (Роман Завада)**. Copyright © 2026 Roman Zavada. All rights reserved.
