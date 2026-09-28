# Документація Taxo

Цей розділ — основна точка входу до експлуатаційної та технічної документації Taxo.

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo 10.5-r8 / `v10.5-r8`  
**Previous stable / rollback:** Taxo 10.1 / `v10.1`  
**Next code revision:** `10.5-r9`

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

## Поточний full checkpoint — 10.5-r8

- [GitHub Release v10.5-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8)
- [Release notes 10.5-r8](releases/RELEASE_NOTES_v10_5_r8.md)
- [Індекс релізів](releases/RELEASE_INDEX.md)
- [Поточна контрольна точка](maintenance/CHECKPOINT_CURRENT.md)
- [Технічний стан](maintenance/PROJECT_STATE.md)

`v10.5-r8` містить повний набір Windows modern, Windows 7 SP1, macOS ARM64/Intel, START і SHA-256. Він merged у `main`, але stable залишається `v10.3` до окремого рішення власника.

## Для розробки

- [START_HERE.md](../START_HERE.md) — перша точка входу для нового чату/сесії.
- [PROJECT_RULES.md](../PROJECT_RULES.md) — постійні правила.
- [PROJECT_STATE.md](../PROJECT_STATE.md) — канонічний інтегрований стан.
- [WORKLOG.md](../WORKLOG.md) — оперативний поточний стан.
- [Правила розробки](maintenance/DEVELOPMENT_RULES.md) — кожен завершений крок = нова ревізія `r1 … r10`; після `r10` — наступна minor-версія з `r1`.
- [Чекліст випуску](maintenance/RELEASE_CHECKLIST.md)
- [Політика main](maintenance/MAIN_BRANCH_POLICY.md)
- GitHub Issue #61 — append-only live development ledger.

Після `10.5-r8` наступний кодовий крок — тільки **10.5-r9**. Уже видані revision не перевикористовуються.

## Дані користувача

Робочі БД, SQLite, скани, кеші та персональні документи не публікуються в GitHub releases. Оновлення програми не повинно вимагати повторного введення робочої бази.

## Історія

Старі release/checkpoint-и залишаються immutable у GitHub tags/releases. Історичні матеріали 8.x збережені окремо в [`history/development-v8`](https://github.com/RomanZavadaM/Taxo/tree/history/development-v8). Для поточного стану не використовувати старі work/candidate branches як кодову базу.
