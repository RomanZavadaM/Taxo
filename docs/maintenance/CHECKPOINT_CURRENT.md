# Поточна контрольна точка Taxo

**23.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r5.**

## Stable

- Release: [v10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3)
- Exact source: `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`
- 8 canonical assets; GitHub Latest; prerelease=false; draft=false.
- Owner explicit promotion decision: 23.11.2026.
- Stable не змінювати без окремого рішення власника.

## Current Test

- Release: [v10.24-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r5)
- Exact source: `6d697a641b4f546dc533c8f55379696ad827b278`
- 8 canonical assets; prerelease=true; draft=false.
- Prep #625: START #45169334073, Windows #45169334161, Win7 #45169334164, macOS Intel/ARM #45169334069 — SUCCESS.
- Candidate #626: START #45190123472, Windows #45190123183, Win7 #45190124279, macOS #45190123566 — SUCCESS.
- Exact source: START #45191514761, Windows #45191514632, Win7 #45191514666, macOS Intel/ARM #45191514659 — SUCCESS.
- Windows/Win7 Defender + post-scan integrity — SUCCESS.
- Guarded release-trigger #627 merged as `53127f27929b7f1c72c6876ce4a048c9955d02de`; trigger checks START #45192571617, Windows #45192571441, Win7 #45192571278, macOS #45192571563 — SUCCESS.
- Publisher #45193506957 — SUCCESS.

## Що перевірено у r5

- separate `Data/CorrespondenceCases/cases.json` із stable case IDs;
- strict `Data/Correspondence` registry guard не послаблено;
- explicit membership by correspondence ID; no file/scan/attachment copy;
- one letter max one case; atomic move/unfile;
- archive read-only until explicit restore;
- response/related graph is candidate-only until user confirms «Додати пов'язані»;
- backup/restore preserves case store;
- third «Справи» tab, case assignment/browser/open/remove actions;
- 760×520 case-action reachability and START required-module guard.

## Далі

Після recovery r5 визначити наступний bounded correspondence slice окремо зі свіжого плану. Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не починати автоматично.

#553/#556/#562 remain open; draft #543/#395 stay open.
