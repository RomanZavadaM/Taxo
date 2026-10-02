# WORKLOG — Taxo

**Оновлено:** 02.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable release:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated code checkpoint:** **10.9-r9**  
**Latest issued fast-test:** **10.9-r9 / `v10.9-r9`**  
**Latest full multi-platform published checkpoint:** **10.9-r1 / `v10.9-r1`**  
**Main integration:** PR #128 → merge `3f59544b8737cd4715d84f786e32378d87d1dd99`  
**Exact r9 source/tag:** `a368bf3bdfd4a16cc099844b830379c5e2646c2d`  
**START:** `Taxo_v10_9_candidate_r9_START.zip` · SHA-256 `9c30bf70e8c7adc4f2560a22e2bdfa2c26d698573982de01aafa4b34bbcd62d4`  
**Exact-head Windows:** `36919102579` — success  
**Exact-head macOS:** `36919102540` — success  
**Open stacked PRs r2…r8:** none; #121–#127 closed as historical/superseded  
**Next code revision:** **10.9-r10**  
**Live ledger:** Issue #61

## DONE — cumulative integration 10.9-r2 → 10.9-r9

За прямою командою власника PR #128 ретаргетовано на `main`, переведено з draft у ready та успішно злито.

У `main` інтегровано:

- r2 — waybill history / number reuse / retention guards;
- r3 — vehicle-document validity for the whole trip;
- r4 — work/rest compliance hardening;
- r5 — tachograph / 60-day activity safety;
- r6 — personnel balance / P-5 safety;
- r7 — STOIR odometer chronology and maintenance forecast;
- r8 — immutable approved/signed orders and assignment safety;
- r9 — explicit SQLite schema compatibility baseline.

Exact r9 candidate/source `a368bf3bdfd4a16cc099844b830379c5e2646c2d` already had successful Windows and macOS gates before cumulative merge. Historical tags/releases remain immutable.

## DONE — repository cleanup

- PR #128 is the single cumulative integration point for the whole r2…r9 line.
- PR #121–#127 closed and marked historical/superseded.
- Historical work/candidate refs are not valid code bases for new development.
- `main` is the only code base for the next slice.
- Old tags/releases are preserved for reproducibility and audit history; they are not treated as competing current releases.

## DOING

No active code slice. 10.9-r9 is integrated and frozen as the latest code checkpoint.

## NEXT

The next code change is **10.9-r10**, created only from current `main`.

Continue the modular architecture in small complete slices and keep `domain → service → repository/data access → infrastructure → UI` boundaries. Do not reopen or merge historical stacked PRs.
