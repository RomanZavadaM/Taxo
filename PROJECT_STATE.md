# PROJECT_STATE — Taxo

**Confirmed integrated: 17.11.2026.**

- Latest completed code revision **10.21-r8**. Product PR #513 merged, immutable exact source `c9dc9799c22565b56c737216983dd900265c29bd`.
- Exact-source START #44167952855 **1475/1475**; Windows #44167952924, Win7 #44167952849, macOS Intel/ARM #44167952840 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #514 merged `293ddccfcf88433e7a331d79372e4fe1c71239b4`; publisher #44169744409 SUCCESS.
- [v10.21-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r8) — Test prerelease, 6 assets, exact immutable source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), 8 assets, unchanged.

## Result r8

Unsafe positional pairing of independent vehicle and driver selections was removed. A new assignment order now stages concrete pairs explicitly: exactly one vehicle + one or more drivers per action, with the resulting pairs visible before save; another vehicle is added separately. Unstaged selection blocks save instead of silently re-pairing. The existing-order bulk path follows the same rule. Historical stored orders are not rewritten. The 12-pair regression still validates persistence, reopen, DOCX/PDF/JPG and backup/restore.

## Active code revision

None. **10.21-r9 not started.**

## Next action

Continue only the still-open part of **Issue #511**: owner cannot reuse already prepared driver↔vehicle pairs from «Експлуатація» when creating the order. Trace that prepared-pair source through selection/import, stage/store/reopen/generate and add regression coverage without restoring positional pairing. Perform fresh live GitHub reconciliation before modifications; leave stable unchanged.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Development log: WORKLOG.md and Issue #61.
