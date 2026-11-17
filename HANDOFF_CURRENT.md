# HANDOFF_CURRENT — Taxo

**Підтверджено 17.11.2026 після звірки live GitHub, включно з гілками без PR.**

## Поточний стан

- Перевірена база main перед цим docs-only checkpoint: `086b0c5dfbbbf707717dbabe97f4698d7d09f8f3`; checkpoint змінює лише документацію.
- **10.21-r1 завершена, інтегрована й опублікована.**
- Product PR #490 merged / exact immutable release source: `c5e17aec02e60d8b87fc518165b7f62086dc5a9f`.
- Final product head before merge: `d0c2f0f34821f7443a877f556cb3152837422616`.
- Exact-source CI: START `44095180937` — **1436/1436**; Windows `44095181008`; Win7 `44095180907`; macOS Intel/ARM `44095180721` — SUCCESS.
- Microsoft Defender та post-scan integrity — PASS для Windows/Win7.
- Release-trigger PR #491 merged: `086b0c5dfbbbf707717dbabe97f4698d7d09f8f3`; publisher `44097198739` — SUCCESS.
- [v10.21-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r1) — Test prerelease, рівно 6 завантажених файлів: 4 Portable + START + SHA256; tag target `c5e17aec02e60d8b87fc518165b7f62086dc5a9f`.
- **Stable / GitHub Latest:** [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5), 8 файлів, без змін.

## Що завершено в r1

У загальному каталозі «Документи» додано read-only фільтр «Скани»: «Усі», «Є скани», «Немає сканів», «Помилка перевірки». Він поєднується з пошуком і фільтром джерела та застосовується до повного списку до розбиття на сторінки. Вузькі режими охоплюють лише записи DocumentVault; помилка перевірки не видається за відсутність сканів.

Зміна не редагує файли, скани, статуси чи резервні копії. КЕП/e-signature, auto «підписано», physical purge, migration, нові залежності та бізнес-статуси не додавались.

## Recovery

Fresh verification почався з main `9965827de5a75c64872848b54df2ccb6012d6a52`. Перевірено 402 refs, включно з гілками без PR; готової 10.21-r1 не було, тому реалізацію не повторювали. Стару stable не змінювали.

## Одна наступна дія

**10.21-r2 ще не розпочата.** У новій сесії виконати fresh GitHub verification, включно з відкритими PR та всіма refs, і лише тоді вибрати один наступний вузький крок з Issue #289.

Не перевикористовувати r1/tag/release. TemplateLibrary read-only; власні шаблони — CompanyTemplates. Stable/Latest змінюється тільки за прямою командою власника. Працювати через GitHub/хмарні перевірки; executable вручну не запускати.
