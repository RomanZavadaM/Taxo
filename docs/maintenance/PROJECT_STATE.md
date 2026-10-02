# Taxo — технічний стан

Цей файл є коротким технічним дзеркалом канонічного [PROJECT_STATE.md](../../PROJECT_STATE.md). Історичні checkpoint-и не дублюються тут: вони збережені в Git history, release notes та Issue #61.

**Дата:** 02.10.2026  
**Stable:** Taxo 10.3 / `v10.3`  
**Previous stable / rollback:** Taxo 10.1 / `v10.1`  
**Latest integrated checkpoint in `main`:** **Taxo 10.9-r10**  
**Structural cleanup PR:** #132  
**Exact r10 source before merge:** `ff56519da35e03204bdaf77f7187cddd692f79d4`  
**Main structural merge:** `5e179eabccc35afa984be04208e2e4d96094a2fb`  
**Documentation closeout:** PR #133 / `fc9827f5a38efb05e1d70e1b83c6fb5782550606`  
**Exact-head Windows:** `37018721703` — success  
**Exact-head Windows 7:** `37018721695` — success  
**Exact-head macOS:** `37018722335` — success  
**Latest full multi-platform published checkpoint:** `10.9-r9 / v10.9-r9`  
**Next code revision:** `10.10-r1`

## Структура після 10.9-r10

- `src/taxo/` — runtime/support Python modules;
- `assets/` — runtime templates та ресурси;
- `packaging/` — active PyInstaller/Inno Setup definitions;
- `packaging/history/` — historical packaging specs;
- у root залишені entry points, project-state/legal файли та мінімальний bootstrap;
- `START.bat`, Windows, Windows 7 і macOS build paths адаптовані до структурованого layout;
- business logic та user-data contracts цією ревізією не змінювалися;
- database/workspace/backup migration не вводилась.

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

## Інтегрована лінія 10.9

- r2 — waybill history / number reuse / retention guards;
- r3 — vehicle-document validity for the whole trip;
- r4 — work/rest compliance hardening;
- r5 — tachograph / 60-day activity safety;
- r6 — personnel balance / P-5 / employment-aware history;
- r7 — STOIR odometer chronology and maintenance forecast;
- r8 — immutable approved/signed orders and assignment safety;
- r9 — explicit SQLite schema compatibility baseline;
- r10 — full repository structural cleanup.

## Release infrastructure

Останній повний user-test release `v10.9-r9` містить:

- modern Windows x64 Setup/Portable;
- Windows 7 SP1 x64 Setup/Portable;
- macOS ARM64 Portable;
- macOS Intel x86_64 Portable;
- START/source;
- SHA-256 manifests.

`10.9-r10` перевірено на Windows, Windows 7 і macOS та інтегровано в `main`, але окремий public tag/release r10 з повним набором пакетів не публікувався.

Windows 7 compatibility line: CPython 3.8.10 x64 + PyInstaller 5.13.2 + `requirements-win7.txt` + current Win7 packaging spec + `scripts/check_win7_pe.py`.

## Recovery

1. [START_HERE.md](../../START_HERE.md)
2. [PROJECT_RULES.md](../../PROJECT_RULES.md)
3. [PROJECT_STATE.md](../../PROJECT_STATE.md)
4. [WORKLOG.md](../../WORKLOG.md)
5. Issue #61

Release notes: [10.9-r10](../releases/RELEASE_NOTES_v10.9-r10.md).  
Release index: [RELEASE_INDEX.md](../releases/RELEASE_INDEX.md).
