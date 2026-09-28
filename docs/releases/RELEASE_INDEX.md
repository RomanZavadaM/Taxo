# Індекс релізів Taxo

**Стан:** 28.09.2026  
**Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) — immutable  
**Latest full checkpoint in `main`:** [Taxo 10.5-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8) — merged  
**Next code revision:** **10.5-r9**.

> `v10.5-r8` — повний multi-platform candidate/checkpoint. Він не підміняє stable `v10.3` без окремого рішення власника про stable promotion.

## Full checkpoints

| Tag | Статус | Пакети | Основний зміст |
|---|---|---|---|
| [v10.5-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8) | **Latest full checkpoint; merged via PR #76** | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, SHA-256 | Windows 7/Python 3.8 XLSX `tabId` compatibility + вся функціональність r7 |
| [v10.4-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r2) | Previous full checkpoint | Windows x64, Windows 7 SP1, macOS ARM64/Intel, START, SHA-256 | UI cleanup, документи ТЗ, ДЦВ, шляховий лист, Win7 gate |
| [v10.4-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r1) | Historical full checkpoint | Windows x64, Windows 7 SP1, macOS ARM64/Intel, START, SHA-256 | перший повний 10.4 checkpoint із Win7 support |

## Taxo 10.5 history

| Ревізія | Issued source | Перевірка | Зміст |
|---|---|---|---|
| **10.5-r8** | `846e5c5111b14a4a1f2e49203803e86c495b458f` | `483/483 OK`; release workflow `36406419955` | full checkpoint; Win7/Python 3.8 `tabId` compatibility; merged in PR #76 |
| 10.5-r7 | `19a9f462993767a43ca3d5add8c7afabcbd39a96` | `476/476 OK`; START run `36396485974` | локальний цикл звіряння через Дію: отримання → актуалізація → зовнішня фіксація |
| 10.5-r6 | `5f6c7643ce63bffb8069de9775194322a71f13df` | `465/465 OK` | редаговані робочі дані Дія/«Оберіг» і «Шлях» окремо від immutable snapshots |
| 10.5-r5 | `23064b775087c9dfc05867dc65f27e6d6d87e9b4` | `456/456 OK` | in-memory compatibility retry для XLSX «Шлях» / `ChildSheet/tabId` |
| 10.5-r4 | `117b305b048c2588e21d7908f39a3bb1071f74aa` | success | lossless raw snapshot державних XLSX працівників |
| 10.5-r3 | `ca1a1288f915c3fa0eb57c82a3e91aea3b0887d1` | `440/440 OK` | єдиний реєстр документів працівників |
| 10.5-r2 | `d9e7beefa52c7774e1b4bd6711dfc5907e06de37` | `425/425 OK` | покомпонентна звірка ТЗ з «Шлях» |
| 10.5-r1 | `d7e5a730767ebc17e6935b2d3f25208a9f151c16` | `399/399 OK` | відомість військово-транспортного обліку підприємства |

Усі видані revision/checkpoint-и immutable. Після `10.5-r8` наступна кодова ревізія — тільки **10.5-r9**.

## Historical identity anchors

- **Taxo 10.4-r7** — issued source `9f397a092fe828570927bc39cef7a3a467e2aff0`; immutable historical checkpoint розділення державних реєстрів і локального контролю документів. Деталі збережені в Git history, release notes та Issue #61.

## Документи поточної лінії

- [Release notes 10.5-r8](RELEASE_NOTES_v10_5_r8.md)
- [Release notes 10.5-r7](RELEASE_NOTES_v10_5_r7.md)
- [Release notes 10.5-r6](RELEASE_NOTES_v10_5_r6.md)
- [Release notes 10.5-r5](RELEASE_NOTES_v10_5_r5.md)
- [Release notes 10.5-r4](RELEASE_NOTES_v10_5_r4.md)
- [Release notes 10.5-r3](RELEASE_NOTES_v10_5_r3.md)
- [Release notes 10.5-r2](RELEASE_NOTES_v10_5_r2.md)
- [Release notes 10.5-r1](RELEASE_NOTES_v10_5_r1.md)

Точні технічні записи старіших fast-test revision збережені в Git history, release notes та Issue #61. Старі work/candidate branches не використовуються як нова кодова база.

## Stable line

| Tag | Статус | Призначення |
|---|---|---|
| [v10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) | **Current stable** | чинна stable-лінія до окремого рішення про promotion |
| [v10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1) | Previous stable / rollback | попередній production checkpoint |
| [v10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0) | Historical stable | промоція перевіреної 9.1-лінії |
| [v9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1) | Historical stable | 9.0 hotfix |

## Candidate numbering rule

- кожен завершений крок = нова ревізія `r1 … r10`;
- після `r10` — наступна minor-версія з `r1`;
- вже виданий candidate/release не пересувається і не перевидається;
- кожний fast-test checkpoint має окремий чистий START archive;
- при інтенсивній розробці START є основним тестовим пакетом; повні Setup/Portable збірки формуються на full checkpoints.

## Release policy

1. Stable формується тільки після manual operational gate та окремого рішення власника.
2. Full candidate checkpoint може мати повний multi-platform package set до stable promotion.
3. БД, SQLite, скани, кеші та персональні документи не публікуються.
4. Кодові зміни йдуть через окрему work branch і PR.
5. «Злити у main» = перевірки → пакети → tag/release → PR → merge → синхронізація документації та Issue #61.
