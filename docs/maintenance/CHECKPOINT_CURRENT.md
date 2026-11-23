# Поточна контрольна точка Taxo

**23.11.2026 — Stable/Latest 10.24-r3. Новішого published Test немає.**

## Stable

- Release: [v10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3)
- Exact source: `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`
- 8 canonical assets; GitHub Latest; prerelease=false; draft=false.
- Owner explicit promotion decision: 23.11.2026.
- Promotion PR #620: START #45146984711, Windows #45146984611, Win7 #45146984624, macOS #45146984616 — SUCCESS.
- Promotion merge: `c739f37e6a4a2ecc6be6c6302548cf8f83b479cc`.
- Publisher #45147941030 — SUCCESS.
- Guarded exact stable verification/reassembly #45147941048 — SUCCESS.
- Previous Stable: v10.23-r4.

## Stable functionality added in 10.24

- r1 correspondence registry + safe numbering.
- r2 controlled immutable attachments/live vault links + integrity/history.
- r3 separate correspondence journal/card UI with search/date/calendar/sorting/create/reply/attachments/open document and unsaved guard.
- Blank `sent_date` does not imply actual sent; attachment does not imply sent/received/delivered/signed.

## Next development

10.24-r4 prep PR #619 is not merged. First CI caught a 760×520 reachability regression: «Отримано…» was not mapped. Fix layout; do not weaken the test; rerun all platforms.

r4 scope remains explicit sent/received + deadlines/overdue + safe state transitions/history. No automatic e-mail. Cases/threads, OCR/AI APPLY and physical attachment purge later.

#553/#556/#562 remain open; draft #543/#395 stay open.
