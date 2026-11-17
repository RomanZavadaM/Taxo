# HANDOFF_CURRENT — Taxo

**Підтверджено 17.11.2026 після звірки з live GitHub.**

## Поточний стан

- Перевірена продуктова/релізна база перед цим docs-only checkpoint: `d16617ed7e094405ece7e8bb90eecd3bd778b429`; сам checkpoint змінює лише документацію.
- Завершена й опублікована тестова ревізія: **10.20-r9**.
- Product PR #482 merged: `3669470cd80304f0f82f6eb542664e59fbfcca1e`; final product head `e490e1cdac9624d288ae38cceab08e306bafeb25`.
- Release-notes PR #483 merged; **точне джерело Test prerelease r9: `a607024d25557136b92c5de4a91ee1d6c7e8b1e1`**.
- Exact-source CI: START `44074962416` — SUCCESS, **1419/1419**; Windows `44074962450`; Windows 7 `44074962376`; macOS Intel/ARM `44074962435` — SUCCESS.
- Windows Defender та post-scan integrity — PASS.
- Release-trigger PR #484 merged: `d16617ed7e094405ece7e8bb90eecd3bd778b429`; publisher `44076489530` — SUCCESS.
- [v10.20-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r9) — Test prerelease, рівно 6 файлів: 4 Portable + START + SHA256; tag target `a607024d25557136b92c5de4a91ee1d6c7e8b1e1`.
- **Stable / GitHub Latest: [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5)**, 8 файлів; без змін.

## Що завершено в 10.20-r9

У загальному вікні **«Документи»** додано колонку **«Скани»**. Для документа зі сховища одразу видно **«Немає»** або **«Є: N»** за кількістю активних сканів паперового оригіналу.

Скани, прибрані у r8, не рахуються активними. Якщо сховище сканів пошкоджене або не проходить перевірку цілісності, каталог документів не зникає: у колонці показується **«Помилка перевірки»**.

Індикатор лише читає чинне захищене сховище. Наявність скана **не змінює статус документа і не означає «підписано»**. КЕП/e-signature, auto-signed status, physical purge, migration та нові формати зберігання не додавались.

## Важливий CI-факт

Перший r9 CI виявив **41 старий version-guard**, які ще дозволяли поточну версію лише до 10.20-r8. Оновлено тільки ці дозволи версії, без зміни предметної логіки тестів. Final product head `e490e1cd...` та exact release source `a607024d...` повністю зелені.

## Що далі

- **10.20-r10 ще не розпочата.**
- Не перевикористовувати номер r9, tag або release.
- Наступний slice вибирати окремо після fresh GitHub verification з Issue #289; не додавати «заодно» КЕП, auto-signed status, міграцію або physical purge.

Незмінні правила: TemplateLibrary read-only; власні шаблони — CompanyTemplates; Stable/Latest змінюється тільки за прямою командою власника; executable не запускати вручну для перевірки безпеки.
