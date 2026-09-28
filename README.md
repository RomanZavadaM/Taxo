# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md)

**Taxo — настільна система для одного автотранспортного підприємства: водії й персонал, графіки, табелі, шляхові листи, бланки підтвердження діяльності, транспорт, документи, звіти та вибірковий контроль аналогових тахокарт.**

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) — чинна stable-лінія.  
> **Latest full checkpoint in `main`:** [Taxo 10.6-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3) — повний multi-platform candidate/checkpoint.  
> **Previous stable / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.6-r3` не стає stable автоматично; stable promotion — окреме рішення власника.

## Завантаження 10.6-r3

[Windows x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Setup_Windows_x64.exe) · [Windows x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Windows7_x64_Portable.zip) · [macOS ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_macOS_arm64_Portable.zip) · [macOS Intel](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_macOS_x86_64_Portable.zip) · [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/SHA256SUMS_v10_6_r3_FULL.txt)

Для звичайної експлуатації використовуйте готовий Windows/macOS пакет. `START.bat` призначений насамперед для тестування й технічної діагностики; START ZIP спочатку потрібно повністю розпакувати.

Робочі БД, SQLite, скани, кеші та персональні документи у GitHub releases **не входять**.

## Основний функціонал

- реєстр працівників і водіїв із ролями та історією;
- індивідуальні й періодичні графіки водіїв;
- табель робочого часу з чітким розділенням плану й факту та підтримкою поділених змін;
- контроль робочого часу, керування, перерв і відпочинку;
- окремі тижневі баланси **60:00 робочого часу** і **56:00 керування**;
- 60-денний похвилинний реєстр діяльності;
- транспортні засоби, пробіг і реєстр документів ТЗ;
- страховка, ДЦВ, техконтроль, техпаспорт, тимчасова реєстрація, протокол тахографа; кілька активних документів одного типу та ручне архівування;
- маршрути, часові сценарії та нерегулярні виїзди;
- шляхові листи для регулярних маршрутів, замовлень, розвозок, міських, обласних, міжобласних та інших разових поїздок;
- бланки підтвердження діяльності DOCX/PDF/JPG з ревізіями та архівом;
- аналогові тахокарти: скани, інтервали, ручне підтвердження, протоколи;
- PDF/Excel звіти;
- резервні копії та перенесення робочого сховища.

## Що увійшло до checkpoint 10.6-r3

- аудит дня не змішує історичний/перепланований план із поточним шаблоном маршруту;
- у реєстрі документів ТЗ неактивні автомобілі приховані за замовчуванням, але можуть бути показані прапорцем;
- шляхівка може формуватися без регулярного `route_id`: для замовлень, розвозок, поїздок по місту/області/між областями та інших разових робіт;
- для нерегулярної поїздки час береться з графіка водія, автобус можна вибрати при видачі, опис поїздки редагується; типове значення — «по області»;
- зворот нерегулярної шляхівки не отримує фіктивного маршрутного розкладу, але зберігає лікаря, механіка, спідометр і фактичний пробіг, якщо ці дані реально є в Taxo;
- вікно «Про програму» адаптоване до невисоких/масштабованих екранів;
- межа **plan ≠ fact** і тахографічний облік не змінені.

Повні release notes: [10.6-r3](docs/releases/RELEASE_NOTES_v10_6_r3.md).

## Реєстри та військовий облік

Taxo підтримує звірку ТЗ з даними «Шлях», редаговані робочі значення окремо від immutable державних snapshots, єдиний реєстр документів працівників, lossless імпорт державних XLSX, відомість військово-транспортного обліку підприємства та локальний цикл щорічного звіряння персонального військового обліку через Дію.

Taxo **не підміняє державні сервіси**: локальна підготовка не вважається офіційним фактом, а програма не заявляє автоматичного надсилання даних до Дії, «Оберіг» чи «Шлях».

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

Правило candidate-версій: кожен завершений крок = нова ревізія `r1 … r10`; після `r10` піднімається minor-версія й цикл починається з `r1`. Уже видані revision не перевикористовуються. Після `10.6-r3` наступна кодова ревізія — **10.6-r4**.

## Дані та безпека

Програма й робочі дані розділені. Оновлення програми не повинно вимагати повторного введення робочої бази. Планові дані не оголошуються фактом без явного підтвердження.

## Авторські права та ліцензія

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.**

Taxo є **proprietary software**. Публічна видимість репозиторію не надає open-source ліцензії та не означає дозволу на перепублікацію, розповсюдження, продаж або створення похідних версій без письмового дозволу правовласника.

Повні умови: [LICENSE.md](LICENSE.md) · [COPYRIGHT.md](COPYRIGHT.md) · [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) · [Авторські права та ліцензія](docs/LEGAL_AND_COPYRIGHT.md)
