# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 17.11.2026.**

- Поточний `main` перед цим docs-only checkpoint: `3239e6dd87a44a7210ea7ae1f6d3d0deeffaf5c2`.
- Завершений продуктовий checkpoint: **10.20-r7**.
- Product PR #471 merged: `48ef40c77aa43da4140a390dbc14cc3ef3483b47`.
- Точне джерело Test prerelease r7: `172cc44d863c60e63d89f45dcc11d31fa575db46`.
- [v10.20-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r7): Test prerelease, 4 Portable + START + SHA256.
- Exact-source CI: START `43918902181` (**1408/1408**), Windows `43918902255`, Windows 7 `43918902260`, macOS Intel/ARM `43918902511` — SUCCESS.
- Windows Defender та post-build integrity — PASS.
- Release publisher `44054730816` — SUCCESS.
- **Stable/Latest: [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5)**, повний комплект із 8 файлів.
- Точне джерело Stable r5: `8a56a2da438777e1fa4549ad2a63883a2ac67e31`.

## Інтегрований результат 10.20-r7

У вікні «Скани паперових оригіналів» для вибраного вкладення є явна дія **«Відкрити»**. Перед показом файл повторно проходить перевірку типу/розміру/SHA-256 через чинний захищений шлях. Перевірка виконується у фоні. Закриття вікна під час перевірки скасовує подальше відкриття.

Наявність або перегляд скана не змінює бізнес-статус документа і не означає «підписано». КЕП та автоматичний підпис не реалізовані.

## Активна кодова ревізія

Немає. **10.20-r8 ще не розпочата**: гілки/PR/коду r8 у live GitHub не знайдено.

## Наступна дозволена ревізія

**10.20-r8.** Перед створенням гілки взяти один обмежений наступний slice з чинного плану DocumentVault/сканів, не розширюючи його «заодно» на КЕП, авто-статуси чи міграцію.

## Recovery

Читати `START_HERE.md` → `HANDOFF_CURRENT.md` → private profile `profile/taxo` → звірити live GitHub. Issue #61 — журнал змін; WORKLOG.md — історія.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
