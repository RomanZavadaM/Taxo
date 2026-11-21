# Поточна контрольна точка Taxo

**21.11.2026 — Stable/Latest 10.23-r4; Current Test 10.23-r6.**

## Stable

- Release: [v10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4)
- Exact source: `a919ced6bc8665ced70ebb4d897808e4e2618667`
- 8 assets; owner manual acceptance 20.11.2026; stable promotion #44811800328 SUCCESS.
- 37 strict live UI routes.

## Test

- Release: [v10.23-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r6)
- Exact source: `5a321e98c39443f3d37c89837352402df4542551`
- 8 assets; prerelease; publisher #44933358679 SUCCESS.
- START #44932279502, Windows #44932280241, Win7 #44932279586, macOS Intel/ARM #44932279465 — SUCCESS; Defender/integrity PASS.
- Read-only inventory existing archive: SHA256/MIME/size/mtime, stable candidate_id, versioned manifest, exact duplicate groups, symlink skip.
- Немає move/rename/delete/copy, OCR, AI classification чи APPLY.
- Stable/Latest не змінено.

## Наступний напрям

Нормативна AI-ready модель: [DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md](../DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md).

Наступний вузький кодовий крок — **10.23-r7**: атомарно зберігати dry-run inventory/report у керованому workspace як import batch, із повторюваною identity та перевіркою hash. Source-архів не змінювати; AI ANALYZE/PROPOSE/APPLY і фізичне сортування ще не реалізовувати.

#553/#556/#562 не закривати автоматично; draft #543/#395 не чіпати.

Актуальний стан: [PROJECT_STATE](../../PROJECT_STATE.md) · [HANDOFF](../../HANDOFF_CURRENT.md) · [WORKLOG](../../WORKLOG.md).
