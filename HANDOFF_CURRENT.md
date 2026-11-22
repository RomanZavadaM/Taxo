# HANDOFF_CURRENT — Taxo

**22.11.2026 — 10.23-r9 опубліковано як Test prerelease; Stable/Latest лишається 10.23-r4.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`, GitHub Latest.

**Current Test:** [10.23-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r9), exact source `9f41c46a4745815cfc7518f7319f6c6f941ba559`, 8 assets, prerelease. Publisher #45045127128 — SUCCESS.

Exact-source r9 CI: START #45043933564, Windows #45043933540, Win7 #45043933535, macOS Intel/ARM #45043933592 — SUCCESS. Windows і Win7 mandatory Microsoft Defender gates та post-scan integrity verification — SUCCESS.

## Що додає r9

- versioned read-only proposal format `taxo.document-import-proposals.v1`;
- deterministic ruleset `taxo.document-metadata-hints.v1`;
- пропозиції для `document_date`, `document_number`, `document_kind`, `category` і описової `title`;
- кожна пропозиція має confidence, reason і версію правила;
- неоднозначні дати/категорії не вгадуються, а переходять у `needs_review`;
- вже наявні структуровані реквізити не переписуються;
- короткі маркери й номерні позначки мають межі токенів, щоб не ловити випадкові підрядки;
- analysis працює тільки з verified r8 view; source-файли не відкриваються повторно;
- persisted batch, DocumentVault/БД, паперовий підпис і source-архів не змінюються;
- OCR, зовнішні AI/model API, APPLY, move/rename/delete/copy відсутні.

## Нормативна AI-ready модель

`docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md` — джерело правил: immutable originals, stable identity + metadata + links, staging `INVENTORY → ANALYZE → PROPOSE → REVIEW → APPLY → VERIFY`, confidence/reason/review, import batch + rollback та dry-run перед APPLY.

## Наступний крок

**10.23-r10:** безпечний шар **REVIEW** поверх r9 proposals: versioned review record, явні рішення користувача `confirm/reject/needs_review`, відновлення рішення після restart і прив'язка до import_batch_id + candidate_id + sha256. Рішення зберігати окремо від source/batch та не застосовувати до DocumentVault/БД. Без OCR, зовнішніх AI-викликів, APPLY або фізичних move/rename/delete/copy.

Після r10 — перейти до окремого модуля вхідної/вихідної кореспонденції за планом #543; APPLY імпортних пропозицій не робити автоматично без окремого рішення власника.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.
