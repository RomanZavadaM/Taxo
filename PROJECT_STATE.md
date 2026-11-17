# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 17.11.2026.**

- Перевірена база main перед цим docs-only checkpoint: `751480375503f74cdc205d1d20ba5b34ff44cffe`.
- Завершений продуктовий checkpoint: **10.21-r2**.
- Product PR #493 merged / exact immutable release source: `b104f94ace0ae355df79c914b3be6f39417bd6e9`.
- Final product head before merge: `96c9a551e031adf44846263d4f44cc3acb533083`.
- Exact-source CI: START `44102833144` (**1442/1442**), Windows `44102833224`, Win7 `44102833082`, macOS Intel/ARM `44102833261` — SUCCESS.
- Microsoft Defender і post-scan integrity — PASS.
- Release-trigger PR #494 merged: `751480375503f74cdc205d1d20ba5b34ff44cffe`; publisher `44105145533` — SUCCESS.
- [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2): Test prerelease, 4 Portable + START + SHA256, exact target `b104f94ace0ae355df79c914b3be6f39417bd6e9`. Усі 6 assets завантажені.
- **Stable/Latest: [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5)**, повний комплект із 8 файлів; source `8a56a2da438777e1fa4549ad2a63883a2ac67e31`.

## Інтегрований результат 10.21-r2

- У загальному каталозі «Документи» є необов'язковий період «Від / До» у форматі РРРР-ММ-ДД.
- Межі включні; можна задати обидві межі або лише одну.
- Період застосовується до повного snapshot до пагінації та комбінується з пошуком, джерелом і фільтром сканів.
- Некоректні межі відхиляються явною помилкою; записи без коректної дати не потрапляють у активний період.
- Без активного періоду попередня поведінка каталогу зберігається.
- Сховище, файли, скани, backup/restore, шаблони та бізнес-статуси не змінюються.
- КЕП/e-signature, auto «підписано», physical purge, migration та нові залежності не додавались.
- Issue #289 лишається відкритим як ширший напрям.

## Активна кодова ревізія

Немає. **10.21-r3 ще не розпочата.**

## Наступна дозволена ревізія

**10.21-r3**, лише після fresh GitHub verification і визначення одного вузького кроку з Issue #289. Номер r2, tag і release не перевикористовувати.

## Recovery

Читати START_HERE → HANDOFF_CURRENT → private profile profile/taxo → live GitHub, включно з усіма refs. Issue #61 — журнал змін; WORKLOG — історія. Детальний аудит: [фільтр періоду r2](docs/maintenance/AUDIT_DOCUMENT_DATE_FILTER_10_21_R2.md).

На початку r2 live GitHub випереджав старий HANDOFF: r1 уже була завершена, але recovery #492 ще не merged. Це було звірено й закрито без повторної реалізації.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
