# Документація Taxo

Цей розділ — основна точка входу до експлуатаційної та технічної документації Taxo.

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated checkpoint in `main`:** **Taxo 10.9-r10**  
**Latest full multi-platform published checkpoint:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)  
**Previous stable / rollback:** Taxo 10.1 / `v10.1`  
**Next code revision:** `10.10-r1`

> `10.9-r10` уже інтегровано в `main`, але окремий повний public release з готовими пакетами для цієї ревізії не публікувався. Для Windows/macOS тестування останнім повним release лишається `v10.9-r9`.

## Керівництва

- [Швидкий старт](guides/QUICK_START.md) — перший запуск, робоче сховище, базове налаштування.
- [Інструкція для персоналу](guides/USER_MANUAL.md) — щоденна робота диспетчера, кадрового працівника та працівника обліку робочого часу.
- [Робота з персоналом](guides/PERSONNEL_GUIDE.md) — реєстр, планування, відпустки/лікарняні, табель і П-5.
- [Робота з тахографом](guides/TACHOGRAPH_GUIDE.md) — скани тахокарт, інтервали, підтвердження та протоколи.
- [Робота зі звітами](guides/REPORTS_GUIDE.md) — табелі, контроль №340, 60-денний реєстр, PDF/Excel.
- [Адміністрування, сховище і резервні копії](guides/ADMIN_GUIDE.md) — перенесення даних, резервування та відновлення.
- [Типові проблеми](guides/TROUBLESHOOTING.md) — діагностика перед зверненням.

## Опис системи

- [Огляд системи та функціоналу](SYSTEM_OVERVIEW.md)
- [Поточний стан продукту](PRODUCT_STATUS.md)
- [Дані, зберігання та резервування](DATA_MODEL_AND_STORAGE.md)
- [Авторські права та ліцензія](LEGAL_AND_COPYRIGHT.md)

## Поточний інтегрований checkpoint — 10.9-r10

- [Release notes 10.9-r10](releases/RELEASE_NOTES_v10.9-r10.md)
- [Індекс релізів](releases/RELEASE_INDEX.md)
- [Поточна контрольна точка](maintenance/CHECKPOINT_CURRENT.md)
- [Технічний стан](maintenance/PROJECT_STATE.md)

10.9-r10 завершив структурне впорядкування репозиторію: runtime-модулі в `src/taxo/`, шаблони в `assets/`, packaging у `packaging/`, без зміни бізнес-логіки та без міграції робочих даних.

## Останній повний public release — 10.9-r9

- [GitHub Release v10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)
- Windows x64 Setup/Portable;
- Windows 7 SP1 x64 Setup/Portable;
- macOS ARM64/Intel;
- START/source та SHA-256.

Stable лишається `v10.3` до окремого рішення власника.

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

Після завершеного `10.9-r10` наступний кодовий крок — тільки **10.10-r1** від актуального `main`. Уже видані revision не перевикористовуються.

## Дані користувача

Робочі БД, SQLite, скани, кеші та персональні документи не публікуються в GitHub releases. Оновлення програми не повинно вимагати повторного введення робочої бази.

## Історія

Старі release/checkpoint-и залишаються immutable у GitHub tags/releases і не є базою нової розробки.
