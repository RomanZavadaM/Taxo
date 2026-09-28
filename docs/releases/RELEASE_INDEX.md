# Індекс релізів Taxo

**Стан:** 28.09.2026  
**Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) — immutable  
**Latest full checkpoint in `main`:** [Taxo 10.6-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3) — merged via PR #84  
**Next code revision:** **10.6-r4**.

> `v10.6-r3` — поточний повний multi-platform checkpoint у `main`. Він не підміняє stable `v10.3`: stable promotion відбувається тільки за окремим рішенням власника.

## Full checkpoints

| Tag | Статус | Пакети | Основний зміст |
|---|---|---|---|
| [v10.6-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3) | **Latest full checkpoint; merged via PR #84** | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, platform/full SHA-256 | plan/fact audit; нерегулярні шляхівки; default-on фільтр неактивних ТЗ; адаптивне «Про програму»; збереження лікаря/механіка/спідометра/пробігу на звороті нерегулярної шляхівки |
| [v10.5-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8) | Previous full checkpoint | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, SHA-256 | Windows 7/Python 3.8 XLSX `tabId` compatibility + функціональність r7 |
| [v10.4-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r2) | Historical full checkpoint | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, SHA-256 | UI cleanup, документи ТЗ, ДЦВ, шляховий лист, Win7 gate |
| [v10.4-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r1) | Historical full checkpoint | Windows x64, Windows 7 SP1, macOS ARM64/Intel, START, SHA-256 | перший повний 10.4 checkpoint із Win7 support |

## Taxo 10.6 history

| Ревізія | Issued source | Перевірка | Зміст |
|---|---|---|---|
| **10.6-r3** | `97e646936d14d163faf93882daf7894f5bb38ab6` | `530/530 OK`; START `36434131185`; full assets `36440880324`; PR gates `36441149032` / `36441148816` | full main checkpoint; лікар/механік, спідометр і фактичний пробіг більше не очищаються разом із маршрутним розкладом нерегулярної шляхівки |
| 10.6-r2 | `4d976bc7686015c00a3af5387634e8486cefc48b` | `519/519 OK`; START `36428981516`; publisher `36429169682` | нерегулярні поїздки без обов'язкового route_id: замовлення/розвозки/місто/область/міжобласні; вибір автобуса; час з графіка; blank reverse; адаптивне «Про програму» |
| 10.6-r1 | `e4823947d3c5d28af54fd4337bdaf0daf02b4201` | `507/507 OK`; START `36420768488`; publisher `36420943804` | неактивні автомобілі приховані за замовчуванням у реєстрі документів ТЗ; прапорець повертає весь парк |

## Taxo 10.5 history

| Ревізія | Issued source | Перевірка | Зміст |
|---|---|---|---|
| **10.5-r10** | `91a528ba92a56a8e1a399c8c114254f05798b5c7` | `499/499 OK`; START `36416851443` | аудит дня більше не змішує збережений план дня з поточним шаблоном маршруту; fact не переписується |
| 10.5-r9 | `3356ae224f47cffeb74e5b10709b808071222eae` | `493/493 OK`; release workflow `36413453352` | базовий механізм шляхівки без регулярного маршруту: час з графіка, редагований опис, blank reverse |
| **10.5-r8** | `846e5c5111b14a4a1f2e49203803e86c495b458f` | `483/483 OK`; release `36406419955` | previous full checkpoint; Win7/Python 3.8 `tabId` compatibility; merged via PR #76 |
| 10.5-r7 | `19a9f462993767a43ca3d5add8c7afabcbd39a96` | `476/476 OK`; START `36396485974` | локальний цикл звіряння через Дію: отримання → актуалізація → зовнішня фіксація |
| 10.5-r6 | `5f6c7643ce63bffb8069de9775194322a71f13df` | `465/465 OK` | редаговані робочі дані Дія/«Оберіг» і «Шлях» окремо від immutable snapshots |
| 10.5-r5 | `23064b775087c9dfc05867dc65f27e6d6d87e9b4` | `456/456 OK` | in-memory compatibility retry для XLSX «Шлях» / `ChildSheet/tabId` |
| 10.5-r4 | `117b305b048c2588e21d7908f39a3bb1071f74aa` | success | lossless raw snapshot державних XLSX працівників |
| 10.5-r3 | `ca1a1288f915c3fa0eb57c82a3e91aea3b0887d1` | `440/440 OK` | єдиний реєстр документів працівників |
| 10.5-r2 | `d9e7beefa52c7774e1b4bd6711dfc5907e06de37` | `425/425 OK` | покомпонентна звірка ТЗ з «Шлях» |
| 10.5-r1 | `d7e5a730767ebc17e6935b2d3f25208a9f151c16` | `399/399 OK` | відомість військово-транспортного обліку підприємства |

Усі видані revision/checkpoint-и immutable. Після `10.6-r3` наступна кодова ревізія — тільки **10.6-r4**.

## Stable line

| Tag | Статус | Призначення |
|---|---|---|
| [v10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) | **Current stable** | чинна stable-лінія до окремого рішення про promotion |
| [v10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1) | Previous stable / rollback | попередній production checkpoint |
| [v10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0) | Historical stable | промоція перевіреної 9.1-лінії |
| [v9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1) | Historical stable | 9.0 hotfix |

## Документи поточної лінії

- [Release notes 10.6-r3](RELEASE_NOTES_v10_6_r3.md)
- [Release notes 10.6-r2](RELEASE_NOTES_v10_6_r2.md)
- [Release notes 10.6-r1](RELEASE_NOTES_v10_6_r1.md)
- [Release notes 10.5-r10](RELEASE_NOTES_v10_5_r10.md)
- [Release notes 10.5-r8](RELEASE_NOTES_v10_5_r8.md)

Точні технічні записи старіших revision збережені в Git history, release notes та Issue #61. Старі work/candidate branches не використовуються як нова кодова база.

## Release policy

1. Stable формується тільки після manual operational gate та окремого рішення власника.
2. Full candidate checkpoint має повний multi-platform package set.
3. БД, SQLite, скани, кеші та персональні документи не публікуються.
4. Кодові зміни йдуть через окрему work branch і PR.
5. «Злити у main» = перевірки → повні пакети → tag/release → PR → merge → синхронізація документації та Issue #61.
