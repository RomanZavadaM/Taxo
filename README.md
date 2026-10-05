# Taxo / Driver Worktime

[Українська](README.md) · [English](docs/i18n/README.en.md) · [Deutsch](docs/i18n/README.de.md) · [Español](docs/i18n/README.es.md) · [Français](docs/i18n/README.fr.md) · [한국어](docs/i18n/README.ko.md) · [日本語](docs/i18n/README.ja.md)

**Taxo — настільна система для одного автотранспортного підприємства:** водії й персонал, графіки, табелі, шляхові листи, бланки підтвердження діяльності, транспорт, документи, СТОІР, звіти та контроль аналогових тахокарт.

> **Stable:** [Taxo 10.10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10) — 05.10.2026
> **Попередній stable / rollback:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)
> **Наступна кодова ревізія:** `10.10-r4`

## Завантаження — Taxo 10.10 (stable)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/SHA256SUMS_v10_10.txt) · [Release notes 10.10](docs/releases/RELEASE_NOTES_v10_10.md) · [Індекс релізів](docs/releases/RELEASE_INDEX.md)

Робочі БД, SQLite, скани, кеші та персональні документи до GitHub releases **не входять**. Оновлення не вимагає повторного введення робочих даних.

## Що нового в 10.10

- **Без PyMuPDF.** PDF/JPG бланка підтвердження, дата у звіті №340 і перегляд/друк PDF працюють на бібліотеках з permissive-ліцензіями (pypdfium2, reportlab, pypdf); бланк і звіт попіксельно ідентичні попереднім.
- **Правильна версія в програмі** — у заголовку, «Про програму», PDF-шапках і маніфесті резервної копії.
- **Резервна копія** явно попереджає, коли містить лише бази даних.
- **Інфраструктура:** вимкнено застарілі публікаційні workflow, тести ізольовані від робочого сховища, license gate у всіх збірках.
- Накопичено лінію 10.4 … 10.9: контроль документів ТЗ на весь рейс, захист виданих шляхівок і номерів, посилений контроль праці/відпочинку, 60-денний реєстр, П-5/баланс персоналу, СТОІР, незмінність підписаних наказів, контроль сумісності схеми SQLite.

## Що вміє Taxo

Персонал і водії з історією ролей; індивідуальні та періодичні графіки; план/факт і поділені зміни; контроль роботи, керування, перерв та відпочинку; 60-денний реєстр діяльності; транспорт, пробіг, СТОІР і документи ТЗ; регулярні й нерегулярні шляхові листи; бланки підтвердження діяльності; аналогові тахокарти; накази та закріплення водій→ТЗ; PDF/Excel звіти; резервні копії та контроль сумісності SQLite.

Докладніше: [Огляд системи](docs/SYSTEM_OVERVIEW.md) · [Поточний стан](docs/PRODUCT_STATUS.md) · [Швидкий старт](docs/guides/QUICK_START.md) · [Керівництво користувача](docs/guides/USER_MANUAL.md)

## Для розробки

Точка входу: [`START_HERE.md`](START_HERE.md). Далі — `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` та Issue #61. Після stable 10.10 нова кодова робота починається як `10.10-r4` від актуального `main`.

## Ліцензія

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo — proprietary software.

[LICENSE.md](LICENSE.md) · [COPYRIGHT.md](COPYRIGHT.md) · [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
