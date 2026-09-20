# Taxo — індекс релізів

**Стан:** 20.09.2026  
**Поточна stable:** [Taxo 10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0)  
**Previous stable / rollback:** [Taxo 9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1)

> Stable 10.0 опублікований з commit `91c0d6365a40eb09fe40f97a2965da40b314bc15` після завершеного manual operational gate. Старі tags/releases не пересуваються.

## Current candidate line 10.x

| Tag | Статус | Пакет | Призначення |
|---|---|---|---|
| v10.1-r3 | Current candidate / pending publish | START/source + SHA-256 | Approved application shell + exact logo artwork |\n| [v10.1-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1-r2) | Previous immutable candidate | START/source + SHA-256 | First UI refresh, reports, About/Help |
| [v10.1-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1-r1) | Previous immutable candidate | START/source + SHA-256 | Driver-role separation fix + first UI refresh |

> Candidate 10.1.x не замінює stable 10.0 до manual operational gate. Старі tags/releases не пересуваються.

## Stable line

| Tag | Статус | Пакети | Призначення |
|---|---|---|---|
| [v10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0) | **Stable** | Windows Setup/Portable, macOS ARM64/Intel, START, SHA-256 | Перевірена лінія 9.1, промотована в stable |
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

`r1–r4` не публікувалися окремими Releases: це проміжні Git-стани з відомими виправленими проблемами.

## Historical 8.x Releases

- [v8.70-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70-r9)
- [v8.70-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70-r8)
- [v8.70](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70)
- [v8.65](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.65)
- [v8.64](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.64)
- [v8.56](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.56)

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
5. Нові зміни після 10.0 ведуться в окремій work branch через PR.
6. Кожна нова release-контрольна точка отримує новий tag.

Документи:
- [Release notes 10.1-r3](RELEASE_NOTES_v10_1_r3.md)\n- [Release notes 10.1-r2](RELEASE_NOTES_v10_1_r2.md)
- [Release notes 10.1-r1](RELEASE_NOTES_v10_1_r1.md)
- [Release notes 10.0](RELEASE_NOTES_v10_0.md)
- [Фінальний аудит 10.0](../maintenance/AUDIT_v10_0_STABLE.md)
