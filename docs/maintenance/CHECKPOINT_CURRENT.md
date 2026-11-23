# Поточна контрольна точка Taxo

**23.11.2026 — Stable/Latest 10.23-r4; Current Test 10.24-r3.**

## Stable

- Release: [v10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4)
- Exact source: `a919ced6bc8665ced70ebb4d897808e4e2618667`
- 8 assets; GitHub Latest; prerelease=false.
- Owner manual acceptance 20.11.2026.
- Stable не змінювати без окремого рішення власника.

## Test

- Release: [v10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3)
- Exact source: `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`
- 8 assets; prerelease; publisher #45141326182 SUCCESS.
- START #45139752722, Windows #45139752725, Win7 #45139752551, macOS Intel/ARM #45139752538 — SUCCESS.
- Windows/Win7 Defender + post-scan integrity — SUCCESS.
- r1 incoming/outgoing registry + numbering; r2 immutable attachments/live vault links + integrity/history; r3 separate correspondence journal/card UI with search/date/calendar/sorting/create/reply/attachments/open document and unsaved guard.
- Blank `sent_date` не означає фактичного відправлення; attachment не означає sent/received/delivered/signed.
- Stable/Latest не змінено.

## Наступний напрям

**10.24-r4:** явні фактичні «надіслано»/«отримано», контроль строків та overdue, safe state transitions і history. Без automatic e-mail. Cases/threads, OCR/AI APPLY та physical attachment purge — пізніше.

#553/#556/#562 не закривати автоматично; draft #543/#395 не чіпати.
