# Поточна контрольна точка Taxo

**22.11.2026 — Stable/Latest 10.23-r4; Current Test 10.23-r8.**

## Stable

- Release: [v10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4)
- Exact source: `a919ced6bc8665ced70ebb4d897808e4e2618667`
- 8 assets; owner manual acceptance 20.11.2026; stable promotion #44811800328 SUCCESS.
- 37 strict live UI routes.

## Test

- Release: [v10.23-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r8)
- Exact source: `d3d34f7a0fc3de88280324eaeb2d97a72c172359`
- 8 assets; prerelease; publisher #44948759163 SUCCESS.
- START #44947743150, Windows #44947743153, Win7 #44947743132, macOS Intel/ARM #44947743115 — SUCCESS.
- Windows/Win7 mandatory Microsoft Defender malware gates + post-scan package integrity — SUCCESS.
- Verified managed batch reader + deterministic read-only sorting preview; source archive і batch не змінюються.
- Stable/Latest не змінено.

## Наступний напрям

Нормативна AI-ready модель: [DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md](../DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md).

Наступний кодовий крок — **10.23-r9**: read-only **ANALYZE → PROPOSE** contract поверх verified r8 batch. Versioned proposal record, deterministic metadata hints, confidence/reason/review_state, без OCR, зовнішніх AI-викликів, registry APPLY або фізичних move/rename/delete/copy.

#553/#556/#562 не закривати автоматично; draft #543/#395 не чіпати.

Актуальний стан: [PROJECT_STATE](../../PROJECT_STATE.md) · [HANDOFF](../../HANDOFF_CURRENT.md) · [WORKLOG](../../WORKLOG.md).
