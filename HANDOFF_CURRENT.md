# HANDOFF_CURRENT — Taxo

**Confirmed live GitHub state — 19.11.2026.**

- **10.22-r10 finished, integrated and published.** Folder-management PR #550 merged at `4cfb2637683a6a2d74374919f6255ec957526411`. Additional reported PDF-layout defect fixed by PR #551, merged into immutable **exact product source `56917daed4756dc4725cc58c43fcb900ce256f2c`**.
- Exact-source CI: START #44535065602, Windows #44535065617, Windows 7 #44535065603 and macOS Intel/ARM #44535065691 — **SUCCESS**. Windows/Win7 Defender and integrity gates PASS.
- Superseded release PR #552 was closed without merge because it targeted pre-PDF-fix code. Reconciled release-trigger PR #554 merged at `bb01b7537e3309b2c45841731b361b789b1dc01c`; publisher #44536931544 SUCCESS.
- [v10.22-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r10) — immutable Test Portable prerelease, **6 assets** (Windows, Windows 7, macOS x86_64/arm64, START and SHA256), tag points to `56917daed4756dc4725cc58c43fcb900ce256f2c`.
- **Stable/Latest:** [10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), unchanged.

## User-facing changes

In «Документи» → «Мої папки»: selecting an empty folder no longer blocks adding a document — «Додати документ у цю папку…» offers the full document catalog with search. Newly created/updated folder stays selected. Folders may be moved between parents, archived with descendants and restored; logical document memberships and original files/scans stay intact, including after backup/restore.

**Additional PDF fix:** The structured employee/vehicle appendix of orders now wraps long names, roles and VIN values within table cells instead of painting over adjacent columns. Independent layout render and regression checks were performed; user manual acceptance is pending.

## Owner feedback and next work

- Owner's screenshots from Taxo 10.22-r9 show an **unclear / apparently non-working «Експлуатація → Учасники / ТЗ» order workflow**. This is NOT a library-folder complaint and is NOT fully resolved by PDF text wrapping. Tracked in [Issue #553](https://github.com/RomanZavadaM/Taxo/issues/553); check end-to-end order selection → add/edit participants and vehicles → save → preview/print PDF/DOCX; retain historical snapshots. Do not close #553 without owner's manual acceptance.
- [PR #543](https://github.com/RomanZavadaM/Taxo/pull/543): draft design for the separate ready-document library and later incoming/outgoing correspondence ledger (registration numbers, correspondents, replies, deadlines, attachments). Correspondence not yet implemented.
- PR #395 remains independent architecture-only draft; do not overwrite.
- **Next code revision is 10.23-r1** (r10 was issued; never reuse it). One narrow safe step: investigate and reproduce the «Учасники / ТЗ» workflow in Issue #553 before further new features.

## Recovery

Start with `START_HERE.md`, verify live GitHub against this HANDOFF and `PROJECT_STATE.md`, including open PRs and branches without PR. Do not repeat r10 work or change Stable without owner approval.
