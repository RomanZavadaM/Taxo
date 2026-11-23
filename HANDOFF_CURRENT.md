# HANDOFF_CURRENT — Taxo

**23.11.2026 — 10.24-r3 опубліковано як Test prerelease; Stable/Latest лишається 10.23-r4.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`, GitHub Latest.

**Current Test:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease. Publisher #45141326182 — SUCCESS.

Exact-source r3 CI: START #45139752722, Windows #45139752725, Win7 #45139752551, macOS Intel/ARM #45139752538 — SUCCESS. Windows і Win7 Defender та post-scan integrity — SUCCESS. Guarded release-trigger merged як `2ff35228a641de8efc1c63a100815cf9280126cd`.

## Що вже є в модулі кореспонденції

**10.24-r1:** два незалежні журнали incoming/outgoing, річна нумерація, stable `cr-...` ID, окремі semantic dates, correspondent/subject/summary/delivery/responsible/due/status, response/related links, stable document_ref і full backup/restore.

**10.24-r2:** окремий `Data/CorrespondenceAttachments`; immutable PDF/JPG/PNG/TIFF/DOCX з stable `ca-...`, SHA256/MIME/size/original filename; content-addressed dedupe; live `vault:vd-...` link на DocumentVault; integrity/history guards; remove без фізичного видалення байтів; full backup/restore. Attachment не змінює sent/received/status.

**10.24-r3:** видимий модуль «Кореспонденція» через окремий feature-layer і strict route `correspondence.center`; resizable вікно з вкладками «Вхідні»/«Вихідні», пошуком, датою/календарем, «Сьогодні»/«Усі дати», sortable таблицями та карткою листа. Є «Новий вхідний», «Новий вихідний», «Відповісти», «Вкладення…», «Відкрити документ», захист незбережених змін і перевірена досяжність на 760×520. Порожній `sent_date` не робить вихідний лист автоматично надісланим; attachment UI використовує r2 integrity/history API.

## Наступний крок

**10.24-r4 — явні бізнес-стани кореспонденції:**
- фактичне «Надіслано» для вихідного окремо від реєстрації;
- фактичне «Отримано» для вхідного;
- контроль строків і overdue;
- безпечні дозволені переходи станів та історія змін;
- backup/restore regression.

Без автоматичного e-mail. Справи/ланцюжки, OCR, зовнішній AI, AI APPLY і фізичне видалення attachment bytes — пізніше окремими ревізіями.

AI-ready import r6–r10 завершений на REVIEW без APPLY. APPLY не починати без окремого рішення власника.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.
