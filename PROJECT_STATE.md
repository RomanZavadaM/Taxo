# PROJECT_STATE — Taxo

**Confirmed integrated: 18.11.2026.**

- Latest completed code revision **10.22-r7**. Immutable exact product source `544da915100744f4fcf1e094f374d13c76c36c80`; product PR #540 merged; final PR head `b7daf5f3b69bddf9240805c7608118145fc6c2e9`.
- Exact-source START #44404136276 **1540/1540**; Windows #44404136133, Win7 #44404136553, macOS Intel/ARM #44404136897 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #541 merged `7494e415a005a3c30c453069fabce7deefe2c457`; publisher #44406105602 SUCCESS.
- [v10.22-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r7) — Test Portable prerelease, 6 assets, exact immutable product source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), unchanged.

## Result r7

The unified «Документи» catalog now sorts by **Категорія** in both directions from the column header. Sorting is applied to the full filtered result before pagination; «Не визначено» stays last in both directions, and reset restores the default date order.

Focused r7 regression coverage plus the full suite passed **1540/1540**. Exact-source Windows, Win7 and macOS builds all passed, including Defender/integrity. A later release-trigger Win7 check had one transient Defender-signature network timeout `0x80072ee2`; rerun passed without code changes. No SQLite schema, DocumentVault, scans, paper-signature state, backup/restore, driver/vehicle pairing or Stable changes.

## Active code revision

None. **10.22-r8 not started.**

## Next action

Fresh live reconciliation, then one independent narrow Issue #289 step unless owner testing raises a higher-priority defect. Keep Stable unchanged.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Development log: WORKLOG.md and Issue #61.
