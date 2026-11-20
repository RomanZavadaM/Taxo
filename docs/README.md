# Документація Taxo

Головна мова документації — українська. Публічний короткий опис доступний ще шістьма мовами: [переклади](i18n/README.md).

**Stable / Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4) — 20.11.2026, 8 файлів, Windows/Win7/macOS Intel/ARM/START, 37 strict live UI routes.

**Попередня Stable:** [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1). Новішого опублікованого Test за r4 зараз немає. **10.23-r5 уже активна у PR #576, але ще проходить exact-head CI і не є релізом.**

## Робота з програмою

- [Швидкий старт і оновлення](guides/QUICK_START.md).
- [Експлуатація, СТОІР, накази, Word/PDF/JPG](guides/OPERATIONS_STOIR_GUIDE.md).
- [Керівництво користувача](guides/USER_MANUAL.md).
- [Персонал і графіки](guides/PERSONNEL_GUIDE.md).
- [Тахограф](guides/TACHOGRAPH_GUIDE.md).
- [Звіти](guides/REPORTS_GUIDE.md).
- [Адміністрування й резервні копії](guides/ADMIN_GUIDE.md).
- [Типові проблеми](guides/TROUBLESHOOTING.md).

## Актуально для stable r4

Taxo допомагає створювати, редагувати, переглядати й друкувати накази. Паперовий оригінал лишається первинним контролем; позначка паперового підпису не є КЕП і не блокує виправлення робочого запису Taxo.

Доступні DOCX, PDF, JPG та «Створити все». У r4 перегляд наказу адаптовано до малого вікна: довгі кнопки форматів і нижні дії не повинні зникати при 760×560. Робоча область бланків і дерево каталогу документів регулюються користувачем.

## Випуски та стан

- [Stable 10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4)
- [Що нового у 10.23-r4](releases/RELEASE_NOTES_v10.23-r4.md)
- [Індекс випусків](releases/RELEASE_INDEX.md)
- [Стан продукту](PRODUCT_STATUS.md)
- [Модель даних і резервування](DATA_MODEL_AND_STORAGE.md)
- [Ліцензія](LEGAL_AND_COPYRIGHT.md)

## Для розробки та відновлення

- [START_HERE.md](../START_HERE.md) — перший файл будь-якого сеансу.
- [HANDOFF_CURRENT.md](../HANDOFF_CURRENT.md) — поточна контрольна точка.
- [PROJECT_RULES.md](../PROJECT_RULES.md), [PROJECT_STATE.md](../PROJECT_STATE.md), [WORKLOG.md](../WORKLOG.md).
- [Чекліст випуску](maintenance/RELEASE_CHECKLIST.md), [Політика main](maintenance/MAIN_BRANCH_POLICY.md).
- Issue #61 — live development ledger.

Робочі бази, скани й особисті документи не публікуються разом із програмою. Перед оновленням робіть резервну копію.
