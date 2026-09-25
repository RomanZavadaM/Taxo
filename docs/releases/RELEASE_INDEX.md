# Індекс релізів Taxo

> Latest full checkpoint: **v10.4-r1** — modern Windows + Windows 7 SP1 + macOS ARM64/Intel + START; PR #71 merged; full publisher green.  
> Windows 7 compatibility checkpoint: **v10.3-r10** — Portable manual gate accepted on real Windows 7 x64; PR #70 merged.  
> Stable: **v10.3** (immutable; unchanged).  
> Next code revision: **10.4-r2**.

- [Taxo 10.4-r1](RELEASE_NOTES_v10_4_r1.md) — full multi-platform checkpoint with Windows 7 support.
- [Taxo 10.3-r10](RELEASE_NOTES_v10_3_r10.md) — Windows 7 SP1 x64 compatibility.
- [Taxo 10.3-r9](RELEASE_NOTES_v10_3_r9.md) — previous full multi-platform checkpoint.
- [Taxo 10.3-r8](RELEASE_NOTES_v10_3_r8.md) — macOS sidebar contrast / Aqua-safe navigation.
- [Taxo 10.3-r7](RELEASE_NOTES_v10_3_r7.md) — backup dialog + recovery protocol.
- [Taxo 10.3-r6](RELEASE_NOTES_v10_3_r6.md) — legal/copyright checkpoint.

# Taxo — індекс релізів

**Стан:** 25.09.2026  
**Поточна stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)  
**Previous stable / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1)

> Stable 10.1 промотовано після verified candidate v10.1-r5, ручного Windows UI/navigation gate та повторного stable regression: **162 tests / OK** на source, Windows і обох macOS architectures. Stable target: `fa5bbe0a5de733af1e227847ef9584daca57676e`. Stable 10.0 лишається rollback; старі tags/releases не пересуваються.

- [Release notes 10.3](RELEASE_NOTES_v10_3.md)

## Current candidate line 10.x

| Tag | Статус | Пакет | Призначення |
|---|---|---|---|
| [v10.4-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r1) | **Latest full checkpoint; merged** | Modern Windows Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START + SHA-256 | Full packaging with accepted Windows 7 support |
| [v10.3-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3-r10) | Published; merged; Win7 manual gate accepted | Windows 7 SP1 Setup/Portable, START + SHA-256 | Windows 7 compatibility fix |
| [v10.3-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3-r9) | Full checkpoint; merged | Windows Setup/Portable, macOS ARM64/Intel, START + SHA-256 | Accepted r8 state, complete multi-platform packaging |
| [v10.3-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3-r8) | Published prerelease; manual gate accepted | START/source + SHA-256 | Aqua-safe sidebar contrast |
| [v10.3-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3-r7) | Published prerelease; manual gate accepted | START/source + SHA-256 | Backup dialog footer + recovery protocol hardening |
| [v10.2-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.2-r4) | Published prerelease | START/source + SHA-256 | Replanning fix, timesheet/driver-role corrections, clean START package |
| [v10.1-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1-r5) | Final verified candidate before stable 10.1 | START/source + SHA-256 | Reports navigation loop fix + single-instance timesheet |
| [v10.1-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1-r4) | Previous immutable candidate | START/source + SHA-256 | Approved central-page UI polish + reports grouping |
| [v10.1-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1-r3) | Previous immutable candidate | START/source + SHA-256 | Approved application shell + exact logo artwork |
| [v10.1-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1-r2) | Previous immutable candidate | START/source + SHA-256 | First UI refresh, reports, About/Help |
| [v10.1-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1-r1) | Previous immutable candidate | START/source + SHA-256 | Driver-role separation fix + first UI refresh |

> Candidate line 10.1.x завершена stable релізом 10.1. Candidate tags лишаються immutable historical checkpoints.

## Candidate numbering rule

Поточне правило розробки: кожен завершений крок = нова ревізія; `r1 ... r10`, після `r10` — наступна minor-версія з `r1`. Уже виданий тестовий candidate не перевикористовується. Кожен крок завершується окремим START-архівом. Деталі: [../maintenance/DEVELOPMENT_RULES.md](../maintenance/DEVELOPMENT_RULES.md).

## Stable line

| Tag | Статус | Пакети | Призначення |
|---|---|---|---|
| [v10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) | **Stable** | Windows Setup/Portable, macOS ARM64/Intel, START, SHA-256 | Promoted from manually tested v10.3-r6 |
| [v10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1) | Previous stable / rollback | Windows Setup/Portable, macOS ARM64/Intel, START, SHA-256 | Previous production checkpoint |
| [v10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0) | Previous stable / rollback | Windows Setup/Portable, macOS ARM64/Intel, START, SHA-256 | Перевірена лінія 9.1 |
| [v9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1) | Previous stable / rollback | Windows Setup/Portable, macOS ARM64/Intel, START, SHA-256 | Hotfix 9.0 |
| [v9.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0) | Historical stable | Windows Setup/Portable, macOS ARM64/Intel, START, SHA-256 | Базовий stable 9.x |

## Candidate line 9.1

| Tag | Статус | Ключова зміна |
|---|---|---|
| [v9.1-r9.8](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.8) | Final verified candidate | duty staff = role + date + shift |
| [v9.1-r9.7](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.7) | Historical pre-release | «Відкрити деталізацію» місячного графіка |
| [v9.1-r9.6](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.6) | Historical pre-release | Windows-safe START.bat |
| [v9.1-r9.5](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.5) | Historical known-bad START | CMD parsing defect; не використовувати |
| [v9.1-r9.4](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.4) | Historical pre-release | «Аудит графіків…», П-5, архів, місячний контроль |
| [v9.1-r9.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.3) | Historical pre-release | П-5 та місячний контроль |
| [v9.1-r9.2](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.2) | Historical pre-release | відсутності та аудит |
| [v9.1-r9.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.1) | Historical pre-release | compatibility checkpoint |
| [v9.1-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9) | Historical pre-release | canonical exact intervals |
| [v9.1-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r8) | Historical pre-release | єдиний стан дня |
| [v9.1-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r7) | Historical pre-release | planning hardening |
| [v9.1-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r6) | Historical pre-release | work regimes |
| [v9.1-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r5) | Historical pre-release | early 9.1 operational candidate |

`v10.1-r1` … `v10.1-r5` — immutable prereleases/checkpoints, що передували stable 10.1.

## Historical 8.x Releases

- [v8.70-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70-r9)
- [v8.70-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70-r8)
- [v8.70](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70)
- [v8.65](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.65)
- [v8.64](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.64)
- [v8.56](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.56)

## Taxo 10.1 package set

Офіційний stable набір:
- `Taxo_v10_1_Setup_Windows_x64.exe`;
- `Taxo_v10_1_Windows_x64_Portable.zip`;
- `Taxo_v10_1_macOS_arm64_Portable.zip`;
- `Taxo_v10_1_macOS_x86_64_Portable.zip`;
- `Taxo_v10_1_START.zip`;
- per-platform і combined SHA-256 manifests.

Stable publisher успішно відпрацював з commit `fa5bbe0a5de733af1e227847ef9584daca57676e` у `main`; `v10.1` опубліковано як latest stable.

## Taxo 10.0 package set

Опубліковано:
- [Taxo_v10_0_Setup_Windows_x64.exe](https://github.com/RomanZavadaM/Taxo/releases/download/v10.0/Taxo_v10_0_Setup_Windows_x64.exe);
- [Taxo_v10_0_Windows_x64_Portable.zip](https://github.com/RomanZavadaM/Taxo/releases/download/v10.0/Taxo_v10_0_Windows_x64_Portable.zip);
- [Taxo_v10_0_macOS_arm64_Portable.zip](https://github.com/RomanZavadaM/Taxo/releases/download/v10.0/Taxo_v10_0_macOS_arm64_Portable.zip);
- [Taxo_v10_0_macOS_x86_64_Portable.zip](https://github.com/RomanZavadaM/Taxo/releases/download/v10.0/Taxo_v10_0_macOS_x86_64_Portable.zip);
- [Taxo_v10_0_START.zip](https://github.com/RomanZavadaM/Taxo/releases/download/v10.0/Taxo_v10_0_START.zip);
- per-platform SHA-256 manifests;
- [SHA256SUMS_v10_0.txt](https://github.com/RomanZavadaM/Taxo/releases/download/v10.0/SHA256SUMS_v10_0.txt).

Release target: `91c0d6365a40eb09fe40f97a2965da40b314bc15`. Stable publisher — success; Windows/macOS/source regression suites — 117 tests / OK.

## Release policy

1. Stable release формується тільки після manual operational gate.
2. Stable executable artifacts будуються з commit у `main`.
3. Старі tags/releases не пересуваються й не перезаписуються.
4. БД, SQLite, скани, кеші та персональні документи не публікуються.
5. Нові зміни після 10.1 ведуться в окремій work branch через PR.
6. Кожна нова release-контрольна точка отримує новий tag.

Документи:
- [Release notes 10.1](RELEASE_NOTES_v10_1.md)
- [Фінальний аудит 10.1](../maintenance/AUDIT_v10_1_STABLE.md)
- [Release notes 10.1-r5](RELEASE_NOTES_v10_1_r5.md)
- [Release notes 10.1-r4](RELEASE_NOTES_v10_1_r4.md)
- [Release notes 10.1-r3](RELEASE_NOTES_v10_1_r3.md)
- [Release notes 10.1-r2](RELEASE_NOTES_v10_1_r2.md)
- [Release notes 10.1-r1](RELEASE_NOTES_v10_1_r1.md)
- [Release notes 10.0](RELEASE_NOTES_v10_0.md)
- [Фінальний аудит 10.0](../maintenance/AUDIT_v10_0_STABLE.md)
