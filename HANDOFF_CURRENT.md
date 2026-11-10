# HANDOFF_CURRENT — Taxo

**Дата:** 10.11.2026. **Стан:** 10.15-r4 інтегровано, прийнято власником і опубліковано як тестовий випуск. Документацію та переклади оновлено; структурне перенесення ще не розпочато.

## Підтверджена база

- Stable / GitHub Latest: **[v10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4)**; попередня stable — v10.12-r10. Stable не змінювати без окремого рішення власника.
- **10.15-r4:** PR #304 merged, exact product/tag `ae0c673a42c5b633706efdffc1adfd5b1b70681d`. Власник повідомив, що тестував кандидат і він, за його оцінкою, працює. Контроль документа працівника виявляє відсутній файл, строк перевіряється окремо (#302).
- Exact-main [START](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804380), [Windows](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804065), [Win7-сумісність](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804054), [macOS Intel/ARM](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804153) — SUCCESS; Win7 не є ручним запуском на Windows 7.
- **[v10.15-r4 prerelease](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r4):** publisher [42808943357](https://github.com/RomanZavadaM/Taxo/actions/runs/42808943357) SUCCESS, тег на exact product, 8 файлів: Windows і Win7 Setup/Portable, macOS Intel/ARM, START і SHA256.
- Exact-main START artifact збережено у Drive `02_CURRENT_MAIN`, файл `1QIyvVj4PPTKOjB3anHX4zX3IlxmhvA_X`, 1 847 445 bytes; SHA256 локально перед передаванням `aa4449f6a3233a0e4dd7c0736acb73bf7fe04a14c5ab2ea67982a19777c6b4f2`; після завантаження перевірено назву, розмір, папку, побайтове повторне завантаження не виконувалось.
- README українською та шістьма мовами, інструкція й стан оновлені через #305. Попередні описи й PROJECT_STATE збережено і звірено у private `dev-strategy/profile/taxo/taxo-history/2026-11-10-before-10.15-r4/`. Історія Git і WORKLOG залишені.

## Одна наступна дія

Почати окрему структурну ревізію **10.15-r5**: за рішенням власника спершу накази та інструктажі, визначити змістовний блок і його залежності, забезпечити сценарний захист і перенести код без зміни поведінки; звітувати про фактичне зменшення великих файлів. База `main.py` — 16 644 рядки; перенесення ще немає. Врахувати Issue #290, #275 та часткові карти/backup-restore; не робити масове перенесення ядра або міграцій без достатнього захисту.

## Recovery

`START_HERE.md` → `HANDOFF_CURRENT.md` → private `dev-strategy/profile/taxo/TAXO_PROFILE.md` → live GitHub → `PROJECT_STATE.md`.
