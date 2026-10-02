# Індекс релізів Taxo

**Стан:** 02.10.2026  
**Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) — immutable  
**Latest integrated code checkpoint in `main`:** **Taxo 10.9-r9** — cumulative PR #128 / merge `3f59544b8737cd4715d84f786e32378d87d1dd99`  
**Latest issued fast-test:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)  
**Latest full multi-platform published checkpoint:** [Taxo 10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1)  
**Next code revision:** **10.9-r10**.

> `v10.3` лишається stable до окремого рішення власника. `main` уже інтегрований до 10.9-r9. Історичні fast-test releases зберігаються як immutable checkpoints, але не є паралельними актуальними гілками розвитку.

## Поточний інтегрований checkpoint

| Ревізія | Main / issued source | Перевірка | Статус |
|---|---|---|---|
| **10.9-r9** | main merge `3f59544b8737cd4715d84f786e32378d87d1dd99`; tag source `a368bf3bdfd4a16cc099844b830379c5e2646c2d` | Windows `36919102579` — success; macOS `36919102540` — success | **latest integrated code checkpoint**; cumulative r2…r9 |

START: `Taxo_v10_9_candidate_r9_START.zip`  
SHA-256: `9c30bf70e8c7adc4f2560a22e2bdfa2c26d698573982de01aafa4b34bbcd62d4`

## Taxo 10.9 history

| Ревізія | Статус | Зміст |
|---|---|---|
| **10.9-r9** | **integrated in main; fast-test immutable** | SQLite schema compatibility baseline (`PRAGMA user_version`) |
| 10.9-r8 | historical fast-test; integrated through r9 | immutable approved/signed orders and driver→vehicle assignment safety |
| 10.9-r7 | historical fast-test; integrated through r9 | STOIR odometer chronology and maintenance forecast safety |
| 10.9-r6 | historical fast-test; integrated through r9 | personnel balance / P-5 safety, employment-aware history |
| 10.9-r5 | historical fast-test; integrated through r9 | tachograph / 60-day activity safety |
| 10.9-r4 | historical fast-test; integrated through r9 | work/rest compliance hardening |
| 10.9-r3 | historical fast-test; integrated through r9 | vehicle document validity for the whole trip |
| 10.9-r2 | historical fast-test; integrated through r9 | waybill history, number reuse and retention guards |
| 10.9-r1 | full multi-platform checkpoint | data-access foundation + cumulative 10.8-r4…r10 integration |

PR #121–#127 are closed as historical/superseded. PR #128 is the single cumulative integration point for r2…r9.

## Останні повні multi-platform checkpoints

| Tag | Статус | Пакети |
|---|---|---|
| [v10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1) | **Latest full multi-platform published checkpoint** | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, platform/full SHA-256 |
| [v10.8-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.8-r3) | previous full checkpoint | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, platform/full SHA-256 |
| [v10.6-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r10) | historical | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, platform/full SHA-256 |

## Stable line

| Tag | Статус |
|---|---|
| [v10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) | **Current stable** |
| [v10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1) | Previous stable / rollback |
| [v10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0) | Historical stable |
| [v9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1) | Historical stable |

## Current 10.9 documents

- [Release notes 10.9-r9](RELEASE_NOTES_v10.9-r9.md)
- [Release notes 10.9-r8](RELEASE_NOTES_v10.9-r8.md)
- [Release notes 10.9-r7](RELEASE_NOTES_v10.9-r7.md)
- [Release notes 10.9-r6](RELEASE_NOTES_v10.9-r6.md)
- [Release notes 10.9-r5](RELEASE_NOTES_v10.9-r5.md)
- [Release notes 10.9-r4](RELEASE_NOTES_v10.9-r4.md)
- [Release notes 10.9-r3](RELEASE_NOTES_v10.9-r3.md)
- [Release notes 10.9-r2](RELEASE_NOTES_v10.9-r2.md)
- [Release notes 10.9-r1](RELEASE_NOTES_v10.9-r1.md)

## Release policy

1. Stable формується тільки після manual operational gate та окремого рішення власника.
2. Виданий tag/release не пересувається і не перевидається поверх іншого коду.
3. Full multi-platform checkpoint містить Windows, Windows 7 compatibility packages, macOS packages, START та checksums.
4. БД, SQLite, скани, кеші та персональні документи не публікуються.
5. Новий код починається тільки від актуального `main`.
6. Historical work/candidate branches and stacked PRs are never reused as current development bases.
7. Після завершеного `10.9-r9` наступна кодова зміна — `10.9-r10`; issued revision не використовується повторно.
