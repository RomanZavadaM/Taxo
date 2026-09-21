# Документація Taxo

Цей розділ є основною точкою входу до **експлуатаційної документації Taxo 10.1**.

**Stable:** Taxo 10.1  
**Previous stable / rollback:** Taxo 10.0  
**Verified candidate before stable:** v10.1-r5

## Керівництва

- [Короткий старт](guides/QUICK_START.md) — перший запуск, робоче сховище, базове налаштування.
- [Інструкція для персоналу](guides/USER_MANUAL.md) — щоденна робота диспетчера, кадрового працівника та працівника, який веде облік робочого часу.
- [Робота з персоналом](guides/PERSONNEL_GUIDE.md) — реєстр, масове планування, відпустки/лікарняні, табель і П-5.
- [Робота з тахографом](guides/TACHOGRAPH_GUIDE.md) — скани тахокарт, інтервали, підтвердження та протоколи.
- [Робота зі звітами](guides/REPORTS_GUIDE.md) — табелі, контроль №340, 60-денний реєстр, PDF/Excel.
- [Адміністрування, сховище і резервні копії](guides/ADMIN_GUIDE.md) — робоче сховище, перенесення даних, резервування та відновлення.
- [Типові проблеми](guides/TROUBLESHOOTING.md) — що перевіряти перед зверненням до розробника.

## Опис системи

- [Огляд системи та функціоналу](SYSTEM_OVERVIEW.md)
- [Стан продукту](PRODUCT_STATUS.md)
- [Дані, зберігання та резервування](DATA_MODEL_AND_STORAGE.md)

## Stable 10.1

- [GitHub Release v10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1)
- [Windows Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.1/Taxo_v10_1_Setup_Windows_x64.exe)
- [START/source](https://github.com/RomanZavadaM/Taxo/releases/download/v10.1/Taxo_v10_1_START.zip)
- [Release notes 10.1](releases/RELEASE_NOTES_v10_1.md)
- [Фінальний аудит 10.1](maintenance/AUDIT_v10_1_STABLE.md)
- [Поточний технічний стан](maintenance/PROJECT_STATE.md)
- [Поточна контрольна точка](maintenance/CHECKPOINT_CURRENT.md)
- [Повний індекс GitHub Releases](releases/RELEASE_INDEX.md)

## Previous stable 10.0

- [GitHub Release v10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0)
- [Release notes 10.0](releases/RELEASE_NOTES_v10_0.md)
- [Фінальний аудит 10.0](maintenance/AUDIT_v10_0_STABLE.md)

## Для розробки

- [Правила розробки](maintenance/DEVELOPMENT_RULES.md) — **кожен завершений крок = нова ревізія**; `r1 ... r10`, після `r10` — наступна minor-версія з `r1`.
- [Чекліст випуску](maintenance/RELEASE_CHECKLIST.md)
- [Політика main](maintenance/MAIN_BRANCH_POLICY.md)

Кожен завершений крок має окремий тестовий START-архів і пряме посилання для ручного тестування. Уже видану ревізію повторно не використовувати.

## Історія розробки

Історичні матеріали 8.x збережені в окремій гілці [`history/development-v8`](https://github.com/RomanZavadaM/Taxo/tree/history/development-v8).

Докладніше: [Історія розвитку](HISTORY.md).
