# Документація Taxo

Цей розділ — основна точка входу до експлуатаційної та технічної документації Taxo.

**Stable:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10) — immutable; перевірено власником на реальних даних
**Previous stable / rollback:** Taxo 10.3 / `v10.3`
**Тестова лінія в `main`:** 10.10-r3 (`v10.10-r1`…`r3` — prerelease, перевіряються на реальних даних)
**Next code revision:** `10.10-r4`

## Керівництва

- [Швидкий старт](guides/QUICK_START.md) — перший запуск, робоче сховище, базове налаштування.
- [Інструкція для персоналу](guides/USER_MANUAL.md) — щоденна робота диспетчера, кадрового працівника та працівника обліку робочого часу.
- [Робота з персоналом](guides/PERSONNEL_GUIDE.md) — реєстр, планування, відпустки/лікарняні, табель і П-5.
- [Робота з тахографом](guides/TACHOGRAPH_GUIDE.md) — скани тахокарт, інтервали, підтвердження та протоколи.
- [Робота зі звітами](guides/REPORTS_GUIDE.md) — табелі, контроль №340, 60-денний реєстр, PDF/Excel.
- [Адміністрування, сховище і резервні копії](guides/ADMIN_GUIDE.md) — перенесення даних, резервування та відновлення.
- [Типові проблеми](guides/TROUBLESHOOTING.md) — діагностика перед зверненням.

## Стан посібників (перегляд 05.10.2026)

Посібники описують робочі сценарії, але написані для старіших версій. Для stable 10.9-r10 вони **чинні в описаних частинах**, проте не охоплюють функції 10.5–10.9:

| Посібник | Написано для | Не описано |
|---|---|---|
| [Швидкий старт](guides/QUICK_START.md) | 10.4 | структура пакета 10.9-r10 (`src/taxo/`, `assets/`) |
| [Інструкція для персоналу](guides/USER_MANUAL.md) | 10.4-r2 | СТОІР; накази й групи наказів; захист виданих шляхівок і номерів; контроль праці/відпочинку 10.9 |
| [Робота з персоналом](guides/PERSONNEL_GUIDE.md) | 9.1 | реєстр документів працівників; звірка з Дія; військовий облік; баланс/П-5 10.9 |
| [Робота з тахографом](guides/TACHOGRAPH_GUIDE.md) | 9.0 | правила пріоритету фактичних джерел у 60-денному реєстрі (10.9) |
| [Типові проблеми](guides/TROUBLESHOOTING.md) | 10.0 | контроль сумісності схеми БД (новіша схема блокується) |
| [Дані та резервування](DATA_MODEL_AND_STORAGE.md) | 9.0 | склад повної резервної копії (документи ТЗ, скани, Output — за вибором) |

Оновлення посібників — окрема задача після перевірки інтерфейсу; до того орієнтуйтеся на [release notes](releases/RELEASE_INDEX.md).

## Опис системи

- [Огляд системи та функціоналу](SYSTEM_OVERVIEW.md)
- [Поточний стан продукту](PRODUCT_STATUS.md)
- [Дані, зберігання та резервування](DATA_MODEL_AND_STORAGE.md)
- [Авторські права та ліцензія](LEGAL_AND_COPYRIGHT.md)

## Stable — 10.9-r10

- [GitHub Release v10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10) — Windows x64 Setup/Portable, Windows 7 SP1 x64 Portable, macOS ARM64/Intel, START/source, SHA-256.
- [Release notes 10.9-r10](releases/RELEASE_NOTES_v10.9-r10.md)
- [Індекс релізів](releases/RELEASE_INDEX.md)
- [Поточна контрольна точка](maintenance/CHECKPOINT_CURRENT.md)
- [Повний аудит 05.10.2026](maintenance/AUDIT_FULL_2026-10-05.md)

## Тестова лінія — 10.10

- [10.10-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r1) — без PyMuPDF; [10.10-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r2) — CI hardening; [10.10-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) — правильна версія у вікні, попередження «лише БД».
- Це prerelease для перевірки на реальних даних; stable стануть лише після перевірки власником.

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

Наступний кодовий крок — **10.10-r4** від актуального `main`. Уже видані revision не перевикористовуються.

## Дані користувача

Робочі БД, SQLite, скани, кеші та персональні документи не публікуються в GitHub releases. Оновлення програми не повинно вимагати повторного введення робочої бази.

## Історія

Старі release/checkpoint-и залишаються immutable у GitHub tags/releases і не є базою нової розробки.
