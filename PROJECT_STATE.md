# PROJECT_STATE — Taxo

**Confirmed integrated: 17.11.2026.**

- Latest completed code revision **10.21-r7**. Product PR #509 merged, immutable exact source `b3185f5f558d96880cc8c2614529d0fb2d0de660`.
- Exact-source START #44159339508 **1469/1469**; Windows #44159339500, Win7 #44159340068, macOS Intel/ARM #44159339556 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #510 merged `4f9eafa9729f15b25dd1bf26385e87e3fe1aa520`; publisher #44161402744 SUCCESS.
- [v10.21-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r7) — Test prerelease, 6 assets, exact immutable source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), 8 assets, unchanged.

## Result r7

Existing schedule calendar «Дата…» reused in the «Шляхівки» window. Selecting a new day immediately refreshes this window, cancelling does not; the r6 manual date/day navigation is preserved. No DB/schema, mileage/waybill business logic, backup/restore, security, dependency changes. Manual UI acceptance of r7 not yet recorded.

## Active code revision

None. **10.21-r8 not started.**

## Next action

Address owner-reported **Issue #511**: wrong pair grouping of chosen drivers/vehicles in order UI **and inability to import prepared pairs from «Експлуатація»**. Validate exact driver↔vehicle associations in select/stage/store/reopen/generate paths and add regressions; no silent positional re-pairing or automatic alteration of older orders. Perform fresh live GitHub reconciliation before modifications; leave stable unchanged.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Development log: WORKLOG.md and Issue #61.
