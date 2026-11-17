# HANDOFF_CURRENT — Taxo

**Актуально 17.11.2026, підтверджено live GitHub.**

## Поточний стан

- **10.21-r6 завершена, інтегрована й опублікована як Test prerelease.**
- Product PR #506 merged; exact immutable release source `ef444e7753ee0f112baf8729ca6cceefea738652`, фінальний PR head `e94c39080e2d2ab0e3db25bc7639edd50483c70f`.
- Exact-source CI: START `44150116439` — **1464/1464**; Windows `44150116540`; Win7 `44150116763`; macOS Intel/ARM `44150116499` — SUCCESS. Defender/integrity PASS.
- Release-trigger PR #507 merged `f89351973061538407e64e5c9746a0aec358bca9`; publisher `44151934906` — SUCCESS.
- [v10.21-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r6) — Test prerelease, **6 файлів**: Windows/Win7/macOS Intel/ARM Portable, START, SHA256; tag immutable exact source `ef444e7753ee0f112baf8729ca6cceefea738652`.
- **Stable/Latest** — [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), 8 файлів, без змін.

## Що зроблено в r6

У вікні **«Шляхівки»** додана власна навігація по даті для зручного внесення кілометражу з паперових шляхівок:
- поле `ДД.ММ.РРРР`;
- Enter або **«Перейти»** відкриває вибраний день;
- **«День -» / «Сьогодні» / «День +»** швидко перемикають дні;
- змінюється лише день, показаний у вікні шляхівок; дата головного графіка не переписується.

Логіку кілометражу, видачу/анулювання шляхівок, БД/schema, plan/fact, backup/restore, security та залежності не змінювали. Реалізація винесена в окремий `waybill_date_navigation.py`, а не додана в монолітний `main.py`.

## Recovery

Перший фінальний START на проміжному head `43bdb5a…` мав 1 failure із 1464: новий feature layer був імпортований, але не внесений у реєстр. Виправлено одним рядком до final head `e94c390…`; після цього work-branch і exact-main checks SUCCESS. Не повторювати проміжний failed run.

**10.21-r7 не розпочата.** Ручну UI-перевірку нового поля дати власником ще не зафіксовано. Наступна сесія: fresh live GitHub verification, включно з refs/гілками без PR; потім або врахувати результат ручного тесту r6, або вибрати один новий вузький крок. Stable не рухати без прямої команди.

Читати `START_HERE.md` → `HANDOFF_CURRENT.md` → `PROJECT_STATE.md` → private `profile/taxo` → live GitHub. TemplateLibrary read-only; власні шаблони — CompanyTemplates. Не запускати executable локально.
