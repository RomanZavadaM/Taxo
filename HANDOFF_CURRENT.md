# HANDOFF_CURRENT — Taxo

**22.11.2026 — 10.24-r2 опубліковано як Test prerelease; Stable/Latest лишається 10.23-r4.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`, GitHub Latest.

**Current Test:** [10.24-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r2), exact source `d07f26d8e9e9db6d33278cac5a0199e2d8ae4b50`, 8 assets, prerelease. Publisher #45064537526 — SUCCESS.

Exact-source r2 CI: START #45063475205, Windows #45063475214, Win7 #45063475185, macOS Intel/ARM #45063475161 — SUCCESS. Windows і Win7 Defender та post-scan integrity — SUCCESS.

## Що вже є в модулі кореспонденції

**10.24-r1:** два незалежні журнали incoming/outgoing, річна нумерація, stable `cr-...` ID, окремі semantic dates, correspondent/subject/summary/delivery/responsible/due/status, response/related links, stable document_ref і full backup/restore.

**10.24-r2:** окремий `Data/CorrespondenceAttachments`; immutable PDF/JPG/PNG/TIFF/DOCX з stable `ca-...`, SHA256/MIME/size/original filename; content-addressed dedupe; live `vault:vd-...` link лише на реальний DocumentVault без копії байтів; content/integrity guards; remove = історична подія без видалення байтів; full backup/restore. Attachment не змінює sent/received/status.

## Наступний крок

**10.24-r3 — відповіді, справи й контроль строків** за §10.3–10.4 плану #543:
- явні контрольовані переходи стану incoming;
- фактичне `Позначити відправленим` для outgoing окремо від реєстрації, з sent_date/channel;
- safe reply creation: вихідна відповідь має явний link, номер тільки при реєстрації;
- due-date/overdue без вигаданих нормативних строків;
- logical case/thread для кількох листів без копій документів;
- append-only history для станів/зв'язків;
- full backup/restore regression.

UI журналу/картки — наступним окремим пакетом поверх завершених r1–r3 API. Автоматичний e-mail, OCR/AI APPLY і physical purge не робити.

AI-ready import r6–r10 завершений на REVIEW без APPLY. APPLY не починати без окремого рішення власника.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.
