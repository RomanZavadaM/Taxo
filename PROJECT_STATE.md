# PROJECT_STATE — Taxo

**Confirmed integrated: 17.11.2026.**

- Latest completed code revision **10.21-r9**. Product PR #516 merged, immutable exact source `77b80c77f9fd084208d32847c62a5d16c4640262`.
- Exact-source START #44180404692 **1491/1491**; Windows #44180404613, Win7 #44180404568, macOS Intel/ARM #44180404629 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #517 merged `95d3405c25c7ad7bcc5aa6a2e29991bd74753a8a`; publisher #44181523720 SUCCESS.
- [v10.21-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r9) — Test Portable prerelease, 6 assets, exact immutable source above.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), 8 assets, unchanged.

## Result r9

Owner reported broken, unclear driver–vehicle pair editing in r8 and a confusing switch from a saved/edited order to the general pair tab. r9 removes both automatic redirects. Existing order edits, additions and deletions now target the concrete pair inside the order, with immediate refresh; save of the separate pair dialog is explicit and committed immediately, independent of unsaved order text. New order staging supports replacing a pair and importing exact prior non-cancelled associations from «Експлуатація» with search and deduplication. No schema, bulk rewriting of historical orders, document format, backup format, security or dependency changes.

## Active code revision

None. **10.21-r10 not started.**

## Next action

Collect owner manual UI acceptance for **Issue #511** on v10.21-r9. Run a fresh live GitHub reconciliation before any new changes; if acceptance finds defects, address only one scoped failure and keep stable unchanged.

## History

Taxo 10.3 / `v10.3` exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Development log: WORKLOG.md and Issue #61.
