# PROJECT_STATE — Taxo

**Confirmed integrated: 19.11.2026.**

- Latest completed code revision **10.22-r8**. Product PR #544 merged; final PR head `054061fb85bf85e975f976ce82ab3ddc5a00472c`; immutable exact product source `c3274b85d8e5f9fd7de0cb9172da63b2d392daa8`.
- Exact-source START #44506037689; Windows #44506037500; Win7 #44506037901; macOS Intel/ARM #44506037619 — all SUCCESS; Defender/integrity PASS.
- Release-trigger PR #545 merged `525083510f5ea43a4abd447f979ae3304071b96e`; publisher #44507263991 SUCCESS.
- [v10.22-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r8): Test Portable prerelease, 6 assets, exact immutable product source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), unchanged.

## Result r8

Ready-document catalog tree **«За видами / За датами»** with groups by kind or year/month, **«Без дати»**, **«Усі документи»** and whole-snapshot counts. Folder selection combines with existing catalog filters/search and is evaluated before pagination. No physical folder migration, file copies, DocumentVault/scan/signature/backup changes, database schema changes or Stable changes.

## Owner decisions on following revisions

[Draft PR #543](https://github.com/RomanZavadaM/Taxo/pull/543) plans custom editable document collections, reliable storage/backup/restore, and **inbound/outbound correspondence registration** with distinct number series, correspondent metadata, replies, workflows, attachments and history. These features are **planned, not implemented**. Unrelated old draft PR #395 remains untouched.

## Active code revision

None. **10.22-r9 not started.**

## Next action

Fresh live reconciliation, then one narrow step to design and implement **user-managed logical folders** safely; first verify existing backup/restore boundary. Implement correspondence separately afterward. Keep Stable untouched.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Development log: WORKLOG.md and Issue #61.
