# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md)

**Taxo — настільна система для одного автотранспортного підприємства: водії й персонал, графіки, табелі, шляхові листи, бланки підтвердження діяльності, транспорт, документи, звіти та вибірковий контроль аналогових тахокарт.**

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) — чинна stable-лінія.  
> **Latest full checkpoint in `main`:** [Taxo 10.5-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8) — повний multi-platform candidate/checkpoint.  
> **Previous stable / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.5-r8` не стає stable автоматично; stable promotion — окреме рішення власника.

## Завантаження 10.5-r8

[Windows x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Setup_Windows_x64.exe) · [Windows x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Windows7_x64_Portable.zip) · [macOS ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_macOS_arm64_Portable.zip) · [macOS Intel](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_macOS_x86_64_Portable.zip) · [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/SHA256SUMS_v10_5_r8.txt)

Для звичайної експлуатації використовуйте готовий Windows/macOS пакет. `START.bat` призначений насамперед для тестування й технічної діагностики; START ZIP спочатку потрібно повністю розпакувати.

Робочі БД, SQLite, скани, кеші та персональні документи у GitHub releases **не входять**.

## Основний функціонал

- реєстр працівників і водіїв із ролями та історією;
- індивідуальні й періодичні графіки водіїв;
- табель робочого часу з розділенням плану й факту та підтримкою поділених змін;
- контроль робочого часу, керування, перерв і відпочинку;
- окремі тижневі баланси **60:00 робочого часу** і **56:00 керування**;
- 60-денний похвилинний реєстр діяльності;
- транспортні засоби, пробіг і реєстр документів ТЗ;
- страховка, ДЦВ, техконтроль, техпаспорт, тимчасова реєстрація, протокол тахографа; кілька активних документів одного типу та ручне архівування;
- маршрути й часові сценарії;
- шляхові листи з маршрутом, серією/номером, спідометром, пробігом і реквізитами підприємства;
- бланки підтвердження діяльності DOCX/PDF/JPG з ревізіями та архівом;
- аналогові тахокарти: скани, інтервали, ручне підтвердження, протоколи;
- PDF/Excel звіти;
- резервні копії та перенесення робочого сховища.

## Реєстри та військовий облік — 10.5

Лінія 10.5 додала:

- покомпонентну звірку ТЗ з даними «Шлях»;
- редаговані робочі значення окремо від immutable державних snapshots;
- єдиний реєстр документів працівників;
- lossless імпорт державних XLSX працівників;
- відомість військово-транспортного обліку підприємства по власному/балансовому транспорту;
- локальний цикл щорічного звіряння персонального військового обліку через Дію.

Taxo **не підміняє державні сервіси**: локальна підготовка не вважається офіційним фактом, а програма не заявляє автоматичного надсилання даних до Дії, «Оберіг» чи «Шлях».

## Що виправлено в 10.5-r8

Windows 7 / Python 3.8 може повертати коротку openpyxl-помилку `unexpected keyword argument 'tabId'` без слова `ChildSheet`. r8 коректно розпізнає цей випадок, виконує вузький in-memory compatibility retry і не змінює вихідний XLSX.

Повні release notes: [10.5-r8](docs/releases/RELEASE_NOTES_v10_5_r8.md).

## Документація

- [Огляд документації](docs/README.md)
- [Огляд системи](docs/SYSTEM_OVERVIEW.md)
- [Швидкий старт](docs/guides/QUICK_START.md)
- [Інструкція для персоналу](docs/guides/USER_MANUAL.md)
- [Робота з тахографом](docs/guides/TACHOGRAPH_GUIDE.md)
- [Звіти](docs/guides/REPORTS_GUIDE.md)
- [Адміністрування і резервні копії](docs/guides/ADMIN_GUIDE.md)
- [Типові проблеми](docs/guides/TROUBLESHOOTING.md)
- [Індекс релізів](docs/releases/RELEASE_INDEX.md)

## Розробка й відновлення контексту

Перед новою робочою сесією читати `START_HERE.md`, далі `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` та Issue #61.

Правило candidate-версій: кожен завершений крок = нова ревізія `r1 … r10`; після `r10` піднімається minor-версія й цикл починається з `r1`. Уже видані revision не перевикористовуються.

Після `10.5-r8` наступна кодова ревізія — **10.5-r9**.

## Дані та безпека

Програма й робочі дані розділені. Оновлення програми не повинно вимагати повторного введення робочої бази. Перед масовими змінами, оновленням або перенесенням робочого сховища робіть резервну копію.

Планові дані не оголошуються фактом без явного підтвердження. Якщо джерел недостатньо, Taxo має показувати невизначеність, а не домальовувати факт.

## Авторські права та ліцензія

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.**

Taxo є **proprietary software**. Публічна видимість репозиторію не надає open-source ліцензії та не означає дозволу на перепублікацію, розповсюдження, продаж або створення похідних версій без письмового дозволу правовласника.

Назва підприємства, введена в Taxo, є робочим реквізитом і не змінює правовласника програми.

Повні умови:
- [LICENSE.md](LICENSE.md)
- [COPYRIGHT.md](COPYRIGHT.md)
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- [Авторські права та ліцензія](docs/LEGAL_AND_COPYRIGHT.md)
