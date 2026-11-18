# PROJECT_STATE — Taxo

**Confirmed integrated: 18.11.2026.**

- Latest completed code revision **10.22-r4**. Immutable exact product source `b01437828551fe309c2dfcba81572a9a9d51e628`.
- Exact-source START #44320801103 **1527/1527**; Windows #44320801102, Win7 #44320801191, macOS Intel/ARM #44320801139 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #532 merged `7d443e25f8ec754f71a3749c6e46163d8aca8728`; publisher #44322860950 SUCCESS.
- [v10.22-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r4) — Test Portable prerelease, 6 assets, exact immutable source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), unchanged.

## Result r4

Unified «Документи» now opens a DocumentVault record through a verified temporary read-only DOCX copy. The immutable vault object is rechecked for index consistency, size and SHA-256 before materialization and is never handed directly to Word or another external application. Tampered vault content is rejected.

Three focused regressions added; full suite is **1527/1527**.

No DB schema, DocumentVault format, scan, backup/restore, business status, e-signature or driver↔vehicle pairing changes.

## Active code revision

None. **10.22-r5 not started.**

## Next action

Fresh live reconciliation, then one independent narrow Issue #289 step unless owner testing raises a higher-priority defect. Keep Stable unchanged.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Development log: WORKLOG.md and Issue #61.
