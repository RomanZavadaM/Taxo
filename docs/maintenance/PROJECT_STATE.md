# Taxo — технічний стан

Цей файл є коротким технічним дзеркалом канонічного [PROJECT_STATE.md](../../PROJECT_STATE.md). Історичні checkpoint-и не дублюються тут: вони збережені в Git history, release notes та Issue #61.

**Дата:** 28.09.2026  
**Stable:** Taxo 10.3 / `v10.3`  
**Previous stable / rollback:** Taxo 10.1 / `v10.1`  
**Latest full checkpoint in `main`:** Taxo 10.5-r8 / `v10.5-r8`  
**Issued source:** `846e5c5111b14a4a1f2e49203803e86c495b458f`  
**Main merge:** `eb9cb039d35419fb579ff0f5e1b9c633c95ccd86` via PR #76  
**Release workflow:** `36406419955` — success  
**Regression:** `483/483 OK`  
**Next code revision:** `10.5-r9`

## Технічні інваріанти

- Plan != Fact.
- Exact intervals мають пріоритет над duration-only.
- Duration-only не створює вигаданих часових меж.
- Historical conflicts не переписуються автоматично.
- Employment state != driver role.
- Державні raw snapshots не переписуються локальними робочими змінами.
- Порожнє значення в державному джерелі не очищає локальні дані автоматично.
- Taxo не оголошує локальну підготовку фактом державної операції.
- Робочі БД/SQLite/скани/кеші/персональні документи не входять у release.
- Оновлення програми не повинно вимагати повторного введення робочої бази.

## 10.5-r8

r8 додає тільки compatibility-виправлення імпорту XLSX «Шлях» для Windows 7 / Python 3.8: коротка openpyxl-помилка `unexpected keyword argument 'tabId'` без `ChildSheet` тепер коректно розпізнається. Retry працює на in-memory копії й не змінює вихідний XLSX.

Бізнес-логіка r7 не змінювалась.

## Release infrastructure

Повний checkpoint формує:

- modern Windows x64 Setup/Portable;
- Windows 7 SP1 x64 Setup/Portable;
- macOS ARM64 Portable;
- macOS Intel x86_64 Portable;
- START/source;
- per-platform і combined SHA-256.

Windows 7 compatibility line: CPython 3.8.10 x64 + PyInstaller 5.13.2 + `requirements-win7.txt` + `Taxo_win7.spec` + `scripts/check_win7_pe.py`.

## Recovery

1. [START_HERE.md](../../START_HERE.md)
2. [PROJECT_RULES.md](../../PROJECT_RULES.md)
3. [PROJECT_STATE.md](../../PROJECT_STATE.md)
4. [WORKLOG.md](../../WORKLOG.md)
5. Issue #61

Release notes: [10.5-r8](../releases/RELEASE_NOTES_v10_5_r8.md).  
Release index: [RELEASE_INDEX.md](../releases/RELEASE_INDEX.md).
