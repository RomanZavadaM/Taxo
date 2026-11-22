# Поточна контрольна точка Taxo

**22.11.2026 — Stable/Latest 10.23-r4; Current Test 10.23-r9.**

## Stable

- Release: [v10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4)
- Exact source: `a919ced6bc8665ced70ebb4d897808e4e2618667`
- 8 assets; owner manual acceptance 20.11.2026; stable promotion #44811800328 SUCCESS.
- 37 strict live UI routes.

## Test

- Release: [v10.23-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r9)
- Exact source: `9f41c46a4745815cfc7518f7319f6c6f941ba559`
- 8 assets; prerelease; publisher #45045127128 SUCCESS.
- START #45043933564, Windows #45043933540, Win7 #45043933535, macOS Intel/ARM #45043933592 — SUCCESS.
- Windows/Win7 mandatory Microsoft Defender malware gates + post-scan package integrity — SUCCESS.
- Read-only ANALYZE→PROPOSE deterministic metadata hints; source archive і persisted batch не змінюються.
- Stable/Latest не змінено.

## Наступний напрям

Нормативна AI-ready модель: [DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md](../DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md).

Наступний кодовий крок — **10.23-r10**: людський REVIEW для r9 proposals — versioned decision ledger, explicit accept/reject/edit, черга needs_review. Без автоматичного APPLY, OCR, зовнішнього AI API або фізичних move/rename/delete/copy.

Після r10 — окремий модуль вхідної/вихідної кореспонденції за draft #543.

#553/#556/#562 не закривати автоматично; draft #543/#395 не чіпати.

Актуальний стан: [PROJECT_STATE](../../PROJECT_STATE.md) · [HANDOFF](../../HANDOFF_CURRENT.md) · [WORKLOG](../../WORKLOG.md).
