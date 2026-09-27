# Індекс релізів Taxo

**Стан:** 28.09.2026  
**Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) — immutable  
**Latest full checkpoint:** [Taxo 10.4-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r2) — merged  
**Latest issued fast-test revision:** **Taxo 10.5-r1** — immutable  
**Next code revision:** **10.5-r2**.

> `v10.4-r2` лишається останнім повним multi-platform checkpoint у `main`. Ревізії після нього — швидкі START-checkpoint-и для інтенсивної розробки; вони не підміняють stable/full release без окремого рішення власника.

## Поточна fast-test лінія

### Full checkpoints

| Tag | Статус | Пакети | Призначення |
|---|---|---|---|
| [v10.4-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r2) | **Latest full checkpoint; merged** | Modern Windows Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START + SHA-256 | UI remediation, vehicle docs, waybill readability, reusable Win7 PE gate |
| [v10.4-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r1) | Previous full checkpoint; merged | Modern Windows Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START + SHA-256 | First full 10.4 checkpoint with accepted Windows 7 support |

Документи:
- [Release notes 10.4-r2](RELEASE_NOTES_v10_4_r2.md)
- [Release notes 10.4-r1](RELEASE_NOTES_v10_4_r1.md)

### Fast-test START checkpoints

| Ревізія | Issued code head | Перевірка | Статус / напрям |
|---|---|---|---|
| **Taxo 10.5-r1** | `d7e5a730767ebc17e6935b2d3f25208a9f151c16` | run `36355353170`, `399/399 OK`, artifact `10943696206` | **Latest fast-test; immutable** — відомість військово-транспортного обліку по власному/балансовому транспорту |
| Taxo 10.4-r10 | `0f7944ad3f86bb6ee8ad19b40cfb2b38d924b934` | run `36351811271`, `388/388 OK`, artifact `10942183754` | immutable — військово-транспортний облік ТЗ |
| Taxo 10.4-r9 | `c09aee3588e95682a1d990c681b10c808183b041` | run `36350115825`, `366/366 OK`, artifact `10942445098` | immutable — покомпонентна звірка працівників і військовий облік 2026 |
| Taxo 10.4-r8 | `1c0607ee733217c0d4d0bc459af4c0a175a0409f` | run `36346821842`, `340/340 OK`, artifact `10941021984` | immutable — звірка ТЗ / «Шлях» та контрольні нагадування |
| Taxo 10.4-r7 | `9f397a092fe828570927bc39cef7a3a467e2aff0` | run `36344183395`, `329/329 OK`, artifact `10939983025` | immutable — межа державних реєстрів і локального контролю документів |

Ревізії `10.4-r3 … r6` також залишаються історичними fast-test checkpoint-ами; їхні точні технічні записи збережені в Issue #61 та Git history. Уже виданий checkpoint не перевидається під тим самим номером.

Документи:
- [Release notes 10.5-r1](RELEASE_NOTES_v10_5_r1.md)
- [Release notes 10.4-r10](RELEASE_NOTES_v10_4_r10.md)
- [Release notes 10.4-r9](RELEASE_NOTES_v10_4_r9.md)

## Recent 10.3 checkpoints

| Tag | Статус | Ключова зміна |
|---|---|---|
| [v10.3-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3-r10) | Published; merged; manual Win7 Portable gate accepted | Windows 7 SP1 compatibility |
| [v10.3-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3-r9) | Full checkpoint; merged | Complete multi-platform packaging |
| [v10.3-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3-r8) | Published; merged | macOS Aqua-safe sidebar contrast |
| [v10.3-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3-r7) | Published; merged | Backup dialog + recovery protocol |
| [v10.3-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3-r6) | Published; stable promotion source | Legal/copyright checkpoint |

Документи:
- [Release notes 10.3](RELEASE_NOTES_v10_3.md)
- [Release notes 10.3-r10](RELEASE_NOTES_v10_3_r10.md)
- [Release notes 10.3-r9](RELEASE_NOTES_v10_3_r9.md)
- [Release notes 10.3-r8](RELEASE_NOTES_v10_3_r8.md)
- [Release notes 10.3-r7](RELEASE_NOTES_v10_3_r7.md)
- [Release notes 10.3-r6](RELEASE_NOTES_v10_3_r6.md)

## Stable line

| Tag | Статус | Призначення |
|---|---|---|
| [v10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) | **Current stable** | Promoted from manually tested 10.3 line; immutable |
| [v10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1) | Previous stable / rollback | Previous production checkpoint |
| [v10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0) | Previous stable / rollback | Verified 9.1 line promotion |
| [v9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1) | Historical stable | 9.0 hotfix |
| [v9.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0) | Historical stable | Baseline 9.x |

## Earlier candidate history

Історичні candidate tags/releases залишаються immutable і доступні у GitHub Releases. Ключові лінії:

- `v10.2-r1 … v10.2-r10` — vehicle documents, personnel planning, attestation/timesheet corrections;
- `v10.1-r1 … v10.1-r5` — driver-role separation, UI shell, reports/navigation fixes before stable 10.1;
- `v9.1-r5 … v9.1-r9.8` — planning, work regimes, canonical intervals, schedule audit, START hardening, duty staff;
- `v8.70*`, `v8.65`, `v8.64`, `v8.56` — historical 8.x checkpoints.

Не використовувати старі work/candidate branches як нову кодову базу. Для відновлення контексту читати `START_HERE.md`, `PROJECT_STATE.md`, `WORKLOG.md`, цей індекс і release notes потрібного checkpoint.

## Candidate numbering rule

- кожен завершений крок = нова ревізія `r1 … r10`;
- після `r10` — наступна minor-версія з `r1`;
- уже виданий candidate повторно не використовується;
- після виданого `10.5-r1` наступний кодовий крок — тільки **10.5-r2**;
- кожний fast-test checkpoint має окремий чистий START archive;
- при інтенсивній розробці START є основним тестовим пакетом; Portable/Setup формуються на більш рідкісних/повних checkpoint-ах.

## Release policy

1. Stable release формується тільки після manual operational gate та окремого рішення власника.
2. Candidate full checkpoint може мати повний multi-platform package set до stable promotion.
3. Старі tags/releases/checkpoint-и не пересуваються й не перезаписуються.
4. БД, SQLite, скани, кеші та персональні документи не публікуються.
5. Кодові зміни ведуться в окремій work branch через PR для merge у `main`.
6. «Злити у main» для релізного checkpoint означає: перевірки → пакети → tag/release → PR → merge → синхронізація документації.
