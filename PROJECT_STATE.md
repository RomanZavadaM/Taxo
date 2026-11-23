# PROJECT_STATE — Taxo

**Підтверджено GitHub 23.11.2026 після публікації Test v10.24-r6.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, draft=false, GitHub Latest.

**Current Test:** [10.24-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r6), exact source `d713dd2b085216d8ec764fb16a3ab057f01f07ec`, 8 assets, prerelease=true, draft=false. Publisher #45209524416 — SUCCESS.

## Test 10.24-r6

- control-only revision; no new correspondence business data model;
- 55 strict live routes total, 17 correspondence routes;
- all correspondence routes use runtime-smoke mapping and live Tk activation;
- mapped + onscreen + usable + activation are required;
- protected surfaces cover registry/card actions, actual sent/received, state/history, attachments/open document and case/thread actions;
- r1–r5 storage semantics, numbering, state history, cases and backup/restore remain unchanged.

Prep #629: START #45204102723, Windows #45204102869, Win7 #45204102379, macOS #45204102369 — SUCCESS; Defender/integrity PASS.

Candidate #631: START #45206383953, Windows #45206384077, Win7 #45206384595, macOS #45206384273 — SUCCESS.

Exact issued source `d713dd2b085216d8ec764fb16a3ab057f01f07ec`: START #45207404713, Windows #45207404491, Win7 #45207404242, macOS #45207404447 — SUCCESS; Defender/integrity PASS.

Release trigger #632 merged `4dec0786d2dfc50e718f52901f8a012bf08d58e8`; trigger START #45208494055, Windows #45208494039, Win7 #45208494062, macOS #45208494429 — SUCCESS; publisher #45209524416 — SUCCESS.

## Open boundaries / next package

Stable remains 10.24-r3.

PR #630 is separate from r6. It adds end-to-end live control for order participants and currently sits on the pre-r6 base. After r6 recovery it must be reconciled onto current main and re-tested before it can become the next revision.

Automatic e-mail/mailbox sync/external integrations remain out of scope. OCR/AI APPLY and physical attachment purge remain separately blocked.

#553/#556/#562 remain open; draft #543/#395 stay open.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
