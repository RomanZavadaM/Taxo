# Поточна контрольна точка Taxo

**23.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r7.**

## Stable

- Release: [v10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3)
- Exact source: `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`
- 8 canonical assets; GitHub Latest; prerelease=false; draft=false.
- Stable не змінювати без окремого рішення власника.

## Current Test

- Release: [v10.24-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r7)
- Exact source: `4221b8baaeae4fad6ca8b6ebf4640a4a34050e2d`
- 8 canonical assets; prerelease=true; draft=false.
- 58 strict live routes total; correspondence contract remains exact 17 routes.
- Order participant block: 5 live routes — search/select, edit role/note, add vehicle, remove selected, preview sync.
- Prep #630: START #45213479378, Windows #45213479658, Win7 #45213479371, macOS #45213479464 — SUCCESS; Defender/integrity PASS.
- Candidate #634: START #45216365054, Windows #45216364728, Win7 #45216364723, macOS #45216364729 — SUCCESS.
- Exact source: START #45217452473, Windows #45217452461, Win7 #45217452456, macOS #45217452990 — SUCCESS; Defender/integrity PASS.
- Release-trigger #635 merged as `ee7bdbb5e50e3b47e42da46fc7b47eee2991523e`; publisher #45220620129 — SUCCESS.
- GitHub release exact target `4221b8baaeae4fad6ca8b6ebf4640a4a34050e2d`; 8 canonical assets verified.

## Що перевірено у r7

- add/edit/remove учасників і ТЗ синхронізують уже відкритий preview;
- edit role/note має окрему зрозумілу історичну подію;
- preview пояснює окрему друковану сторінку structured participant list;
- DOCX і PDF використовують той самий frozen participant snapshot;
- full backup/restore зберігає entity identity, role, note, snapshot і sequence;
- live preservation guard включає «Змінити роль / примітку…»;
- correspondence r1–r6 та її 17-route contract не змінені.

## Далі

Після завершення recovery звірити #553/#556/#562 і вибрати один bounded control slice для r8. Не змішувати кілька великих механізмів.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не починати автоматично.

Draft #543/#395 stay open.
