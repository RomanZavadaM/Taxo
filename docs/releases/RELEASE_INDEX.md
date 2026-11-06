# Індекс релізів Taxo

**Стан:** 06.11.2026
**Stable:** [Taxo 10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) — виправлена macOS-версія, stable 05.11.2026
**Previous stable / rollback:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10)
**Older rollback:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)
**Current published candidate:** [**Taxo 10.11-r3**](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r3) — **PRERELEASE** 06.11.2026; exact source `a82a3dc6`; 8 files incl. START and SHA256. Stable remains 10.10-r5.  
**Next code revision:** **10.11-r4**.

> Stable 10.10-r4 використовує ті самі перевірені пакети, що були випущені як candidate; перезбирання після рішення про stable не виконувалось. 10.9-r10 лишається попередньою stable для rollback.

## Кандидатна лінія 10.11

| Версія | PR | Стан |
|---|---|---|
| [**10.11-r3**](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r3) | #176, release #177 | **PRERELEASE 06.11.2026**; exact source `a82a3dc6`; START/Windows/Win7/macOS SUCCESS; 8 assets. Захист існуючого факту та атомарне перепланування. Stable — r5. |
| [**10.11-r2**](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r2) | #169, build-fix #171, release #172 | **PRERELEASE 05.11.2026**; exact source `68d7459b`; START/Windows/Win7/macOS SUCCESS; 8 assets. Назви простого графіка працівників + PDF без «Роль». Stable — r5. |
| [**10.11-r1**](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r1) | #163, #165, #166, #167 | **PRERELEASE 05.11.2026**; CI START/Windows/Win7/macOS SUCCESS; 8 assets, SHA256. UX звітів, назви файлів водійського графіка. Stable — r5. |
| **10.10-r10** | #162 | Integrated; вибір водіїв для звіту, «част.» |
| **10.10-r9** | #160 | Integrated; графік водіїв + коригування відсутностей |

Зауваження r1 до друкованого графіка працівників (назва файлу і колонка «Роль») закриті в 10.11-r2. Два критичні дефекти цілісності даних із code-review 06.11 закриті в 10.11-r3. Подальше системне спрощення інтерфейсу залишається в Issue #164; інші findings — Issue #175.

## Лінія 10.10

| Реліз | PR | Зміст |
|---|---|---|
| [**10.10-r5**](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) | #151 | **STABLE 05.11.2026**; виправлено запуск macOS; повний комплект Windows/Win7/macOS/START |
| [10.10-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r4) | #144 | superseded: підтверджена проблема запуску на macOS; історичний immutable release |
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
| [v10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) | **Current stable** |
| [v10.10-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r4) | Superseded — macOS startup issue |
| [v10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10) | Previous stable / rollback |
| [v10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) | Older rollback |
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
7. Після виданого `10.11-r3` наступна кодова зміна — `10.11-r4`; stable змінюється лише окремим рішенням власника.
