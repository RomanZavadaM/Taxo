# PROJECT_STATE — Taxo

**Підтверджено GitHub 23.11.2026 після публікації Test v10.24-r5.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, draft=false, GitHub Latest.

**Current Test:** [10.24-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r5), exact source `6d697a641b4f546dc533c8f55379696ad827b278`, 8 assets, prerelease=true, draft=false. Publisher #45193506957 — SUCCESS.

## Test 10.24-r5

- logical correspondence cases/topics with stable `cc-...` IDs;
- separate `Data/CorrespondenceCases/cases.json`; strict r1 registry store remains unchanged;
- explicit membership by correspondence IDs only: no copy/renumber of documents, scans or attachments;
- one correspondence record belongs to at most one case in this bounded slice;
- atomic move/unfile operations and fail-closed validation;
- archived case is read-only until restored;
- explicit response/related graph provides thread candidates; membership is changed only after user confirmation;
- third UI tab «Справи», assignment from the letter card, case/thread browser, open/remove actions;
- full backup/restore preserves cases and membership;
- 760×520 reachability and START module-presence guard are covered by regression.

Prep #625: START #45169334073, Windows #45169334161, Win7 #45169334164, macOS #45169334069 — SUCCESS; Defender/integrity PASS.

Candidate #626: START #45190123472, Windows #45190123183, Win7 #45190124279, macOS #45190123566 — SUCCESS; Defender/integrity PASS.

Exact source `6d697a641b4f546dc533c8f55379696ad827b278`: START #45191514761, Windows #45191514632, Win7 #45191514666, macOS #45191514659 — SUCCESS; Windows/Win7 Defender + integrity PASS.

Release trigger #627 merged `53127f27929b7f1c72c6876ce4a048c9955d02de`; publisher #45193506957 — SUCCESS.

## Open boundaries

Stable remains 10.24-r3. r5 does not add automatic e-mail/mailbox sync/external integrations.

OCR/AI APPLY and physical attachment purge remain separately blocked. After recovery r5 choose the next bounded correspondence slice from the fresh plan instead of assuming an external integration.

#553/#556/#562 remain open; draft #543/#395 stay open.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
