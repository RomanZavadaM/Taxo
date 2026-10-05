# Індекс релізів Taxo

**Стан:** 05.10.2026
**Stable:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10) — immutable; перевірено власником на реальних даних
**Previous stable / rollback:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) — immutable
**Next code revision:** **10.10-r4**.

> Stable 10.9-r10 опубліковано з оригінальними CI-збірками, які перевірялись. Лінія 10.10 — prerelease для перевірки на реальних даних.

## Тестова лінія 10.10 (prerelease)

| Реліз | PR | Зміст |
|---|---|---|
| [10.10-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) | #138 | правильна версія у вікні; попередження «лише БД» |
| [10.10-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r2) | #137 | CI hardening; ізоляція тестів |
| [10.10-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r1) | #136 | без PyMuPDF |

## Stable 10.9-r10 і попередні checkpoint-и

| Ревізія | Main / source | Перевірка | Статус |
|---|---|---|---|
| **10.9-r10** | PR #132; main merge `5e179eabccc35afa984be04208e2e4d96094a2fb`; exact PR head `ff56519da35e03204bdaf77f7187cddd692f79d4` | Windows `37018721703`; Win7 `37018721695`; macOS `37018722335` — success | **STABLE (05.10.2026)**; repository structural cleanup |
| **10.9-r9** | tag source `a368bf3bdfd4a16cc099844b830379c5e2646c2d` | Windows/macOS exact-head gates passed | **latest full multi-platform published checkpoint** |

## Taxo 10.9 history

| Ревізія | Статус | Зміст |
|---|---|---|
| **10.9-r10** | **STABLE** | full repository structural cleanup: `src/taxo/`, `assets/`, `packaging/`, START/build path updates |
| **10.9-r9** | full multi-platform published checkpoint | SQLite schema compatibility baseline (`PRAGMA user_version`) + cumulative r2…r9 |
| 10.9-r8 | historical fast-test; integrated through r9 | immutable approved/signed orders and driver→vehicle assignment safety |
| 10.9-r7 | historical fast-test; integrated through r9 | STOIR odometer chronology and maintenance forecast safety |
| 10.9-r6 | historical fast-test; integrated through r9 | personnel balance / P-5 safety, employment-aware history |
| 10.9-r5 | historical fast-test; integrated through r9 | tachograph / 60-day activity safety |
| 10.9-r4 | historical fast-test; integrated through r9 | work/rest compliance hardening |
| 10.9-r3 | historical fast-test; integrated through r9 | vehicle document validity for the whole trip |
| 10.9-r2 | historical fast-test; integrated through r9 | waybill history, number reuse and retention guards |
| 10.9-r1 | previous full multi-platform checkpoint | data-access foundation + cumulative 10.8-r4…r10 integration |

## Останні повні multi-platform checkpoints

| Tag | Статус | Пакети |
|---|---|---|
| [v10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9) | **Latest full multi-platform published checkpoint** | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, SHA-256 |
| [v10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1) | previous full checkpoint | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, SHA-256 |
| [v10.8-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.8-r3) | historical full checkpoint | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, SHA-256 |
| [v10.6-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r10) | historical | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, SHA-256 |

## Stable line

| Tag | Статус |
|---|---|
| [v10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) | **Current stable** |
| [v10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1) | Previous stable / rollback |
| [v10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0) | Historical stable |
| [v9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1) | Historical stable |

## Current 10.9 documents

- [Release notes 10.9-r10](RELEASE_NOTES_v10.9-r10.md)
- [Release notes 10.9-r9](RELEASE_NOTES_v10.9-r9.md)
- [Release notes 10.9-r8](RELEASE_NOTES_v10.9-r8.md)
- [Release notes 10.9-r7](RELEASE_NOTES_v10.9-r7.md)
- [Release notes 10.9-r6](RELEASE_NOTES_v10.9-r6.md)
- [Release notes 10.9-r5](RELEASE_NOTES_v10.9-r5.md)
- [Release notes 10.9-r4](RELEASE_NOTES_v10.9-r4.md)
- [Release notes 10.9-r3](RELEASE_NOTES_v10.9-r3.md)
- [Release notes 10.9-r2](RELEASE_NOTES_v10.9-r2.md)
- [Release notes 10.9-r1](RELEASE_NOTES_v10.9-r1.md)

## Historical identity anchors

- **Taxo 10.4-r7** — immutable historical issued checkpoint, source `9f397a092fe828570927bc39cef7a3a467e2aff0`.
- **Taxo 10.6-r10** — historical full multi-platform checkpoint.
- **Taxo 10.8-r3** — historical full checkpoint перед лінією 10.8-r4…10.9-r1.

## Release policy

1. Stable формується тільки після manual operational gate та окремого рішення власника.
2. Виданий tag/release не пересувається і не перевидається поверх іншого коду.
3. Full multi-platform checkpoint містить Windows, Windows 7 compatibility packages, macOS packages, START та checksums.
4. БД, SQLite, скани, кеші та персональні документи не публікуються.
5. Новий код починається тільки від актуального `main`.
6. Historical work/candidate branches and stacked PRs are never reused as current development bases.
7. Після завершеного `10.9-r10` наступна кодова зміна — `10.10-r1`.
