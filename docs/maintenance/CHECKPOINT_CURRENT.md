# Поточна контрольна точка Taxo

**21.11.2026 — Stable/Latest 10.23-r4; Current Test 10.23-r7.**

## Stable

- Release: [v10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4)
- Exact source: `a919ced6bc8665ced70ebb4d897808e4e2618667`
- 8 assets; owner manual acceptance 20.11.2026; stable promotion #44811800328 SUCCESS.
- 37 strict live UI routes.

## Test

- Release: [v10.23-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r7)
- Exact source: `a60d1933ddde090f0cb5e8672c5070030647301d`
- 8 assets; prerelease; publisher #44944448052 SUCCESS.
- START #44943282760, Windows #44943282736, Win7 #44943282765, macOS Intel/ARM #44943282733 — SUCCESS; Defender/integrity PASS.
- Atomic dry-run inventory batch store у workspace: inventory/report/checksum, idempotent reuse, fail-closed conflicts, source read-only.
- Stable/Latest не змінено.

## Наступний напрям

Нормативна AI-ready модель: [DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md](../DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md).

Наступний вузький кодовий крок — **10.23-r8**: verified batch reader + deterministic sorting preview. Перевіряти format/checksum, читати batch read-only і формувати стабільний preview за датою/номером/категорією/видом із stable identity tie-breaker. OCR, AI ANALYZE/PROPOSE/APPLY і фізичне сортування ще не реалізовувати.

#553/#556/#562 не закривати автоматично; draft #543/#395 не чіпати.

Актуальний стан: [PROJECT_STATE](../../PROJECT_STATE.md) · [HANDOFF](../../HANDOFF_CURRENT.md) · [WORKLOG](../../WORKLOG.md).
