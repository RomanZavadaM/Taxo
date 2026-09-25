# WORKLOG — Taxo

**Оновлено:** 25.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3`  
**Latest full checkpoint:** `v10.3-r9` → `9268f9a94d48388238ac957ee7c32071e887da2b`  
**Active candidate:** `10.3-r10`  
**Branch:** `work/v10.3-r10-windows7-compat`  
**Problem:** Windows 7 x64 loader error `api-ms-win-core-path-l1-1-0.dll`  
**Live ledger:** Issue #61.

## ACTIVE SLICE — 10.3-r10 Windows 7 compatibility

Ціль: окремий Windows 7 SP1 x64 package без зміни modern Windows/macOS line.

- [x] version → 10.3-r10;
- [x] Python 3.8 compatible dependency pins;
- [x] Win7 installer spec + release notes + tests;
- [ ] Python 3.8 compile/regression;
- [ ] build Win7 Portable + Setup;
- [ ] publish `v10.3-r10` prerelease;
- [ ] manual Windows 7 gate before merge to main.

## NEXT

Run exact-head Windows 7 compatibility publisher and fix any Python 3.8 incompatibility reported by CI.

## BLOCKED

Немає.
