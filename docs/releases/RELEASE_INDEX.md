# Індекс релізів Taxo

**Стан:** 01.10.2026  
**Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) — immutable  
**Latest full multi-platform checkpoint:** [Taxo 10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1)  
**Latest integrated code checkpoint in `main`:** Taxo **10.9-r1** — merged via PR #118  
**Next code revision:** **10.9-r2**.

> `v10.3` лишається stable до окремого рішення власника. `v10.9-r1` — актуальний інтегрований full multi-platform checkpoint; це не автоматичне stable promotion.

## Поточний checkpoint

| Ревізія | Main / issued source | Перевірка | Пакети / зміст |
|---|---|---|---|
| **10.9-r1** | main merge `843a38243dd4eeeb02b40f8de59cc630ef4dce09`; tag source `b0eebbf88b22fbd7761544640d9804416a328acb` | exact-source regression **730/730 OK**; full package `36857771398` — success | Windows x64 Setup/Portable, Windows 7 SP1 x64 Setup/Portable + PE gate, macOS ARM64/Intel, START, platform/full SHA-256; data-access foundation + cumulative 10.8-r4…r10 integration |

START: `Taxo_v10_9_candidate_r1_START.zip`  
SHA-256: `0c819f9f3e4b31f58e6b86e2b4f1d72086901c0bd2a26a499e4c17f6de9c1766`

## Taxo 10.9 history

| Ревізія | Issued source | Статус | Зміст |
|---|---|---|---|
| **10.9-r1** | `b0eebbf88b22fbd7761544640d9804416a328acb` | **full multi-platform checkpoint; PR #118 merged** | `data_access.py`, transaction boundary, `ApplicationServices.data`, єдина workspace-aware infrastructure path |

## Taxo 10.8 history після r3

| Ревізія | Статус | Зміст |
|---|---|---|
| 10.8-r10 | immutable historical checkpoint | `database_runtime.py`, SQLite connection policy |
| 10.8-r9 | immutable historical checkpoint | `backup_migration.py`, backup/restore/legacy migration mechanics |
| 10.8-r8 | immutable historical checkpoint | `application_context.py`, application/infrastructure services |
| 10.8-r7 | immutable historical checkpoint | ordered feature-layer registry |
| 10.8-r6 | immutable historical checkpoint | `output_files.py`, перший slice декомпозиції `main.py` |
| 10.8-r5 | immutable historical checkpoint | прогноз ТО, заявки на ремонт, compact STOIR summary |
| 10.8-r4 | immutable historical checkpoint | базовий СТОІР / ТО ТЗ |
| 10.8-r3 | full historical checkpoint | ТЦК date fix + optional vehicle requisites |
| 10.8-r2 | fast-test | runtime Tk/ttk UI smoke tests |
| 10.8-r1 | fast-test | functionality-contract guard інтерфейсу |

## Останні повні multi-platform checkpoints

| Tag | Статус | Пакети |
|---|---|---|
| [v10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1) | **Latest full multi-platform checkpoint** | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, platform/full SHA-256 |
| [v10.8-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.8-r3) | previous full checkpoint | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, platform/full SHA-256 |
| [v10.6-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r10) | historical | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, platform/full SHA-256 |
| [v10.6-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3) | historical | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, SHA-256 |
| [v10.5-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8) | historical | Windows x64/Win7, macOS ARM64/Intel, START, SHA-256 |

## Stable line

| Tag | Статус |
|---|---|
| [v10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) | **Current stable** |
| [v10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1) | Previous stable / rollback |
| [v10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0) | Historical stable |
| [v9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1) | Historical stable |

## Документи поточної лінії

- [Release notes 10.9-r1](RELEASE_NOTES_v10.9-r1.md)
- [Release notes 10.8-r10](RELEASE_NOTES_v10.8-r10.md)
- [Release notes 10.8-r9](RELEASE_NOTES_v10.8-r9.md)
- [Release notes 10.8-r8](RELEASE_NOTES_v10.8-r8.md)
- [Release notes 10.8-r7](RELEASE_NOTES_v10.8-r7.md)
- [Release notes 10.8-r6](RELEASE_NOTES_v10.8-r6.md)
- [Release notes 10.8-r5](RELEASE_NOTES_v10.8-r5.md)
- [Release notes 10.8-r4](RELEASE_NOTES_v10.8-r4.md)

Точна історія старіших revisions збережена в Git history, release notes та Issue #61. Старі work/candidate branches не використовуються як нова кодова база.

## Release policy

1. Stable формується тільки після manual operational gate та окремого рішення власника.
2. Виданий tag/release не пересувається і не перевидається поверх іншого коду.
3. Full multi-platform checkpoint містить Windows, Windows 7 compatibility packages, macOS packages, START та checksums.
4. БД, SQLite, скани, кеші та персональні документи не публікуються.
5. Кодові зміни йдуть через окрему work branch і PR.
6. «Злити у main» = перевірки → інтеграція → синхронізація документації → повні пакети/checksums, якщо не вказано інше.
7. Після завершеного `10.9-r1` наступна кодова зміна — `10.9-r2`; issued revision не використовується повторно.