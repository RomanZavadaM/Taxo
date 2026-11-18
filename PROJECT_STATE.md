# PROJECT_STATE — Taxo

**Confirmed integrated: 18.11.2026.**

- Latest completed code revision **10.22-r2**. Immutable exact product source `0aac6e80025cdcc5b54f2f393dbc256f40e42f2d`.
- Exact-source START #44291976150 **1520/1520**; Windows #44291976175, Win7 #44291976210, macOS Intel/ARM #44291976217 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #526 merged `c51f2016b12187d87ab4567d5649f5a1747bec40`; publisher #44293509376 SUCCESS.
- [v10.22-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r2) — Test Portable prerelease, 6 assets, exact immutable source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), unchanged.

## Result r2

Unified «Документи» catalog now exposes exact employee/vehicle navigation from structured order relations. Ordinary orders use frozen `operations_order_entities` snapshots; assignment orders use stored `vehicle_driver_assignments`. Filtering is keyed by stable Taxo IDs, so equal employee names do not collapse into one logical person. Structured employee/vehicle labels are also visible in the catalog column and searchable text.

The new filters combine with year/month, date range, type, category, source, scans and search before pagination. Legacy rows without a structured relation remain visible without the filter and are never assigned an inferred person or vehicle from free text.

No document files, DocumentVault, scans, DB schema, backup format, security rules, dependencies, business statuses, or driver↔vehicle pair behavior changed.

## Active code revision

None. **10.22-r3 not started.**

## Next action

Fresh live reconciliation, then continue Issue #289 with one narrow independent slice unless owner testing reports a higher-priority defect. Keep Stable unchanged.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Development log: WORKLOG.md and Issue #61.
