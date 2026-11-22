# Taxo / Driver Worktime

🇺🇦 [Українська](README.md) · 🇬🇧 [English](docs/i18n/README.en.md) · 🇩🇪 [Deutsch](docs/i18n/README.de.md) · 🇪🇸 [Español](docs/i18n/README.es.md) · 🇫🇷 [Français](docs/i18n/README.fr.md) · 🇰🇷 [한국어](docs/i18n/README.ko.md) · 🇯🇵 [日本語](docs/i18n/README.ja.md)

**Taxo — настільна система для роботи автотранспортного підприємства:** працівники й транспорт, графіки та робочий час, шляхові листи, накази, документи, технічне обслуговування, звіти й резервування.

## Можливості

- **Працівники та документи.** Картки персоналу й водіїв, ролі, документи, строки дії та контроль локальних вкладень.
- **Графіки та робочий час.** Планування змін і маршрутів, табель, окремий план і факт, поділені зміни та місячні підсумки.
- **Контроль водія.** Робота, керування, перерви й відпочинок, звіти та 60-денний реєстр діяльності.
- **Транспорт і СТОІР.** Картки ТЗ, пробіг, документи, технічне обслуговування, ремонти та контроль готовності.
- **Експлуатація.** Шляхові листи, накази, закріплення водій–ТЗ, учасники наказів, DOCX/PDF/JPG, перегляд і друк.
- **Документи.** Власні шаблони, контрольовані Word-редакції, PDF/друк, сховище готових документів, скани паперових оригіналів, окрема відмітка паперового підпису, фільтри та власні папки.
- **Інструктажі й стажування.** Редаговані програми, відомості підписів, листи стажування та каталог створених документів.
- **Тахограф, звіти й резервування.** Аналогові тахокарти з ручною перевіркою, PDF/Excel-звіти та резервні копії робочого сховища.

Докладніше: [огляд системи](docs/SYSTEM_OVERVIEW.md) · [посібник користувача](docs/guides/USER_MANUAL.md) · [експлуатація та СТОІР](docs/guides/OPERATIONS_STOIR_GUIDE.md).

## Стабільна 10.23-r4

**10.23-r4 прийнята власником 20.11.2026 і є Stable/Latest.** Вона включає зміни r1–r4:

- **Документи:** пошук, фільтри, сортування, дерево за видами/датами, власні вкладені папки без дублювання файлів, скани й паперовий підпис; робочу область бланків та ширину дерева каталогу можна регулювати.
- **Накази:** явні пари водій–ТЗ, редагування наявних пар, редагування ролі/примітки учасника, накопичення вибору при пошуку, тема активного наказу та прямий перехід до закріплень.
- **Перегляд наказу:** кнопки DOCX/PDF/JPG і нижні дії адаптовані до вузького вікна; виправлено випадок, коли при 760×560 блок форматів міг бути витіснений за межі екрана.
- **Захист від втрати функцій:** 37 суворих live-маршрутів із перевіркою mapped / onscreen / usable / activation. START, Windows, Windows 7 і macOS Intel/ARM пройшли перевірки; Windows/Win7 — також Defender та integrity.

Ручне приймання саме 10.23-r4 виконано. Загальний аудит повного покриття всіх функцій (#556) і ширший наскрізний контроль механізму наказів (#553) залишаються відкритими; реєстрація вхідної/вихідної кореспонденції ще запланована.

### Test 10.24-r1

[Taxo 10.24-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r1) — поточний Test prerelease, 8 файлів, exact source `adb6ae40e966d77018c6dc8c1c4fdcbde6a6a827`. r1 додає окремий реєстр ділової кореспонденції: два журнали Вх./Вих., незалежну безпечну нумерацію, окремі дати, кореспондента/тему/контроль, response links та посилання на готові документи без копіювання байтів. Реєстр входить у full workspace backup/restore. UI, вкладення та автоматична пошта ще не реалізовані; Stable/Latest лишається 10.23-r4.


## Завантаження

**Stable / Latest: [Taxo 10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4).** Попередня стабільна точка: [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1).

- **Windows 10/11 x64:** [інсталятор](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_Setup_Windows_x64.exe) · [portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_Windows_x64_Portable.zip)
- **Windows 7 SP1 x64:** [інсталятор](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_Setup_Windows7_x64.exe) · [portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_Windows7_x64_Portable.zip)
- **macOS:** [Apple Silicon](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_macOS_arm64_Portable.zip) · [Intel](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_macOS_x86_64_Portable.zip)
- **Вихідний пакет:** [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/SHA256SUMS_v10_23_r4.txt)

**Test:** [Taxo 10.23-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r7) — prerelease, 8 файлів, exact source `a60d1933ddde090f0cb5e8672c5070030647301d`. r7 атомарно зберігає dry-run inventory batch/report у workspace; Stable/Latest не змінює.

## Початок роботи та дані

Розпакуйте portable-архів або встановіть програму, виберіть **окрему папку робочого сховища** та внесіть реквізити підприємства, працівників, транспорт і маршрути. Детальні кроки — у [короткому старті](docs/guides/QUICK_START.md).

Бази, скани та персональні документи зберігаються в робочому сховищі окремо від програми. Перед оновленням робіть резервну копію. Не запускайте дві копії Taxo одночасно з одним робочим сховищем.

## Для розробки

Почніть із [START_HERE.md](START_HERE.md). Фактичний GitHub має пріоритет над застарілим handoff після збою сесії.

## Ліцензія

Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved. Taxo — proprietary software. [LICENSE.md](LICENSE.md) · [Сторонні компоненти](THIRD_PARTY_NOTICES.md).
