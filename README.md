# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

**Taxo — настільна система для одного автотранспортного підприємства: водії й персонал, графіки, табелі, шляхові листи, бланки підтвердження діяльності, транспорт, документи, звіти та вибірковий контроль аналогових тахокарт.**

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) — чинна stable-лінія.  
> **Latest integrated checkpoint in `main`:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9).  
> **Latest full multi-platform checkpoint:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9).  
> **Previous stable / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.9-r9` не стає stable автоматично; stable promotion — окреме рішення власника.

## Завантаження 10.9-r9

**Windows:** [x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows_x64.exe) · [x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows7_x64_Portable.zip)

**macOS:** [ARM64 / Apple Silicon](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_x86_64_Portable.zip)

**Тестування/діагностика:** [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [Release 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9) · [Release notes](docs/releases/RELEASE_NOTES_v10.9-r9.md)

Для звичайної експлуатації використовуйте готовий Windows/macOS пакет. `START.bat` призначений насамперед для тестування й технічної діагностики; START ZIP спочатку потрібно повністю розпакувати.

Робочі БД, SQLite, скани, кеші та персональні документи у GitHub releases **не входять**.

## Основний функціонал

- реєстр працівників і водіїв із ролями та історією;
- індивідуальні й періодичні графіки водіїв;
- табель робочого часу з чітким розділенням плану й факту та підтримкою поділених змін;
- контроль робочого часу, керування, перерв і відпочинку;
- 60-денний похвилинний реєстр діяльності без вигадування відпочинку з невідомого часу;
- транспортні засоби, пробіг, СТОІР і реєстр документів ТЗ;
- страховка, ДЦВ, техконтроль, техпаспорт, тимчасова реєстрація, протокол тахографа; кілька активних документів одного типу та ручне архівування;
- маршрути, часові сценарії та нерегулярні виїзди;
- шляхові листи для регулярних маршрутів і нерегулярної роботи;
- бланки підтвердження діяльності DOCX/PDF/JPG з ревізіями та архівом;
- аналогові тахокарти: скани, інтервали, ручне підтвердження, протоколи;
- накази та закріплення водій→ТЗ із захистом затвердженої/підписаної історії;
- PDF/Excel звіти;
- резервні копії, перенесення робочого сховища та контроль сумісності схеми SQLite.

## Що інтегровано в 10.9-r2 → 10.9-r9

- захист історії виданих шляхівок і номерів від повторного використання;
- перевірка чинності документів ТЗ на весь період рейсу;
- посилений контроль робочого часу/відпочинку, overlaps, boundary gaps, 3+9 і двотижневий контроль;
- безпечний пріоритет фактичних джерел у 60-денному реєстрі;
- коректні історичні межі працевлаштування, П-5 та цикли 2/2 і 3/3;
- надійніша хронологія одометра й прогноз ТО;
- immutable затверджені/підписані накази та безпечні закріплення водій→ТЗ;
- explicit SQLite schema baseline через `PRAGMA user_version` і future-schema guard від r9.

Повні release notes: [10.9-r9](docs/releases/RELEASE_NOTES_v10.9-r9.md) · [індекс релізів](docs/releases/RELEASE_INDEX.md).

## Реєстри та військовий облік

Taxo підтримує звірку ТЗ з даними «Шлях», редаговані робочі значення окремо від immutable державних snapshots, єдиний реєстр документів працівників, lossless імпорт державних XLSX, відомість військово-транспортного обліку підприємства та локальний цикл щорічного звіряння персонального військового обліку через Дію.

Taxo **не підміняє державні сервіси**: локальна підготовка не вважається офіційним фактом, а програма не заявляє автоматичного надсилання даних до Дії, «Оберіг» чи «Шлях».

## Документація

[Огляд документації](docs/README.md) · [Огляд системи](docs/SYSTEM_OVERVIEW.md) · [Поточний стан продукту](docs/PRODUCT_STATUS.md) · [Швидкий старт](docs/guides/QUICK_START.md) · [Інструкція для персоналу](docs/guides/USER_MANUAL.md) · [Індекс релізів](docs/releases/RELEASE_INDEX.md)

## Розробка й відновлення контексту

Перед новою робочою сесією читати `START_HERE.md`, далі `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` та Issue #61.

Правило candidate-версій: кожен завершений **кодовий** крок = нова ревізія `r1 … r10`; після `r10` піднімається minor-версія й цикл починається з `r1`. Уже видані revision не перевикористовуються. Після `10.9-r9` наступна кодова ревізія — **10.9-r10**.

## Авторські права та ліцензія

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.**

Taxo є **proprietary software**. Публічна видимість репозиторію не надає open-source ліцензії та не означає дозволу на перепублікацію, розповсюдження, продаж або створення похідних версій без письмового дозволу правовласника.

Повні умови: [LICENSE.md](LICENSE.md) · [COPYRIGHT.md](COPYRIGHT.md) · [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) · [Авторські права та ліцензія](docs/LEGAL_AND_COPYRIGHT.md)
