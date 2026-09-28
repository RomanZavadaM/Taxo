# Taxo — поточна контрольна точка

**Дата:** 28.09.2026  
**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Previous stable / rollback:** Taxo 10.1 / `v10.1`  
**Latest full checkpoint in `main`:** Taxo 10.5-r8 / `v10.5-r8`  
**Issued source:** `846e5c5111b14a4a1f2e49203803e86c495b458f`  
**PR #76:** merged  
**Main merge:** `eb9cb039d35419fb579ff0f5e1b9c633c95ccd86`  
**Full publisher:** `36406419955` — success  
**Regression:** `483/483 OK`  
**Packages:** modern Windows Setup/Portable + Windows 7 SP1 Setup/Portable + macOS ARM64/Intel + START + SHA-256  
**Next code revision:** `10.5-r9`  
**Recovery:** `START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8

## Gate result

Повний checkpoint пройшов:

- source regression: **483/483 OK**;
- modern Windows package build: success;
- Windows 7 compatibility line / Python 3.8: success;
- macOS ARM64: success;
- macOS Intel x86_64: success;
- START package: success;
- release publication: success;
- PR #76 merge into `main`: success.

## Основна зміна r8

Виправлено вузьку сумісність XLSX «Шлях» на Windows 7 / Python 3.8: openpyxl може повертати короткий `TypeError` `unexpected keyword argument 'tabId'` без `ChildSheet`. Compatibility retry виконується тільки для цього фактичного випадку та не змінює вихідний XLSX.

## Політика

- `v10.3` лишається stable до окремого рішення власника;
- `v10.5-r8` — повний candidate/checkpoint і immutable після видачі;
- r8 не перевидається і не пересувається;
- наступна кодова зміна — тільки `10.5-r9`;
- робочі БД, скани, кеші та персональні документи не входять у release;
- plan/fact, державні snapshots і робочі редаговані дані лишаються розділеними.

Канонічний стан: [../../PROJECT_STATE.md](../../PROJECT_STATE.md).  
Канонічні правила: [../../PROJECT_RULES.md](../../PROJECT_RULES.md).  
Release notes: [../releases/RELEASE_NOTES_v10_5_r8.md](../releases/RELEASE_NOTES_v10_5_r8.md).  
Release index: [../releases/RELEASE_INDEX.md](../releases/RELEASE_INDEX.md).

Правовласник: **Roman Zavada (Роман Завада)**. Copyright © 2026 Roman Zavada. All rights reserved.
