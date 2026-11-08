# Taxo / Driver Worktime

[Українська](README.md) · [English](docs/i18n/README.en.md) · [Deutsch](docs/i18n/README.de.md) · [Español](docs/i18n/README.es.md) · [Français](docs/i18n/README.fr.md) · [한국어](docs/i18n/README.ko.md) · [日本語](docs/i18n/README.ja.md)

**Taxo — настільна система для одного автотранспортного підприємства:** водії й персонал, графіки, табелі, шляхові листи, бланки підтвердження діяльності, транспорт, документи, СТОІР, звіти та контроль аналогових тахокарт.

> **Stable / Latest:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10) — завершений цикл захисту від втрати функцій; Windows 10/11, Windows 7, macOS Intel та Apple Silicon перевірені
> **Попередній stable / rollback:** [Taxo 10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5)
> **Старіший rollback:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10)
> **Давніший rollback:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)

## Завантаження — Taxo 10.9-r10 (старіший rollback)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/SHA256SUMS_v10_9_r10.txt) · [Release notes 10.9-r10](docs/releases/RELEASE_NOTES_v10.9-r10.md) · [Індекс релізів](docs/releases/RELEASE_INDEX.md)

## Завантаження — Taxo 10.12-r10 (stable)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/SHA256SUMS_v10_12_r10.txt) · [Release notes 10.12-r10](docs/releases/RELEASE_NOTES_v10.12-r10.md)

Робочі БД, SQLite, скани, кеші та персональні документи до GitHub releases **не входять**. Оновлення не вимагає повторного введення робочих даних.

## Що було в stable 10.9-r10

- незворотна історія виданих шляхівок і номерів; retention не видаляє пов'язаний факт;
- чинність документів ТЗ на весь плановий період рейсу;
- посилений контроль праці/відпочинку, перекриттів, 3+9, тижневого й двотижневого відпочинку;
- 60-денний реєстр без вигаданого відпочинку; пріоритет фактичних джерел;
- баланс персоналу / П-5, режими 2/2 і 3/3;
- СТОІР: хронологія одометра й прогноз ТО;
- незмінність затверджених/підписаних наказів і закріплень водій→ТЗ;
- контроль сумісності схеми SQLite;
- структуроване сховище коду без зміни бізнес-логіки.

## Лінія 10.10

[10.10-r1 … r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) — попередні тестові prerelease. `10.10-r4` була superseded через проблему запуску на macOS. [**10.10-r5**](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) виправила запуск macOS і тепер є попередньою stable / rollback.

## Лінія 10.12

**10.12-r10** завершує цикл «нічого не загубити»: повернено й захищено критичні UI-маршрути, 23/23 критичних функцій мають runtime-smoke requirement, а «План → факт» додатково перевіряється реальною дією на ізольованих даних. Після ручного приймання власником r10 опубліковано як stable 07.11.2026.

## Що вміє Taxo

Персонал і водії з історією ролей; індивідуальні та періодичні графіки; план/факт і поділені зміни; контроль роботи, керування, перерв та відпочинку; 60-денний реєстр діяльності; транспорт, пробіг, СТОІР і документи ТЗ; регулярні й нерегулярні шляхові листи; бланки підтвердження діяльності; аналогові тахокарти; накази та закріплення водій→ТЗ; PDF/Excel звіти; резервні копії та контроль сумісності SQLite.

Докладніше: [Огляд системи](docs/SYSTEM_OVERVIEW.md) · [Поточний стан](docs/PRODUCT_STATUS.md) · [Швидкий старт](docs/guides/QUICK_START.md) · [Керівництво користувача](docs/guides/USER_MANUAL.md)

## Для розробки

Точка входу: [`START_HERE.md`](START_HERE.md). Далі — `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` та Issue #61. Поточна stable — `10.12-r10`; у `main` уже інтегровано новішу `10.13-r4`, але вона не stable. Наступна кодова ревізія — `10.13-r5`.

## Ліцензія

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo — proprietary software.

[LICENSE.md](LICENSE.md) · [COPYRIGHT.md](COPYRIGHT.md) · [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
