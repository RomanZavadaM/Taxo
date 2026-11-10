# HANDOFF_CURRENT — Taxo

**10.11.2026:** власник протестував 10.15-r4 і доручив зробити її стабільною. GitHub підтверджує [v10.15-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r4) як Latest, prerelease=false; попередня stable — 10.14-r4.

- Product/tag `ae0c673a42c5b633706efdffc1adfd5b1b70681d`; у випуску 8 файлів. Перевірки [START](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804380), [Windows](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804065), [Win7-сумісність](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804054), [macOS Intel/ARM](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804153) — SUCCESS; ручного запуску на фізичній Windows 7 немає.
- Нові описи й переклади, маршрут до приватного профілю та актуальний статус — PR #308. Історичний WORKLOG звірено у private `dev-strategy/profile/taxo/taxo-history/2026-11-10-worklog-snapshot/WORKLOG.md`; новий журнал — `taxo-history/DEVELOPMENT_LOG.md`.
- Опис stable виправлено штатним publisher [42837469420](https://github.com/RomanZavadaM/Taxo/actions/runs/42837469420); GitHub Latest, tag та ID/digest усіх 8 файлів після публікації звірені й не змінені. У виданому START старий README: [актуальний комплект документації](docs/releases/DOCUMENTATION_v10.15-r4.md) доступний окремо зі сторінки релізу.
- Exact-main START artifact збережено у Drive `02_CURRENT_MAIN`, файл `1QIyvVj4PPTKOjB3anHX4zX3IlxmhvA_X`, 1 847 445 bytes; SHA256 до передавання `aa4449f6a3233a0e4dd7c0736acb73bf7fe04a14c5ab2ea67982a19777c6b4f2`; побайтове повторне зчитування не виконувалось.
- Власник доручив спроєктувати спільне збереження готових документів з необов'язковими підписаними копіями та відокремити накази й інструктажі. [Проєкт взаємодії](https://github.com/RomanZavadaM/dev-strategy/blob/profile/taxo/taxo-history/DESIGN_DOCUMENTS_ORDERS_BRIEFINGS_2026-11-10.md) і окремий автоматизований read-only огляд зафіксовано приватно; огляд виявив межу 1000 наказів, приховану ініціалізацію БД при читанні та ризики узгодженості резерву. Реалізації та перенесення ще немає. База `main.py` — 16 644 рядки (#289, #290).

## Наступна дія

Робота 10.15-r5 у гілці `work/v10.15-r5-document-catalog`: спільний читальний список наказів та PaperDocuments, без міграції і зміни схеми при перегляді. Потрібні CI/перевірка START, приймання власником, інтеграція та checkpoint; додавання сканів — наступний етап. Перед продовженням звірити open PR і його перевірки.

## Recovery

`START_HERE.md` → `HANDOFF_CURRENT.md` → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
