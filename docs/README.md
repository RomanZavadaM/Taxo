# Документація Taxo

Цей розділ є основною точкою входу до **експлуатаційної документації** Taxo. Stable залишається **9.0.1**; поточна перевірочна лінія — **9.1 candidate r9.8** у PR #29.

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
- [Стан продукту та правила подальшої розробки](PRODUCT_STATUS.md)
- [Дані, зберігання та резервування](DATA_MODEL_AND_STORAGE.md)

## Поточний супровід

- [Технічний стан і контрольна точка](maintenance/README.md)
- [Поточний аудит Taxo 9.1 candidate r9.8](maintenance/AUDIT_v9_1_r9_8.md)
- [Аудит r9.7](maintenance/AUDIT_v9_1_r9_7.md)
- [Аудит Windows START r9.6](maintenance/AUDIT_v9_1_r9_6.md)
- [Аудит проблеми START r9.5](maintenance/AUDIT_v9_1_r9_5.md)
- [Функціональний аудит r9.4](maintenance/AUDIT_v9_1_r9_4.md)
- [Примітки до актуального релізу](releases/README.md)

## Історія розробки

Історичні `CHECKPOINT_*`, `TEST_REPORT_*`, `PUBLISH_STATUS_*`, старі примітки до релізів, патчі та ранні архіви версій 8.x **не знаходяться в `main`**. Вони збережені в окремій гілці [`history/development-v8`](https://github.com/RomanZavadaM/Taxo/tree/history/development-v8).

Докладніше: [Історія розвитку](HISTORY.md).

## Версія документації

Документація описує stable **Taxo 9.0.1** та зміни поточного перевірочного кандидата **Taxo 9.1 candidate r9.7**. Кандидат не вважається stable до завершення ручної експлуатаційної перевірки.

## Публікація і релізи

- [Повний індекс GitHub Releases](releases/RELEASE_INDEX.md)
- [GitHub publication summary r9.4](maintenance/GITHUB_PUBLICATION_SUMMARY_v9_1_r9_4.md)

Усі підготовлені 9.x release-контрольні точки опубліковані. Stable лишається 9.0.1; r9.5 є pre-release до завершення manual operational gate.
