# HANDOFF_CURRENT — Taxo

**Актуально 17.11.2026, за live GitHub.**

## Поточний стан

- Продуктова ревізія **10.21-r5 завершена, інтегрована й опублікована як Test prerelease**.
- Product PR #503 merged; exact immutable release source `d3f01d1cefd11ac5cab15054dfab85d962c0a84c`, фінальний PR head `639d4461b2119dd7caebd37f8fb18e3ded5a890e`.
- Exact-source START `44141706069` — **1459/1459**, Windows `44141706165`, Win7 `44141706293`, macOS Intel/ARM `44141706021` — SUCCESS, Microsoft Defender та integrity PASS.
- Release-trigger PR #504 merged `1515b1b52fe0a9e9d38d49bed7fd4f06f0de674f`. Publisher run `44143863239` — SUCCESS з першої спроби.
- [v10.21-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r5) — Test prerelease, **6 файлів**: Windows/Win7/macOS Intel/ARM Portable, START, SHA256; tag immutable exact source `d3f01d1cefd11ac5cab15054dfab85d962c0a84c`.
- **Stable/Latest** — [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), 8 файлів, без змін, marker `10.21-r2`.

## Що зроблено в r5

У єдиному каталозі «Документи» клік заголовка **«№»** перемикає числово-природне сортування ▲/▼ (2 перед 10, 2-А перед 10-А). Порожні номери завжди в кінці. Відбір усім набором пошуку/джерела/типу/сканів/періоду й сортування виконуються **до пагінації**. Перемикання повертає першу сторінку. Сортування «Дата» з r4 збережено.

Лише read-only: без зміни сховища, сканів, даних, backup/restore, статусів, КЕП або залежностей.

## Recovery

Fresh verification перед r5: `main` `fd0e97f9af7cb54bf5112188cd1004e414d829fe`, 415 refs, жодної r5 гілки, старий docs-only PR #395. START/Windows/Win7/macOS попереднього main SUCCESS.

Перший проміжний START r5 знайшов помилкову regex-екранізацію числових груп. Виправлено до продуктового merge; фінальний head пройшов 1459/1459 і платформи. Не повторювати перші невдалі runs.

**10.21-r6 ще не розпочата.** Наступна дія: fresh verification live GitHub, включно з refs без PR, далі один вузький крок Issue #289. Не перевикористовувати r5/tag/release. Stable змінюється лише за прямою командою.

Читати `START_HERE.md` → `HANDOFF_CURRENT.md` → `PROJECT_STATE.md` → private `profile/taxo` → live GitHub. TemplateLibrary read-only; власні шаблони — CompanyTemplates. Не запускати executable локально.
