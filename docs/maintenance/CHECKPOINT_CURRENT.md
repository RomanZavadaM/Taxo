# Поточна контрольна точка Taxo

**27.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r9.**

## Stable

- Release: [v10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3)
- Exact source: `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`
- 8 canonical assets; GitHub Latest; prerelease=false; draft=false.
- Stable не змінювати без окремого рішення власника.

## Current Test

- Release: [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9)
- Exact source: `e3770aa72b0744eee192979a2e569651bac4f257`
- 8 canonical assets; prerelease=true; draft=false.
- 58 strict live routes total; correspondence contract remains exact 17 routes.
- r8 is control-only: fresh reopen + same-order refresh/status transition preservation for «Учасники / ТЗ».
- Prep #638: START #45231841871, Windows #45231841838, Win7 #45231842010, macOS #45231841929 — SUCCESS; Defender/integrity PASS.
- Candidate #639: START #45234694758, Windows #45234694250, Win7 #45234694546, macOS #45234694225 — SUCCESS; Defender/integrity PASS.
- Exact source: START #45235704945, Windows #45235704686, Win7 #45235704998, macOS #45235705102 — SUCCESS; Defender/integrity PASS.
- Release-trigger #640 merged as `411c1e496ccddcd4ed0f9fd754743dfdf9ef8986`; publisher #46004721962 — SUCCESS.
- GitHub release exact target `d24b1bc96115de52d6088813992aca3b410fe243`; 8 canonical assets verified.

## Що перевірено у r8

- повне закриття й створення нової UI-поверхні повторно читає той самий наказ із SQLite;
- номер, дата, тема і стан наказу не губляться;
- роль/примітка та рядок учасника зберігаються;
- «Чернетка» → «Діє в Taxo» не змінює participant snapshot/sequence;
- same-order refresh зберігає selection;
- r7 add/edit/remove, preview, DOCX/PDF і backup/restore control лишається активним;
- correspondence r1–r6 та її 17-route contract не змінені.

## Далі

Recovery r8 закритий: public docs, private profile, Issue #61 і Drive синхронізовані. Наступна дія: звірити ручне приймання #553/#556/#562; якщо нових дефектів немає — вибрати один bounded control slice для r9.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не починати автоматично.

Draft #543/#395 stay open.
