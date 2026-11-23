# HANDOFF_CURRENT — Taxo

**23.11.2026 — v10.24-r3 переведено у Stable/Latest за прямим рішенням власника.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 canonical assets, `prerelease=false`, GitHub Latest.

**Попередня Stable:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`.

Promotion PR #620 пройшов START #45146984711, Windows #45146984611, Win7 #45146984624, macOS Intel/ARM #45146984616 — SUCCESS і merged як `c739f37e6a4a2ecc6be6c6302548cf8f83b479cc`. Publisher #45147941030 — SUCCESS. Окремий guarded historical-stable flow #45147941048 — SUCCESS: exact source/тег/8 assets/Latest перевірені повторно.

## Що входить у Stable 10.24-r3

- Увесь прийнятий функціонал 10.23-r4: документи, скани, паперовий підпис, логічні папки, регульовані робочі області, накази/пари/учасники, адаптивний preview.
- 10.24-r1: incoming/outgoing correspondence registry, незалежна річна нумерація, semantic dates, correspondent/subject/control metadata, response/related links, document_ref, backup/restore.
- 10.24-r2: controlled immutable correspondence attachments або live DocumentVault links, SHA256/MIME/size/name, content-addressed dedupe, history-only remove, integrity guards, backup/restore.
- 10.24-r3: окремий `correspondence_ui.py`, видимий пункт «Кореспонденція», strict route `correspondence.center`, resizable «Вхідні»/«Вихідні», пошук, дата/календар, сортування, картка листа, «Новий вхідний/вихідний», «Відповісти», «Вкладення…», «Відкрити документ», unsaved-change guard і 760×520 reachability.
- Порожній `sent_date` не означає фактичного відправлення; attachment не означає sent/received/delivered/signed.

## Поточна розробка

Окремого новішого опублікованого Test після promotion r3 немає.

**10.24-r4** лишається наступною ревізією. Prep PR #619 не merged: перший CI зупинився на одному реальному UI-регресі — кнопка «Отримано…» не була mapped у мінімальному 760×520 вікні. Перш ніж продовжувати r4, виправити компоновку/досяжність і повторити повний CI. Не послаблювати тест.

Межа r4 лишається: explicit actual sent/received, deadline/overdue, safe state transitions/history. Без automatic e-mail; cases/threads, OCR/AI APPLY і physical attachment purge — пізніше.

AI-ready import r6–r10 завершений на REVIEW без APPLY. APPLY не починати без окремого рішення власника.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.
