# HANDOFF_CURRENT — Taxo

**21.11.2026 — 10.23-r6 опубліковано як Test prerelease; Stable/Latest лишається 10.23-r4.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`, GitHub Latest.

**Test:** [10.23-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r6), exact source `5a321e98c39443f3d37c89837352402df4542551`, 8 assets, prerelease. Publisher #44933358679 — SUCCESS.

Exact-source r6 CI: START #44932279502, Windows #44932280241, Win7 #44932279586, macOS Intel/ARM #44932279465 — SUCCESS; Defender/integrity PASS.

## Що додає r6

- read-only inventory довільної існуючої папки документів;
- source path / relative path / name, file size, MIME, modified time, SHA256;
- стабільний `candidate_id` для незміненого файла;
- machine-readable manifest `taxo.document-inventory.v1`;
- exact duplicate groups лише за однаковим SHA256;
- symlink-и не проходяться;
- змінений файл стає новим кандидатом;
- AI-поля поки порожні, `review_state=inventory`;
- жодного move/rename/delete/copy, OCR, AI-класифікації або APPLY.

## Нормативна AI-ready модель

`docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md` уже в main. Канонічна структура — stable document identity + metadata + links; дерево папок лише представлення. Оригінали не змінюються. Масова робота має staging INVENTORY → ANALYZE → PROPOSE → REVIEW → APPLY → VERIFY, confidence/reason/review, import batch + rollback і dry-run перед APPLY.

## Наступний крок

**10.23-r7:** збереження dry-run inventory/report у керованому workspace (`Data/DocumentLibrary/import_batches` або еквівалент) атомарно, з batch identity та повторюваністю. Вихідний архів і далі не змінювати; ніякого AI APPLY чи фізичного сортування.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.
