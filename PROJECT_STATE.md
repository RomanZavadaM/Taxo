# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 17.11.2026.**

- Перевірена база main перед цим docs-only checkpoint: `cdaaafe6078d55bbc7a2b3f5d605fc840d2d1cb6`.
- Завершений продуктовий checkpoint: **10.21-r3**.
- Product PR #496 merged / exact immutable release source: `f8a30882c473568293b3123e1f23feca22e54334`.
- Final product head before merge: `7ad2df8ba4dd08d754cb1f47ea29b804438a4979`.
- Exact-source CI: START `44111408334` (**1448/1448**), Windows `44111408360`, Win7 `44111408405`, macOS Intel/ARM `44111408772` — SUCCESS.
- Microsoft Defender і post-scan integrity — PASS.
- Release-trigger PR #497 merged: `a301ed020d62831257748c7658d5bc61987d4e98`; publisher `44113848030` — SUCCESS.
- [v10.21-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r3): Test prerelease, 4 Portable + START + SHA256, exact target `f8a30882c473568293b3123e1f23feca22e54334`. Усі 6 assets завантажені.
- **Stable/Latest: [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2)**, повний комплект із 8 файлів; immutable source `b104f94ace0ae355df79c914b3be6f39417bd6e9`. За прямою командою власника PR #499 merged `cdaaafe6078d55bbc7a2b3f5d605fc840d2d1cb6`; historical promoter `44116866634` SUCCESS. Тестова `v10.21-r3` лишається prerelease.

## Інтегрований результат 10.21-r3

- У загальному каталозі «Документи» є read-only фільтр «Тип».
- Доступні значення беруться з уже наявних структурованих `kind` у поточному snapshot; схема даних не змінюється.
- Точний тип застосовується до повного snapshot до пагінації.
- Фільтр комбінується з пошуком, джерелом, сканами та періодом «Від / До».
- Невідомий тип дає порожню read-only вибірку, а не змінює записи.
- Категорії БДР/ОП/кадрові та employee/vehicle navigation не входили в цей slice.
- Сховище, файли, скани, backup/restore, шаблони та бізнес-статуси не змінюються.
- КЕП/e-signature, auto «підписано», physical purge, migration та нові залежності не додавались.
- Issue #289 лишається відкритим як ширший напрям.

## Активна кодова ревізія

Немає. **10.21-r4 ще не розпочата.**

## Наступна дозволена ревізія

**10.21-r4**, лише після fresh GitHub verification і визначення одного вузького кроку з Issue #289. Номер r3, tag і release не перевикористовувати.

## Recovery

Читати START_HERE → HANDOFF_CURRENT → private profile profile/taxo → live GitHub, включно з усіма refs. Issue #61 — журнал змін; WORKLOG — історія. Детальний аудит: [фільтр типу r3](docs/maintenance/AUDIT_DOCUMENT_TYPE_FILTER_10_21_R3.md).

На старті r3 live GitHub підтвердив r2 як завершену та recovery-закриту; готової r3 гілки/PR не було. Перший новий START знайшов тільки надто жорстке очікування порядку українських назв у новому regression-тесті; продуктову логіку змінювати не довелось.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
