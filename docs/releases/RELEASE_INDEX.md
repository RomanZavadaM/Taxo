# Індекс релізів Taxo

**Стан:** 27.09.2026  
**Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) — immutable  
**Latest full checkpoint:** [Taxo 10.4-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r2)  
**Next code revision:** **10.4-r3**.

> `v10.4-r2` опубліковано з exact target `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`; full publisher `36275440403` — success; PR #74 merged у `main` як `271d43c0912e24c95014ac2a92ba2fc1695f4a11`. Stable `v10.3` не пересувався.

## Current candidate line 10.4

| Tag | Статус | Пакети | Призначення |
|---|---|---|---|
| [v10.4-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r2) | **Latest full checkpoint; merged** | Modern Windows Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START + SHA-256 | UI remediation, vehicle docs, waybill readability, reusable Win7 PE gate |
| [v10.4-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r1) | Previous full checkpoint; merged | Modern Windows Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START + SHA-256 | First full 10.4 checkpoint with accepted Windows 7 support |

Документи:
- [Release notes 10.4-r2](RELEASE_NOTES_v10_4_r2.md)
- [Release notes 10.4-r1](RELEASE_NOTES_v10_4_r1.md)

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

Історичні candidate tags лишаються immutable і доступні у GitHub Releases. Ключові лінії:

- `v10.2-r1 … v10.2-r10` — vehicle documents, personnel planning, attestation/timesheet corrections;
- `v10.1-r1 … v10.1-r5` — driver-role separation, UI shell, reports/navigation fixes before stable 10.1;
- `v9.1-r5 … v9.1-r9.8` — planning, work regimes, canonical intervals, schedule audit, START hardening, duty staff;
- `v8.70*`, `v8.65`, `v8.64`, `v8.56` — historical 8.x checkpoints.

Не використовувати старі work/candidate branches як нову кодову базу. Для відновлення контексту достатньо `START_HERE.md`, `PROJECT_STATE.md`, `WORKLOG.md` та release notes потрібного tag.

## Candidate numbering rule

- кожен завершений крок = нова ревізія `r1 … r10`;
- після `r10` — наступна minor-версія з `r1`;
- уже виданий candidate повторно не використовується;
- після виданого `10.4-r2` наступний кодовий крок — тільки **10.4-r3**;
- кожний test checkpoint має окремий чистий START archive.

## Release policy

1. Stable release формується тільки після manual operational gate та окремого рішення власника.
2. Candidate checkpoint може мати повний multi-platform package set до stable promotion.
3. Старі tags/releases не пересуваються й не перезаписуються.
4. БД, SQLite, скани, кеші та персональні документи не публікуються.
5. Кодові зміни ведуться в окремій work branch через PR.
6. «Злити у main» для релізного checkpoint означає: перевірки → пакети → tag/release → PR → merge → синхронізація документації.
