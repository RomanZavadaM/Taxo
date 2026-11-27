# Документація Taxo

Головна мова документації — українська. Публічний короткий опис доступний ще шістьма мовами: [переклади](i18n/README.md).

**Stable / Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3) — 23.11.2026, 8 файлів, exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, Windows/Win7/macOS Intel/ARM/START, 39 strict live UI routes, correspondence journal/card UI.

**Попередня Stable:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4). **Поточний Test:** [10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`; 8 assets; захист копій документів ТЗ у workspace/backup/restore; Stable лишається 10.24-r3.

## Робота з програмою

- [Швидкий старт і оновлення](guides/QUICK_START.md).
- [Експлуатація, СТОІР, накази, Word/PDF/JPG](guides/OPERATIONS_STOIR_GUIDE.md).
- [Керівництво користувача](guides/USER_MANUAL.md).
- [Персонал і графіки](guides/PERSONNEL_GUIDE.md).
- [Тахограф](guides/TACHOGRAPH_GUIDE.md).
- [Звіти](guides/REPORTS_GUIDE.md).
- [Адміністрування й резервні копії](guides/ADMIN_GUIDE.md).
- [Типові проблеми](guides/TROUBLESHOOTING.md).

## Актуально для Stable 10.24-r3

Taxo допомагає створювати, редагувати, переглядати й друкувати накази. Паперовий оригінал лишається первинним контролем; позначка паперового підпису не є КЕП і не блокує виправлення робочого запису Taxo.

Доступні DOCX, PDF, JPG та «Створити все». Ще у 10.23-r4 перегляд наказу адаптовано до малого вікна: довгі кнопки форматів і нижні дії не повинні зникати при 760×560. Робоча область бланків і дерево каталогу документів регулюються користувачем.

## Випуски та стан

- [Stable 10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3)
- [Current Test 10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9) — Taxo-owned копії документів ТЗ, source path/size/SHA-256, factual file state і перевірений backup/restore; Stable не змінює
- [Test 10.24-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r7) — end-to-end live-control «Учасники / ТЗ»; Stable не змінює
- [Test 10.24-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r6) — full live-control correspondence actions; Stable не змінює
- [Попередній Test 10.24-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r5) — logical cases/threads без копіювання листів
- [Що нового у 10.24-r9](releases/RELEASE_NOTES_v10.24-r9.md)
- [Попередній Test 10.24-r8](releases/RELEASE_NOTES_v10.24-r8.md)
- [Що нового у 10.24-r7](releases/RELEASE_NOTES_v10.24-r7.md)
- [Що нового у 10.24-r6](releases/RELEASE_NOTES_v10.24-r6.md)
- [Що нового у 10.24-r5](releases/RELEASE_NOTES_v10.24-r5.md)
- [Попередній Test 10.24-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r4) — explicit sent/received, state history, due/overdue
- [Що нового у 10.24-r4](releases/RELEASE_NOTES_v10.24-r4.md)
- [Що нового у 10.24-r3](releases/RELEASE_NOTES_v10.24-r3.md)
- [Індекс випусків](releases/RELEASE_INDEX.md)
- [Стан продукту](PRODUCT_STATUS.md)
- [Модель даних і резервування](DATA_MODEL_AND_STORAGE.md)
- [Збереження, класифікація та AI-сортування документів](DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md)
- [Ліцензія](LEGAL_AND_COPYRIGHT.md)

## Для розробки та відновлення

- [START_HERE.md](../START_HERE.md) — перший файл будь-якого сеансу.
- [HANDOFF_CURRENT.md](../HANDOFF_CURRENT.md) — поточна контрольна точка.
- [PROJECT_RULES.md](../PROJECT_RULES.md), [PROJECT_STATE.md](../PROJECT_STATE.md), [WORKLOG.md](../WORKLOG.md).
- [Чекліст випуску](maintenance/RELEASE_CHECKLIST.md), [Політика main](maintenance/MAIN_BRANCH_POLICY.md).
- Issue #61 — live development ledger.

Робочі бази, скани й особисті документи не публікуються разом із програмою. Перед оновленням робіть резервну копію.
