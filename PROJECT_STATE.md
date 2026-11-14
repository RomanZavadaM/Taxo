# PROJECT_STATE — Taxo

**Дата:** 14.11.2026.

## Поточний підтверджений стан

Taxo інтегрував і опублікував **10.19-r4**.

- Exact product / release source: `a408ddbea823defdc91d1dd562e99ebddd032622`.
- Stable/Latest: **v10.18-r3**, без змін.
- Current Test prerelease: **v10.19-r4 — Test Portable**.
- 6 assets: Windows, Windows 7, macOS Intel, macOS ARM, START, SHA256.

## Реалізовано у r4

- typed fact validation;
- окремий fact-normalization module;
- окремий structural draft renderer;
- deep-copy in-memory preview;
- required/type/unknown-field validation;
- stable-ID person/vehicle snapshots;
- dynamic rows для pairs/participants/table_rows;
- повна відсутність write side effects під час preview.

Проміжний regex-defect під час refactor був виправлений до інтеграції; release source містить коректний variable-name regex.

## Exact-source CI

- START `43607027278` SUCCESS;
- Windows `43607027231` SUCCESS;
- Windows 7 `43607027233` SUCCESS;
- macOS `43607027263` SUCCESS;
- Defender/integrity gates PASS.
- Publisher `43607894395` SUCCESS.

## Наступна продуктова ревізія

**10.19-r5** — UI збору фактичних даних і перегляду in-memory draft через існуючі реєстри Taxo.

Не включати в r5:
- DOCX/PDF generation;
- запис business fact;
- DocumentArchive;
- signed scan/original handling.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
