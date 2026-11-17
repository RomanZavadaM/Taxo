# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 17.11.2026.**

- Перевірена база main перед цим docs-only checkpoint: `086b0c5dfbbbf707717dbabe97f4698d7d09f8f3`.
- Завершений продуктовий checkpoint: **10.21-r1**.
- Product PR #490 merged / exact immutable release source: `c5e17aec02e60d8b87fc518165b7f62086dc5a9f`.
- Final product head before merge: `d0c2f0f34821f7443a877f556cb3152837422616`.
- Exact-source CI: START `44095180937` (**1436/1436**), Windows `44095181008`, Win7 `44095180907`, macOS Intel/ARM `44095180721` — SUCCESS.
- Microsoft Defender і post-scan integrity — PASS.
- Release-trigger PR #491 merged: `086b0c5dfbbbf707717dbabe97f4698d7d09f8f3`; publisher `44097198739` — SUCCESS.
- [v10.21-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r1): Test prerelease, 4 Portable + START + SHA256, exact target `c5e17aec02e60d8b87fc518165b7f62086dc5a9f`. Усі 6 assets завантажені.
- **Stable/Latest: [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5)**, повний комплект із 8 файлів; source `8a56a2da438777e1fa4549ad2a63883a2ac67e31`.

## Інтегрований результат 10.21-r1

- У загальному каталозі «Документи» є read-only фільтр сканів: усі / є / немає / помилка перевірки.
- Фільтр застосовується до повного snapshot до пагінації та комбінується з пошуком і джерелом.
- Режими «Є», «Немає» та «Помилка» показують лише записи DocumentVault.
- Невідома/помилкова кількість не вважається «немає сканів».
- Файли, скани, історія, бізнес-статуси й резервування не змінюються.
- КЕП/e-signature, auto «підписано», physical purge, migration, нові залежності та статуси не додавались.
- Issue #289 лишається відкритим як ширший напрям.

## Активна кодова ревізія

Немає. **10.21-r2 ще не розпочата.**

## Наступна дозволена ревізія

**10.21-r2**, лише після fresh GitHub verification і визначення одного вузького кроку з Issue #289. Номер r1, tag і release не перевикористовувати.

## Recovery

Читати START_HERE → HANDOFF_CURRENT → private profile profile/taxo → live GitHub, включно з усіма refs. Issue #61 — журнал змін; WORKLOG — історія. Детальний аудит: [фільтр сканів r1](docs/maintenance/AUDIT_DOCUMENT_SCAN_FILTER_10_21_R1.md).

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
