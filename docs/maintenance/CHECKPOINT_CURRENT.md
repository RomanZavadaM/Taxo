# Taxo — поточна контрольна точка

**Дата:** 05.10.2026
**Stable:** [Taxo 10.10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10) — 05.10.2026, immutable
**Previous stable / rollback:** Taxo 10.3 / `v10.3`
**Verified candidate:** Taxo 10.10-r3 / `v10.10-r3` (перевірено власником)
**Next code revision:** `10.10-r4`
**Recovery:** `START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61

## Stable 10.10

- Код = перевірена власником ревізія 10.10-r3 + ідентичність версії `10.10` (за зразком stable 10.3).
- Пакети: Windows 10/11 x64 Setup/Portable, Windows 7 SP1 x64 Portable, macOS ARM64/Intel Portable, START, SHA-256 — зібрані CI з stable-коміту `main`.
- Робочі БД, SQLite, скани й персональні документи до релізу не входять.

## Лінія 10.10

| Ревізія | PR | Зміст |
|---|---|---|
| 10.10-r1 | #136 | без PyMuPDF (AGPL-3.0); pypdfium2 + reportlab + pypdf; license gate |
| 10.10-r2 | #137 | CI hardening; ізоляція тестів |
| 10.10-r3 | #138 | правильна версія в програмі; попередження «лише БД» |

Release notes: [../releases/RELEASE_NOTES_v10_10.md](../releases/RELEASE_NOTES_v10_10.md).
Повний аудит: [AUDIT_FULL_2026-10-05.md](AUDIT_FULL_2026-10-05.md).
