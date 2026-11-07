# Документація Taxo

Цей розділ — основна точка входу до експлуатаційної та технічної документації Taxo.

**Stable / Latest:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10) — exact r10 checkpoint; повний multi-platform комплект; GitHub Latest
**Previous stable / safe rollback:** [Taxo 10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5)
**Older rollback:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10)
**Current integrated candidate:** **Taxo 10.13-r1** (`4ed9530`) — не опублікований; «Експлуатація / СТОІР / накази».
**Next code revision:** `10.13-r2`

## Керівництва

- [Швидкий старт](guides/QUICK_START.md) — перший запуск, робоче сховище, базове налаштування.
- [Інструкція для персоналу](guides/USER_MANUAL.md) — щоденна робота диспетчера, кадрового працівника та працівника обліку робочого часу.
- [Робота з персоналом](guides/PERSONNEL_GUIDE.md) — реєстр, планування, відпустки/лікарняні, табель і П-5.
- [Робота з тахографом](guides/TACHOGRAPH_GUIDE.md) — скани тахокарт, інтервали, підтвердження та протоколи.
- [Робота зі звітами](guides/REPORTS_GUIDE.md) — табелі, контроль №340, 60-денний реєстр, PDF/Excel.
- [Експлуатація, СТОІР і накази](guides/OPERATIONS_STOIR_GUIDE.md) — стан автопарку, ТО/ремонти, заявки, документи та життєвий цикл наказу.
- [Адміністрування, сховище і резервні копії](guides/ADMIN_GUIDE.md) — перенесення даних, резервування та відновлення.
- [Типові проблеми](guides/TROUBLESHOOTING.md) — діагностика перед зверненням.

## Стан посібників

Новий посібник **«Експлуатація, СТОІР і накази»** відповідає інтегрованому 10.13-r1. Решта старших посібників описують робочі сценарії попередніх ліній і в окремих місцях ще потребують актуалізації:

| Посібник | Написано для | Не описано |
|---|---|---|
| [Експлуатація, СТОІР і накази](guides/OPERATIONS_STOIR_GUIDE.md) | 10.13-r1 | поточний робочий сценарій; ручне приймання власником триває |
| [Швидкий старт](guides/QUICK_START.md) | 10.4 | структура пакета 10.9-r10 (`src/taxo/`, `assets/`) |
| [Інструкція для персоналу](guides/USER_MANUAL.md) | 10.4-r2 | СТОІР; накази й групи наказів; захист виданих шляхівок і номерів; контроль праці/відпочинку 10.9 |
| [Робота з персоналом](guides/PERSONNEL_GUIDE.md) | 10.10-r8 | Дія/державні відомості, масове поновлення, документи й строки, backup копій, простий місячний графік, персональні PDF/Excel, П-5 |
| [Робота з тахографом](guides/TACHOGRAPH_GUIDE.md) | 9.0 | правила пріоритету фактичних джерел у 60-денному реєстрі (10.9) |
| [Типові проблеми](guides/TROUBLESHOOTING.md) | 10.0 | контроль сумісності схеми БД (новіша схема блокується) |
| [Дані та резервування](DATA_MODEL_AND_STORAGE.md) | 9.0 | склад повної резервної копії (документи ТЗ, скани, Output — за вибором) |

Оновлення посібників — окрема задача після перевірки інтерфейсу; до того орієнтуйтеся на [release notes](releases/RELEASE_INDEX.md).

## Опис системи

- [Огляд системи та функціоналу](SYSTEM_OVERVIEW.md)
- [Поточний стан продукту](PRODUCT_STATUS.md)
- [Дані, зберігання та резервування](DATA_MODEL_AND_STORAGE.md)
- [Авторські права та ліцензія](LEGAL_AND_COPYRIGHT.md)

## Stable — 10.12-r10

- [GitHub Release v10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10) — Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START/source, SHA-256.
- [Release notes 10.12-r10](releases/RELEASE_NOTES_v10.12-r10.md)
- [Індекс релізів](releases/RELEASE_INDEX.md)
- [Поточна контрольна точка](maintenance/CHECKPOINT_CURRENT.md)
- [Повний аудит 05.10.2026](maintenance/AUDIT_FULL_2026-10-05.md)

## Лінія 10.10

- r1 — без PyMuPDF; r2 — CI hardening; r3 — версія/backup warning; r4 — version UI + Win7 Setup, але superseded через macOS startup issue; **r5 — попередня stable / rollback**.

## Мови публічного опису

Короткий public README підтримується українською, англійською, німецькою, іспанською, французькою, корейською та японською: [індекс перекладів](i18n/README.md).

## Для розробки

- [START_HERE.md](../START_HERE.md) — перша точка входу для нового чату/сесії.
- [PROJECT_RULES.md](../PROJECT_RULES.md) — постійні правила.
- [PROJECT_STATE.md](../PROJECT_STATE.md) — канонічний інтегрований стан.
- [WORKLOG.md](../WORKLOG.md) — оперативний поточний стан.
- [Правила розробки](maintenance/DEVELOPMENT_RULES.md)
- [Чекліст випуску](maintenance/RELEASE_CHECKLIST.md)
- [Політика main](maintenance/MAIN_BRANCH_POLICY.md)
- GitHub Issue #61 — append-only live development ledger.

Наступний кодовий крок — **10.13-r2** від актуального `main`, але спочатку потрібне ручне приймання 10.13-r1. Уже видані revision не перевикористовуються.

## Дані користувача

Робочі БД, SQLite, скани, кеші та персональні документи не публікуються в GitHub releases. Оновлення програми не повинно вимагати повторного введення робочої бази.

## Історія

Старі release/checkpoint-и залишаються immutable у GitHub tags/releases і не є базою нової розробки.
