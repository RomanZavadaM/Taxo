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

## Поточний тестовий кандидат — Taxo 10.15-r3

Після стабільної 10.14-r4 інтегрується робоча лінія 10.15. У **10.15-r3** інструктажі отримали дію **«Створити комплект DOCX для друку»**: редагована програма і окремий лист для власноручних підписів. CSV більше не є головним результатом. У «Експлуатації» є **«Лист стажування…»** із вибором водія, наставника та транспортного засобу з бази, а також каталог підготовлених Word-документів за датою, темою і працівниками.

Готові файли зберігаються в робочому сховищі `Data/PaperDocuments` та входять у повний backup. Створення файла **не означає**, що інструктаж проведено, водія допущено або документ підписано. Майбутні опційні скани та ієрархічний каталог за працівником, ТЗ і категоріями — окрема задача [#289](https://github.com/RomanZavadaM/Taxo/issues/289); планована модульна перебудова Python — [#290](https://github.com/RomanZavadaM/Taxo/issues/290).

**Важливо:** стабільний випуск поки 10.14-r4. Тестовий r3 не вважати офіційно опублікованим, доки GitHub Release/tag/assets не перевірені. [Зміни 10.15-r3](docs/releases/RELEASE_NOTES_v10.15-r3.md).

## Попередні випуски

[Taxo 10.12-r10 — попередня стабільна](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10) · [10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) · [10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10).

## Історія можливостей 10.9-r10

- незворотна історія виданих шляхівок і номерів; retention не видаляє пов'язаний факт;
- чинність документів ТЗ на весь плановий період рейсу;
- посилений контроль праці/відпочинку, перекриттів, 3+9, тижневого й двотижневого відпочинку;
- 60-денний реєстр без вигаданого відпочинку; пріоритет фактичних джерел;
- баланс персоналу / П-5, режими 2/2 і 3/3;
- СТОІР: хронологія одометра й прогноз ТО;
- історичний контроль наказів у 10.9; **у 10.14 статус і паперовий підпис більше не блокують редагування чи видалення**;
- контроль сумісності схеми SQLite;
- структуроване сховище коду без зміни бізнес-логіки.

## Лінія 10.10

[10.10-r1 … r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) — попередні тестові prerelease. `10.10-r4` була superseded через проблему запуску на macOS. [**10.10-r5**](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) виправила запуск macOS і тепер є старішим архівним rollback.

## Лінія 10.12

**10.12-r10** завершує цикл «нічого не загубити»: повернено й захищено критичні UI-маршрути, 23/23 критичних функцій мають runtime-smoke requirement, а «План → факт» додатково перевіряється реальною дією на ізольованих даних. Після ручного приймання власником r10 опубліковано як stable 07.11.2026.

## Що вміє Taxo

Персонал і водії з історією ролей; індивідуальні та періодичні графіки; план/факт і поділені зміни; контроль роботи, керування, перерв та відпочинку; 60-денний реєстр діяльності; транспорт, пробіг, СТОІР і документи ТЗ; регулярні й нерегулярні шляхові листи; бланки підтвердження діяльності; аналогові тахокарти; накази та закріплення водій→ТЗ; PDF/Excel звіти; резервні копії та контроль сумісності SQLite.

Докладніше: [Огляд системи](docs/SYSTEM_OVERVIEW.md) · [Поточний стан](docs/PRODUCT_STATUS.md) · [Швидкий старт](docs/guides/QUICK_START.md) · [Керівництво користувача](docs/guides/USER_MANUAL.md)

## Для розробки

Починати з [`START_HERE.md`](START_HERE.md), далі [`HANDOFF_CURRENT.md`](HANDOFF_CURRENT.md), [`PROJECT_RULES.md`](PROJECT_RULES.md) та [`PROJECT_STATE.md`](PROJECT_STATE.md). Стабільна версія — **10.14-r4**, після завершення 10.15-r3 наступний кодовий крок — **10.15-r4**. Історія змін — [індекс релізів](docs/releases/RELEASE_INDEX.md).

## Ліцензія

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo — proprietary software.

[LICENSE.md](LICENSE.md) · [COPYRIGHT.md](COPYRIGHT.md) · [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
