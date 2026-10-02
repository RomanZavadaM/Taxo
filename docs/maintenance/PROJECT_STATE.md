# Taxo — технічний стан

Цей файл є коротким технічним дзеркалом канонічного [PROJECT_STATE.md](../../PROJECT_STATE.md). Історичні checkpoint-и не дублюються тут: вони збережені в Git history, release notes та Issue #61.

**Дата:** 02.10.2026  
**Stable:** Taxo 10.3 / `v10.3`  
**Previous stable / rollback:** Taxo 10.1 / `v10.1`  
**Latest integrated checkpoint in `main`:** Taxo 10.9-r9 / `v10.9-r9`  
**Issued source:** `a368bf3bdfd4a16cc099844b830379c5e2646c2d`  
**Main code merge:** `3f59544b8737cd4715d84f786e32378d87d1dd99` via PR #128  
**Documentation closeout:** `34a56e05133bedfc81e6273ea572f6e9757ddab7` via PR #129  
**Exact-head Windows:** `36919102579` — success  
**Exact-head macOS:** `36919102540` — success  
**Next code revision:** `10.9-r10`

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
- Видана шляхівка та використаний номер мають незворотну історію.
- Approved/signed orders та історичні закріплення не переписуються тихо.
- Від r9 future SQLite schema блокується, якщо її версія вища за підтримувану збіркою.

## 10.9-r2 → 10.9-r9

- r2 — waybill history / number reuse / retention guards;
- r3 — vehicle-document validity for the whole trip;
- r4 — work/rest compliance hardening;
- r5 — tachograph / 60-day activity safety;
- r6 — personnel balance / P-5 / employment-aware history;
- r7 — STOIR odometer chronology and maintenance forecast;
- r8 — immutable approved/signed orders and assignment safety;
- r9 — explicit SQLite schema compatibility baseline.

## Release infrastructure

Поточний user-test checkpoint `v10.9-r9` містить:

- modern Windows x64 Setup/Portable;
- Windows 7 SP1 x64 Setup/Portable;
- macOS ARM64 Portable;
- macOS Intel x86_64 Portable;
- START/source;
- SHA-256 manifests.

Windows 7 compatibility line: CPython 3.8.10 x64 + PyInstaller 5.13.2 + `requirements-win7.txt` + `Taxo_win7.spec` + `scripts/check_win7_pe.py`.

## Recovery

1. [START_HERE.md](../../START_HERE.md)
2. [PROJECT_RULES.md](../../PROJECT_RULES.md)
3. [PROJECT_STATE.md](../../PROJECT_STATE.md)
4. [WORKLOG.md](../../WORKLOG.md)
5. Issue #61

Release notes: [10.9-r9](../releases/RELEASE_NOTES_v10.9-r9.md).  
Release index: [RELEASE_INDEX.md](../releases/RELEASE_INDEX.md).
