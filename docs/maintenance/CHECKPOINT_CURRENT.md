# Поточна контрольна точка Taxo

**22.11.2026 — Stable/Latest 10.23-r4; Current Test 10.24-r1.**

## Stable

- Release: [v10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4)
- Exact source: `a919ced6bc8665ced70ebb4d897808e4e2618667`
- 8 assets; owner manual acceptance 20.11.2026; stable promotion #44811800328 SUCCESS.
- 37 strict live UI routes.

## Test

- Release: [v10.24-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r1)
- Exact source: `adb6ae40e966d77018c6dc8c1c4fdcbde6a6a827`
- 8 assets; prerelease; publisher #45053863942 SUCCESS.
- START #45052687870, Windows #45052687839, Win7 #45052687867, macOS Intel/ARM #45052687880 — SUCCESS.
- Windows/Win7 mandatory Microsoft Defender malware gates + post-scan package integrity — SUCCESS.
- Два журнали business correspondence, independent annual numbering, semantic dates, response links, document_ref without byte copy, atomic registry і full backup/restore.
- Stable/Latest не змінено.

## Наступний напрям

**10.24-r2:** контрольовані файли/вкладення кореспонденції та backup/restore.

Межі r2: immutable attachment bytes або stable link на вже наявний vault; SHA256/MIME/filename/size/stable attachment ID; attachment→correspondence link; safe history/remove semantics; backup/restore. Attachment не є автоматичним доказом отримання/відправлення. UI/e-mail/OCR/AI та справи — окремими наступними ревізіями.

AI-import APPLY після r10 не починати без окремого рішення власника.

#553/#556/#562 не закривати автоматично; draft #543/#395 не чіпати.

Актуальний стан: [PROJECT_STATE](../../PROJECT_STATE.md) · [HANDOFF](../../HANDOFF_CURRENT.md) · [WORKLOG](../../WORKLOG.md).
