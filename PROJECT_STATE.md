# PROJECT_STATE — Taxo

**Confirmed integrated: 19.11.2026.**

- Latest completed and issued code revision: **10.22-r10**.
- Folder-management PR #550 merged; PDF-appendix fix PR #551 merged. Exact immutable product source: `56917daed4756dc4725cc58c43fcb900ce256f2c`.
- Exact-source CI: START #44535065602, Windows #44535065617, Windows 7 #44535065603, macOS Intel/ARM #44535065691 — all SUCCESS; Windows/Win7 Defender/integrity PASS.
- Release trigger PR #554 merged `bb01b7537e3309b2c45841731b361b789b1dc01c`. Publisher #44536931544 SUCCESS.
- [v10.22-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r10): Test Portable prerelease, 6 files, exact source above. Stable/Latest [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2) unchanged.

## Confirmed r10 changes

«Документи» → «Мої папки»: full-catalog picker can add to an empty folder; folder selection persists. Folder re-parenting, reversible archive/restore and backup of the folder tree and document associations do not move/copy/delete original documents. For order PDF appendices, long role, employee/vehicle and identifier text now wraps inside table columns, without modifying order snapshots.

## Known owner-reported defect

[Issue #553](https://github.com/RomanZavadaM/Taxo/issues/553) — «Експлуатація → Учасники / ТЗ» workflow remains confusing/not working as expected. A PDF overlap defect shown in the same screenshots was fixed in r10, but **the full participant-management workflow has not passed owner manual acceptance**. Keep the issue open until end-to-end testing and manual confirmation.

## Next

**Next code revision: 10.23-r1**. Fresh GitHub reconciliation; reproduce and repair one narrow failure from Issue #553, with regression tests. Incoming/outgoing correspondence remains planned under draft PR #543 and must be implemented separately. PR #395 remains untouched. Stable unchanged.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Earlier checkpoints and detailed logs: WORKLOG.md, Issue #61 and the private profile `RomanZavadaM/dev-strategy` branch `profile/taxo`.
