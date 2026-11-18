# PROJECT_STATE — Taxo

**Confirmed integrated: 18.11.2026.**

- Latest completed code revision **10.22-r1**. Immutable exact product source `4d108acc1eac69c120244c19d32c89e112f6afcd`.
- Exact-source START #44280221670 **1511/1511**; Windows #44280221497, Win7 #44280221443, macOS Intel/ARM #44280221618 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #523 merged `061ebf398f69591703ee996582a1ce7219b17da6`; publisher #44284701235 SUCCESS.
- [v10.22-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r1) — Test Portable prerelease, 6 assets, exact immutable source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), unchanged.

## Result r1

Unified «Документи» catalog now has quick year/month navigation based only on valid structured document dates. Available years come from real catalog data; months adjust to the selected year, year changes clear an incompatible month, and month-only filtering can span all years. The new selectors combine with search/source/scans/date-range/type/category filters before pagination. Rows with missing/invalid dates remain visible when no calendar filter is active.

No document files, DocumentVault, scans, DB schema, backup format, security rules, dependencies, business statuses, or driver↔vehicle pair behavior changed.

The r9 pair workflow was manually accepted by the owner on 18.11.2026 with no defect found.

## Active code revision

None. **10.22-r2 not started.**

## Next action

Fresh live reconciliation, then one narrow independent catalog slice for employee/vehicle navigation unless owner testing reports a higher-priority defect. Keep Stable unchanged.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Development log: WORKLOG.md and Issue #61.
