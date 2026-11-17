# HANDOFF_CURRENT — Taxo

**Підтверджено 17.11.2026 після звірки live GitHub, включно з гілками без PR.**

## Поточний стан

- Перевірена база main перед цим docs-only checkpoint: `cdaaafe6078d55bbc7a2b3f5d605fc840d2d1cb6`; checkpoint змінює лише документацію.
- **10.21-r3 завершена, інтегрована й опублікована.**
- Product PR #496 merged / exact immutable release source: `f8a30882c473568293b3123e1f23feca22e54334`.
- Final product head before merge: `7ad2df8ba4dd08d754cb1f47ea29b804438a4979`.
- Exact-source CI: START `44111408334` — **1448/1448**; Windows `44111408360`; Win7 `44111408405`; macOS Intel/ARM `44111408772` — SUCCESS.
- Microsoft Defender та post-scan integrity — PASS для Windows/Win7.
- Release-trigger PR #497 merged: `a301ed020d62831257748c7658d5bc61987d4e98`; publisher `44113848030` — SUCCESS.
- [v10.21-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r3) — Test prerelease, рівно 6 завантажених файлів: 4 Portable + START + SHA256; tag target `f8a30882c473568293b3123e1f23feca22e54334`.
- **Stable / GitHub Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), 8 файлів; PR #499 merged `cdaaafe6078d55bbc7a2b3f5d605fc840d2d1cb6`, historical promotion `44116866634` SUCCESS. Стабільний реліз побудовано з незмінного r2 source `b104f94ace0ae355df79c914b3be6f39417bd6e9`; r3 лишається тестовою.

## Що завершено в r3

У загальному каталозі «Документи» додано read-only фільтр **«Тип»**. Список значень формується лише з уже наявного структурованого поля типу документа; нові категорії не вигадуються і дані не мігруються.

Точний тип застосовується до повного snapshot до пагінації та поєднується з пошуком, джерелом, фільтром сканів і періодом «Від / До». Невідомий тип дає порожню read-only вибірку.

Зміна не редагує файли, скани, сховище, backup/restore, шаблони чи бізнес-статуси. Категорії БДР/охорони праці/кадрові та навігація за працівниками/ТЗ у r3 не нормалізувались. КЕП/e-signature, auto «підписано», physical purge, migration та нові залежності не додавались.

## Recovery

Fresh verification почався з main `2145f025c82471b4917e5fafa20f2a821e7b169e`: перевірено 408 refs, включно з гілками без PR; готової 10.21-r3 гілки/PR не було. r2 не повторювали.

Перший START на проміжному r3 head запустив 1448 тестів і знайшов одну помилку лише у новому тесті: він жорстко очікував конкретний Unicode-порядок українських назв типів. Тест виправлено на перевірку складу значень без зміни продукту; фінальний PR head `7ad2df8ba4dd08d754cb1f47ea29b804438a4979` пройшов усі перевірки.

Після публікації r3 власник окремо наказав перевести **10.21-r2** у Stable/Latest. Команду виконано через PR #499, не змінюючи код або тестовий тег r3. Звичайний publisher на merge #499 відмовився повторно випускати існуючу ревізію; спеціальний stable promotion завершився SUCCESS.

## Одна наступна дія

**10.21-r4 ще не розпочата.** У новій сесії виконати fresh GitHub verification, включно з відкритими PR та всіма refs, і лише тоді вибрати один наступний вузький крок з Issue #289.

Не перевикористовувати r3/tag/release. TemplateLibrary read-only; власні шаблони — CompanyTemplates. Stable/Latest змінюється тільки за прямою командою власника. Працювати через GitHub/хмарні перевірки; executable вручну не запускати.
