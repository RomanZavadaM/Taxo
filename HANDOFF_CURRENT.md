# HANDOFF_CURRENT — Taxo

**10.11.2026:** власник протестував 10.15-r4 і доручив зробити її стабільною. GitHub підтверджує [v10.15-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r4) як Latest, prerelease=false; попередня stable — 10.14-r4.

- Product/tag `ae0c673a42c5b633706efdffc1adfd5b1b70681d`; у випуску 8 файлів. Перевірки [START](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804380), [Windows](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804065), [Win7-сумісність](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804054), [macOS Intel/ARM](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804153) — SUCCESS; ручного запуску на фізичній Windows 7 немає.
- Нові описи й переклади, маршрут до приватного профілю та актуальний статус — PR #308. Історичний WORKLOG звірено у private `dev-strategy/profile/taxo/taxo-history/2026-11-10-worklog-snapshot/WORKLOG.md`; новий журнал — `taxo-history/DEVELOPMENT_LOG.md`.
- На сторінці релізу текст ще каже «тестовий кандидат» і помилково називає stable 10.14-r4. Виправити metadata, коли стане доступне редагування релізу. У виданому START r4 також застарілий README; тег і asset не змінювалися. Потрібен окремий комплект актуальної документації до випуску.
- Exact-main START artifact збережено у Drive `02_CURRENT_MAIN`, файл `1QIyvVj4PPTKOjB3anHX4zX3IlxmhvA_X`, 1 847 445 bytes; SHA256 до передавання `aa4449f6a3233a0e4dd7c0736acb73bf7fe04a14c5ab2ea67982a19777c6b4f2`; побайтове повторне зчитування не виконувалось.
- Наступна кодова ревізія 10.15-r5 — перебудова, починаючи з наказів та інструктажів. База `main.py` — 16 644 рядки, перенесення ще не починалося (#290).

## Наступна дія

Завершити оформлення стабільної 10.15-r4: синхронізувати опис релізу і додати окремо актуальну документацію; після цього почати узгоджену перебудову.

## Recovery

`START_HERE.md` → `HANDOFF_CURRENT.md` → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
