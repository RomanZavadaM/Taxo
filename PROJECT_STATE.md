# PROJECT_STATE — Taxo

**Підтверджено GitHub 23.11.2026 після публікації Test 10.24-r3.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`.

**Current Test:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease. Publisher #45141326182 — SUCCESS.

## Stable r4

Stable r4 залишається вручну прийнятою власником версією. 37 strict live UI routes; Stable не змінюється без окремого рішення власника.

## Current Test 10.24-r3

Лінія ділової кореспонденції:
- r1: incoming/outgoing registry, independent annual numbering, semantic dates, correspondent/control metadata, response/related links, stable document_ref, full backup/restore;
- r2: controlled immutable attachments або live DocumentVault link, SHA256/MIME/size/name metadata, content-addressed dedupe, history-only removal, integrity guards і full backup/restore;
- r3: окремий journal/card UI — видимий пункт «Кореспонденція», strict route `correspondence.center`, resizable window, incoming/outgoing tabs, search/date/calendar, sorting, detail card, create/reply/attachments/open-document actions та unsaved-changes guard;
- physical reachability ключових дій перевірена на 760×520; Tk search callback після закриття не лишається;
- attachment не означає sent/received/delivered/signed; вихідний без `sent_date` лишається лише зареєстрованим.

Exact-source CI `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`: START #45139752722, Windows #45139752725, Win7 #45139752551, macOS Intel/ARM #45139752538 — SUCCESS; Windows/Win7 Defender + post-scan integrity PASS. Guarded release-trigger merged як `2ff35228a641de8efc1c63a100815cf9280126cd`; publisher #45141326182 — SUCCESS.

## Наступна ревізія

**10.24-r4:** явні фактичні стани «надіслано»/«отримано», контроль строків та overdue, safe state transitions і append-only історія. Без автоматичного e-mail. Cases/threads, OCR/AI APPLY і physical attachment purge — окремими пізнішими кроками.

AI-ready document import r6–r10 завершений на REVIEW без APPLY. APPLY — лише після окремого рішення власника.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
