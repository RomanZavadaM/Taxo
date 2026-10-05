# Документація Taxo

Цей розділ — основна точка входу до експлуатаційної та технічної документації Taxo.

**Stable:** [Taxo 10.10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10) — 05.10.2026, immutable
**Previous stable / rollback:** Taxo 10.3 / `v10.3`
**Verified candidate:** Taxo 10.10-r3 / `v10.10-r3` (перевірено власником)
**Next code revision:** `10.10-r4`

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

## Stable 10.10

- [GitHub Release v10.10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10) — Windows x64 Setup/Portable, Windows 7 SP1 x64 Portable, macOS ARM64/Intel, START/source та SHA-256.
- [Release notes 10.10](releases/RELEASE_NOTES_v10_10.md)
- [Індекс релізів](releases/RELEASE_INDEX.md)
- [Поточна контрольна точка](maintenance/CHECKPOINT_CURRENT.md)
- [Повний аудит 05.10.2026](maintenance/AUDIT_FULL_2026-10-05.md)

Stable 10.10 промотує перевірену власником лінію 10.10-r1…r3 (без PyMuPDF, CI hardening, правильна версія в програмі) разом з усією лінією 10.4…10.9.

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

Після stable 10.10 наступний кодовий крок — **10.10-r4** від актуального `main`. Уже видані revision не перевикористовуються.

## Дані користувача

Робочі БД, SQLite, скани, кеші та персональні документи не публікуються в GitHub releases. Оновлення програми не повинно вимагати повторного введення робочої бази.

## Історія

Старі release/checkpoint-и залишаються immutable у GitHub tags/releases і не є базою нової розробки.
