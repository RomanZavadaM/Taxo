# WORKLOG — Taxo

**Оновлено:** 02.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable release:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated code checkpoint:** **10.9-r10**  
**Latest full multi-platform published checkpoint:** **10.9-r9 / `v10.9-r9`**  
**Current main merge:** `5e179eabccc35afa984be04208e2e4d96094a2fb`  
**Next code revision:** **10.10-r1**  
**Live ledger:** Issue #61

## DONE — 10.9-r10 structural cleanup

PR #132 merged the repository structural refactor into `main`.

Completed:
- support/runtime modules moved to `src/taxo/`;
- runtime templates moved to `assets/`;
- PyInstaller/Inno Setup definitions moved to `packaging/`;
- historical specs moved to `packaging/history/`;
- root reduced to entry points, project state/legal files and minimal bootstrap files;
- START/Windows/Windows 7/macOS paths adapted to the structured tree;
- no working-database or user-data migration introduced;
- `VERSION.txt` and `main.APP_VERSION` identify **10.9-r10**.

Exact PR head: `ff56519da35e03204bdaf77f7187cddd692f79d4`.

Verified on that head:
- Windows run `37018721703` — **success**;
- Windows 7 run `37018721695` — **success**;
- macOS run `37018722335` — **success**.

Merged through PR #132 to main commit `5e179eabccc35afa984be04208e2e4d96094a2fb`.

## RELEASE STATE

- Stable remains `v10.3` until a separate owner decision.
- Latest already published full multi-platform release remains `v10.9-r9`.
- `10.9-r10` is the latest integrated code checkpoint in `main` and closes the 10.9 revision cycle.
- Historical tags/releases are immutable and are not reused.

## NEXT

Start the next code slice only from the current `main` as **Taxo 10.10-r1**. Do not create `11.x` without an explicit owner decision.
