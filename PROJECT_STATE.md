# PROJECT_STATE — Taxo

**Confirmed integrated: 18.11.2026.**

- Latest completed code revision **10.22-r6**. Immutable exact product source `28d2b838dae51a8ed009dd4b14fe1a0afa561384`; product PR #537 merged; final PR head `d764e56596dc30a0b4c717a0a6b0a5b56a7f39c9`.
- Exact-source START #44386227495 **1535/1535**; Windows #44386227504, Win7 #44386227480, macOS Intel/ARM #44386227490 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #538 merged `c42d3554797ed3bfc133fd1337ab1288b8facc37`; publisher #44388264823 SUCCESS.
- [v10.22-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r6) — Test Portable prerelease, 6 assets, exact immutable product source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), unchanged.

## Result r6

The unified «Документи» catalog now has a separate **«Сезонні заходи»** category for structured `seasonal_operation` orders. Personnel series still wins; free-text subject/content is never used to guess the category.

Four focused r6 regression checks were added. The first PR START exposed one outdated category fixture; the fixture was corrected without weakening production logic. Final suite is **1535/1535**. No SQLite schema, DocumentVault, scans, paper-signature state, backup/restore, driver/vehicle pairing or Stable changes.

## Active code revision

None. **10.22-r7 not started.**

## Next action

Fresh live reconciliation, then one independent narrow Issue #289 step unless owner testing raises a higher-priority defect. Keep Stable unchanged.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Development log: WORKLOG.md and Issue #61.
