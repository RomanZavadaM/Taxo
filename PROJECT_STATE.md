# PROJECT_STATE — Taxo

**Confirmed integrated: 18.11.2026.**

- Latest completed code revision **10.22-r5**. Immutable exact product source `576f93acd7d070a6786cfcd3c28af1d5f29d98c0`; product PR #534 merged.
- Exact-source START #44375223718 **1531/1531**; Windows #44375224479, Win7 #44375223666, macOS Intel/ARM #44375223669 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #535 merged `ef8f63bdf5771d2a365509d5786bbf9ab6a115e8`; publisher #44376388134 SUCCESS.
- [v10.22-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r5) — Test Portable prerelease, 6 assets, exact immutable product source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), unchanged.

## Result r5

The unified «Документи» catalog displays a separate paper-signature state and lets the operator explicitly mark the paper original as signed with a date, or cancel the mark while retaining all historical events. The presence of a scan alone never implies a signed original. Journal: `Data/DocumentVault/paper_original_events.json`, covered by full workspace backup/restore and protected by strict vault validation.

Four focused regression tests added; full suite is **1531/1531**. No SQLite schema, immutable DOCX, attachment contents, business state, digital signatures, driver/vehicle pairing, or Stable changes.

## Active code revision

None. **10.22-r6 not started.**

## Next action

Fresh live reconciliation, then one independent narrow Issue #289 step unless owner testing raises a higher-priority defect. Keep Stable unchanged.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Development log: WORKLOG.md and Issue #61.
