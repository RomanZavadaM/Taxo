# Поточна контрольна точка Taxo

**23.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r6.**

## Stable

- Release: [v10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3)
- Exact source: `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`
- 8 canonical assets; GitHub Latest; prerelease=false; draft=false.
- Stable не змінювати без окремого рішення власника.

## Current Test

- Release: [v10.24-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r6)
- Exact source: `d713dd2b085216d8ec764fb16a3ab057f01f07ec`
- 8 canonical assets; prerelease=true; draft=false.
- 55 strict live routes total; 17 correspondence routes.
- Prep #629: START #45204102723, Windows #45204102869, Win7 #45204102379, macOS #45204102369 — SUCCESS.
- Candidate #631: START #45206383953, Windows #45206384077, Win7 #45206384595, macOS #45206384273 — SUCCESS.
- Exact source: START #45207404713, Windows #45207404491, Win7 #45207404242, macOS #45207404447 — SUCCESS.
- Release-trigger #632: START #45208494055, Windows #45208494039, Win7 #45208494062, macOS #45208494429 — SUCCESS.
- Windows/Win7 Defender + post-scan integrity — SUCCESS.
- Publisher #45209524416 — SUCCESS.

## Що перевірено у r6

- correspondence center і 16 критичних дій поверх нього мають strict runtime route contracts;
- кожна дія має live Tk reachability/activation test;
- mapped + onscreen + usable + activation є обов'язковими;
- r1–r5 data model, numbering, attachments, states, cases і backup/restore не змінені.

## Далі

PR #630 — окремий пакет end-to-end order participant control. Він зелений на старій pre-r6 базі, але перед наступною ревізією має бути перебазований на актуальний main і повністю перевірений повторно.

Automatic e-mail, mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не змішувати автоматично.

#553/#556/#562 remain open; draft #543/#395 stay open.
