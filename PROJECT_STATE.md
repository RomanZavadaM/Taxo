# PROJECT_STATE — Taxo

**Підтверджено GitHub 23.11.2026 після promotion v10.24-r3 у Stable/Latest.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, `prerelease=false`, `draft=false`, GitHub Latest.

**Попередня Stable:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`.

Promotion PR #620: START #45146984711, Windows #45146984611, Win7 #45146984624, macOS Intel/ARM #45146984616 — SUCCESS; merged `c739f37e6a4a2ecc6be6c6302548cf8f83b479cc`. Publisher #45147941030 — SUCCESS. Guarded exact historical promotion #45147941048 — SUCCESS.

## Stable 10.24-r3

Stable містить усю лінію 10.23-r4 та correspondence r1–r3:
- r1: two journals, independent annual numbering, semantic dates, metadata/links, backup/restore;
- r2: immutable controlled attachments/live DocumentVault links, SHA256/MIME/size/name, dedupe, history-only remove, integrity + backup/restore;
- r3: separate resizable journal/card UI via strict `correspondence.center`, Incoming/Outgoing, search/date/calendar, sorting, details, create/reply/attachments/open document, unsaved-change guard.
- blank `sent_date` remains registered-only; attachment presence never implies sent/received/delivered/signed.

## Current Test / next revision

Новішого опублікованого Test немає.

10.24-r4 prep PR #619 не merged. Його перший CI виявив UI-regression у minimum viewport 760×520: «Отримано…» не mapped. Цей тест не послаблювати; спочатку виправити layout і повторити START/Windows/Win7/macOS.

План r4: explicit sent/received, deadline/overdue, safe state transitions + append-only history. Без automatic e-mail; cases/threads, OCR/AI APPLY і physical attachment purge — пізніше.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
