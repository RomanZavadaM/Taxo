# PROJECT_STATE — Taxo

**Confirmed integrated: 19.11.2026.**

- Latest completed code revision **10.22-r9**. Product PR #547 merged; final PR head `f1f01699f284d57b8db98bcef9473e3780276b0c`; immutable exact product source `d38f6a2609775295dbd4885ebee58c9e587b9c2e`.
- Exact-source START #44517481797; Windows #44517481864; Win7 #44517482057; macOS Intel/ARM #44517481994 — all SUCCESS; Defender/integrity PASS.
- Release-trigger PR #548 merged `5e5633214084535f1d594fc26ceea0e8c155befc`; publisher #44519029232 SUCCESS.
- [v10.22-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r9): Test Portable prerelease, 6 assets, exact immutable product source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), unchanged.

## Result r9

Ready-document catalog now has **«Мої папки»** beside «За видами / За датами». Users can create nested logical folders, rename them and place one ready document in one or several folders without moving or copying document bytes.

Folder structure and memberships are stored separately in `Data/DocumentLibrary/collections.json` with atomic writes and validation. A prepared document keeps its logical folder identity after DocumentVault registration. Full workspace backup/restore covers the folder tree and memberships; regression also covers interrupted-write residue and fail-closed corruption handling.

No DocumentVault bytes, scans, paper-signature state, order data, SQLite schema, driver/vehicle pairs or Stable assignment were changed.

## Owner decisions on following revisions

[Draft PR #543](https://github.com/RomanZavadaM/Taxo/pull/543) remains the broader plan for the ready-document library and future **inbound/outbound correspondence registration**. Correspondence is still planned, not implemented. Unrelated old draft PR #395 remains untouched.

## Active code revision

None. **10.22-r10 not started.**

## Next action

Fresh live reconciliation, then one narrow follow-up to finish user-folder management: move/re-parent a folder and safe archive/removal semantics without touching document bytes. Implement correspondence separately afterward. Keep Stable untouched.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Development log: WORKLOG.md and Issue #61.

