# WORKLOG — Taxo

**Оновлено:** 02.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable release:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated code checkpoint:** **10.9-r9**  
**Latest issued fast-test:** **10.9-r9 / `v10.9-r9`**  
**Latest full multi-platform published checkpoint:** **10.9-r9 / `v10.9-r9`**  
**Current development revision:** **10.9-r10**  
**Branch:** `work/v10.9-r10-structure`  
**Base main:** `3fbaa1b39cb1b683d46cc5748129d0417dc94bfc`  
**PR:** #132 — full repository structural cleanup  
**Live ledger:** Issue #61

## DONE — integrated baseline 10.9-r9

The cumulative r2…r9 line is integrated in `main`. The public `v10.9-r9` checkpoint has Windows x64, Windows 7 SP1 x64, macOS ARM64/Intel and START packages. Historical tags/releases remain immutable.

## DOING — 10.9-r10 structural cleanup

Goal: make the repository readable without changing Taxo business logic or user data contracts.

Implemented on the working branch:

- runtime support modules moved from repository root to `src/taxo/`;
- only executable entry points `main.py` and `taxo_app.py` remain at root, plus compatibility bootstrap `sitecustomize.py`;
- historical flat imports remain supported through `src/taxo` path bootstrap;
- DOCX/PDF runtime templates moved to `assets/`;
- active PyInstaller specs moved to `packaging/`;
- historical packaging specs moved out of root to `packaging/history/`;
- Inno Setup definitions moved to `packaging/installer/`;
- `START.bat` updated for the structured layout;
- `VERSION.txt` and `main.APP_VERSION` raised to **10.9-r10**;
- packaging definitions updated for `assets/` and `src/taxo/`;
- Windows, Windows 7, macOS ARM64/Intel and START workflows are configured to verify the same r10 structure;
- structured compile checks no longer depend on shell wildcard expansion and enumerate `src/taxo/*.py` explicitly through Python/PowerShell.

No database, workspace, backup, scan or user-document migration is introduced by this revision.

## VERIFY BEFORE DONE

This WORKLOG commit is the synchronization point used to trigger all platform checks on one exact PR head after the structured-compilation CI fixes.

1. exact-head Windows gate must pass;
2. full regression suite must pass with the new source path;
3. START complete/incomplete preflight must pass;
4. Windows portable and installer must build and contain `assets/` templates;
5. START test archive must be generated from the new tree;
6. Windows 7 portable must pass the PE compatibility check;
7. macOS ARM64 and Intel application bundles must build and verify;
8. documentation and Issue #61 must record the final exact SHA and test artifacts.

## NEXT

Fix any path-dependent regression reported by this synchronized exact-head CI. When all gates are green, publish the 10.9-r10 test artifacts and present PR #132 as ready for owner testing. Do not promote to stable automatically.
