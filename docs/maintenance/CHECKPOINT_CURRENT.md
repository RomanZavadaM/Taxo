# Taxo — поточна контрольна точка

**Дата:** 05.10.2026
**Stable:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10) — immutable; перевірено власником на реальних даних
**Previous stable / rollback:** Taxo 10.3 / `v10.3`
**Тестова лінія в `main`:** 10.10-r3 (`v10.10-r1`…`r3` — prerelease, перевіряються на реальних даних)
**Next code revision:** `10.10-r4`
**Recovery:** `START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61

## Stable 10.9-r10

- Код: main merge `5e179eabccc35afa984be04208e2e4d96094a2fb` (PR #132); exact PR head `ff56519da35e03204bdaf77f7187cddd692f79d4` (ідентичне git tree).
- Пакети — оригінальні CI-збірки exact head: Windows `37018721703`, Windows 7 `37018721695`, macOS `37018722335`, START `37018715592`; SHA-256 збігаються з CI.
- Перевірено власником на реальних даних (3 дні роботи) і промотовано в stable 05.10.2026.

## Тестова лінія 10.10 (prerelease)

| Ревізія | PR | Зміст |
|---|---|---|
| 10.10-r1 | #136 | без PyMuPDF (AGPL-3.0) |
| 10.10-r2 | #137 | CI hardening; ізоляція тестів |
| 10.10-r3 | #138 | правильна версія у вікні; попередження «лише БД» |

Release notes stable: [../releases/RELEASE_NOTES_v10.9-r10.md](../releases/RELEASE_NOTES_v10.9-r10.md).
Повний аудит: [AUDIT_FULL_2026-10-05.md](AUDIT_FULL_2026-10-05.md).
