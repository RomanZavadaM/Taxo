# Поточна контрольна точка Taxo

**22.11.2026 — Stable/Latest 10.23-r4; Current Test 10.23-r10.**

## Stable

- Release: [v10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4)
- Exact source: `a919ced6bc8665ced70ebb4d897808e4e2618667`
- 8 assets; owner manual acceptance 20.11.2026; stable promotion #44811800328 SUCCESS.
- 37 strict live UI routes.

## Test

- Release: [v10.23-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r10)
- Exact source: `f87991c624a971fe3ffd4112e5dfde9fd9e4b6cd`
- 8 assets; prerelease; publisher #45049398522 SUCCESS.
- START #45048321322, Windows #45048321299, Win7 #45048321313, macOS Intel/ARM #45048321471 — SUCCESS.
- Windows/Win7 mandatory Microsoft Defender malware gates + post-scan package integrity — SUCCESS.
- Explicit REVIEW decisions are stored separately from source/import batch and have `applies_changes=false`.
- Stable/Latest не змінено.

## Наступний напрям

Після `10.23-r10` наступна ревізія — **10.24-r1**.

Наступний кодовий пакет — фундамент **«Ділова кореспонденція»**: окремий доменний модуль і safe persistence для incoming/outgoing registry, separate numbering, registration date, correspondent, subject, execution deadline/status, reply/related links та зв'язок із готовим документом без дублювання файла. Не розростати `main.py`; не робити імпортний APPLY без окремого рішення власника.

#553/#556/#562 не закривати автоматично; draft #543/#395 не чіпати.

Актуальний стан: [PROJECT_STATE](../../PROJECT_STATE.md) · [HANDOFF](../../HANDOFF_CURRENT.md) · [WORKLOG](../../WORKLOG.md).
