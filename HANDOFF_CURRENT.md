# HANDOFF_CURRENT — Taxo

**Підтверджено 17.11.2026 після звірки live GitHub, включно з гілками без PR.**

## Поточний стан

- Перевірена база main перед цим docs-only checkpoint: `751480375503f74cdc205d1d20ba5b34ff44cffe`; checkpoint змінює лише документацію.
- **10.21-r2 завершена, інтегрована й опублікована.**
- Product PR #493 merged / exact immutable release source: `b104f94ace0ae355df79c914b3be6f39417bd6e9`.
- Final product head before merge: `96c9a551e031adf44846263d4f44cc3acb533083`.
- Exact-source CI: START `44102833144` — **1442/1442**; Windows `44102833224`; Win7 `44102833082`; macOS Intel/ARM `44102833261` — SUCCESS.
- Microsoft Defender та post-scan integrity — PASS для Windows/Win7.
- Release-trigger PR #494 merged: `751480375503f74cdc205d1d20ba5b34ff44cffe`; publisher `44105145533` — SUCCESS.
- [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2) — Test prerelease, рівно 6 завантажених файлів: 4 Portable + START + SHA256; tag target `b104f94ace0ae355df79c914b3be6f39417bd6e9`.
- **Stable / GitHub Latest:** [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5), 8 файлів, без змін.

## Що завершено в r2

У загальному каталозі «Документи» додано необов'язковий read-only період **«Від / До»** у форматі РРРР-ММ-ДД. Межі включні. Період застосовується до повного списку до розбиття на сторінки та поєднується з пошуком, джерелом і фільтром сканів.

Якщо період активний, записи без коректної дати не видаються за такі, що входять у нього. Без періоду їхня попередня видимість збережена. Помилкова дата у полі фільтра або «Від» пізніше за «До» дають явну помилку, а не тихий неправильний результат.

Зміна не редагує файли, скани, сховище, backup/restore, шаблони чи бізнес-статуси. КЕП/e-signature, auto «підписано», physical purge, migration та нові залежності не додавались.

## Recovery

На початку цієї сесії HANDOFF/вхідний промпт казав, що 10.21-r1 ще не розпочата. Live GitHub показав інший стан: product/release r1 уже були завершені, а відкритим лишався recovery PR #492. Реалізацію r1 не повторювали.

У #492 macOS arm64 впав лише на upload artifact через DNS `ENOTFOUND`; build/regression до цього пройшли. Перезапущено тільки цей job, він завершився SUCCESS, після чого #492 merged як `bc63503e3b87bb0c5767c9c14ebd2f8b804aa6e3`.

Після цього fresh verification підтвердив: готової 10.21-r2 гілки/PR не було. r2 розпочато від exact main `bc63503e3b87bb0c5767c9c14ebd2f8b804aa6e3`. Stable не змінювали.

## Одна наступна дія

**10.21-r3 ще не розпочата.** У новій сесії виконати fresh GitHub verification, включно з відкритими PR та всіма refs, і лише тоді вибрати один наступний вузький крок з Issue #289.

Не перевикористовувати r2/tag/release. TemplateLibrary read-only; власні шаблони — CompanyTemplates. Stable/Latest змінюється тільки за прямою командою власника. Працювати через GitHub/хмарні перевірки; executable вручну не запускати.
