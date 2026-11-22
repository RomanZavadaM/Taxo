# HANDOFF_CURRENT — Taxo

**22.11.2026 — 10.23-r8 опубліковано як Test prerelease; Stable/Latest лишається 10.23-r4.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`, GitHub Latest.

**Current Test:** [10.23-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r8), exact source `d3d34f7a0fc3de88280324eaeb2d97a72c172359`, 8 assets, prerelease. Publisher #44948759163 — SUCCESS.

Exact-source r8 CI: START #44947743150, Windows #44947743153, Win7 #44947743132, macOS Intel/ARM #44947743115 — SUCCESS. Windows і Win7 mandatory Microsoft Defender gates та post-scan integrity verification — SUCCESS.

## Що додає r8

- read-only відкриття лише керованого r7 import batch;
- перевірка format, batch ID, source root, inventory/report і checksum manifest;
- fail-closed для corrupted checksum, missing/malformed batch та unknown future format;
- deterministic preview режими `date_desc`, `number_asc`, `category_asc`, `source_asc`;
- порожні/невідомі дати, номери й категорії йдуть у кінець;
- natural number sort: `2-A` перед `10-A`;
- stable candidate/document identity — остаточний tie-breaker;
- exact duplicate groups, errors, skipped та unresolved metadata лишаються видимими у preview;
- source-файли й batch не змінюються; OCR/AI APPLY/registry write/move/rename/delete/copy відсутні.

## Нормативна AI-ready модель

`docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md` — джерело правил: immutable originals, stable identity + metadata + links, staging `INVENTORY → ANALYZE → PROPOSE → REVIEW → APPLY → VERIFY`, confidence/reason/review, import batch + rollback та dry-run перед APPLY.

## Наступний крок

**10.23-r9:** безпечний read-only шар **ANALYZE → PROPOSE** поверх verified r8 batch. Спочатку формалізувати versioned proposal record та deterministic rule-based metadata hints із назви/шляху/наявних полів; результат лише preview/proposal з confidence/reason/review_state. Не робити OCR, зовнішніх AI-викликів, registry APPLY, зміни юридично значимих реквізитів або фізичних move/rename/delete/copy.

Кореспонденція залишається наступним окремим модулем за планом #543 після завершення безпечної основи документного імпорту.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.
