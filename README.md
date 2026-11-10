# Taxo / Driver Worktime

[Українська](README.md) · [English](docs/i18n/README.en.md) · [Deutsch](docs/i18n/README.de.md) · [Español](docs/i18n/README.es.md) · [Français](docs/i18n/README.fr.md) · [한국어](docs/i18n/README.ko.md) · [日本語](docs/i18n/README.ja.md)

**Taxo — настільна система для одного автотранспортного підприємства:** водії й персонал, графіки, табелі, шляхові листи, бланки підтвердження діяльності, транспорт, документи, СТОІР, звіти та контроль аналогових тахокарт.

> **Стабільна / остання версія:** [Taxo 10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4) — 09.11.2026; перевірені Windows 10/11, Windows 7, macOS Intel / Apple Silicon та START.
> **Попередня стабільна / повернення:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10)
> **Старіші архівні випуски:** [10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) · [10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10)

## Завантаження — Taxo 10.14-r4 (стабільна)

**Windows 10/11 x64:** [Інсталятор EXE](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Setup_Windows_x64.exe) · [Portable ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Інсталятор EXE](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Setup_Windows7_x64.exe) · [Portable ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_macOS_arm64_Portable.zip) · [Intel / x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_macOS_x86_64_Portable.zip)

**Перевірка з вихідного коду:** [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_START.zip) · [Контрольні суми SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/SHA256SUMS_v10_14_r4.txt) · [Що змінилося](docs/releases/RELEASE_NOTES_v10.14-r4.md) · [Індекс випусків](docs/releases/RELEASE_INDEX.md).

**Що нового після 10.12-r10:** упорядковані «Експлуатація» та СТОІР; вибір кількох водіїв і ТЗ для наказів; окрема кадрова й робоча нумерація; перегляд наказів; DOCX, PDF і JPG з узгодженими реквізитами та таблицями; редагування й видалення наказів без обмежень за статусом або паперовим підписом. **Taxo — допоміжне робоче середовище, паперові оригінали контролює людина.**

**Робочі бази даних, скани, кеші та персональні документи не входять до GitHub releases.** Перед заміною програми збережіть резервну копію робочого сховища; нову базу створювати або заново вводити дані не потрібно.

## Тестова версія 10.15-r4

У цій версії контроль документів працівників повідомляє, якщо прив'язаний локальний файл відсутній. Строк дії контролюється окремо. Якщо повернули файл на місце, натисніть «Оновити» у вікні контролю.

Лінія 10.15 також містить інструктажі з редагованим DOCX і окремим листом підписів, лист стажування та початковий каталог створених Word-документів. Файли каталогу входять у повну резервну копію. Створення файла не підтверджує проведення, підпис чи допуск.

Стабільною залишається 10.14-r4. [Завантажити START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.15-r4/Taxo_v10_15_candidate_r4_START.zip) · [Сторінка тестового випуску 10.15-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r4) · [Усі випуски](https://github.com/RomanZavadaM/Taxo/releases).

## Що вміє Taxo

Персонал і водії з історією ролей; індивідуальні та періодичні графіки; план/факт і поділені зміни; контроль роботи, керування, перерв та відпочинку; 60-денний реєстр діяльності; транспорт, пробіг, СТОІР і документи ТЗ; регулярні й нерегулярні шляхові листи; бланки підтвердження діяльності; аналогові тахокарти; накази та закріплення водій→ТЗ; PDF/Excel звіти; резервні копії та контроль сумісності SQLite.

Докладніше: [Огляд системи](docs/SYSTEM_OVERVIEW.md) · [Поточний стан](docs/PRODUCT_STATUS.md) · [Швидкий старт](docs/guides/QUICK_START.md) · [Керівництво користувача](docs/guides/USER_MANUAL.md)

## Для розробки

Починати з [`START_HERE.md`](START_HERE.md), далі [`HANDOFF_CURRENT.md`](HANDOFF_CURRENT.md), [`PROJECT_RULES.md`](PROJECT_RULES.md) та [`PROJECT_STATE.md`](PROJECT_STATE.md). Стабільна версія — **10.14-r4**; наступний напрям — поетапна перебудова структури (Issue #290). Історія змін — [індекс релізів](docs/releases/RELEASE_INDEX.md).

## Ліцензія

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo — proprietary software.

[LICENSE.md](LICENSE.md) · [COPYRIGHT.md](COPYRIGHT.md) · [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
