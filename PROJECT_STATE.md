# PROJECT_STATE — Taxo

**Confirmed integrated: 18.11.2026.**

- Latest completed code revision **10.21-r10**. Immutable exact product source `3c6a4aedaf18399f3688d02bba3eb0cd30dd74ad`.
- Exact-source START #44270332491 **1501/1501**; Windows #44270332484, Win7 #44270332389, macOS Intel/ARM #44270332442 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #520 merged `f78e213b496117c400599568ff4133fd1f9b616c`; publisher #44271925495 SUCCESS.
- [v10.21-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r10) — Test Portable prerelease, 6 assets, exact immutable source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), unchanged.

## Result r10

Unified «Документи» catalog now exposes a structured category column/filter. Order categories are derived only from `order_series` and `order_type`: personnel, operational, occupational safety, road safety, fire safety. Legacy Word/DocumentVault rows without structured direction remain visible as «Не визначено» rather than being guessed from free text. Category filtering combines with existing search/source/scans/date/type filters before pagination. No file, vault, scan, DB-schema, backup-format, security or dependency changes.

Driver↔vehicle pair UI from r9 was not changed in r10 and still awaits owner manual acceptance.

## Active code revision

None. **10.22-r1 not started.**

## Next action

Fresh live reconciliation, then choose one narrow independent catalog slice (year/month or employee/vehicle navigation), unless owner manual testing reports a pair defect first. Keep Stable unchanged.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Development log: WORKLOG.md and Issue #61.
