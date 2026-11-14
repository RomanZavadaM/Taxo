# HANDOFF_CURRENT — Taxo

**Актуально на 14.11.2026.**

## Поточний стан

- Поточний продуктовий checkpoint: **10.19-r4**.
- Exact product / release source: `a408ddbea823defdc91d1dd562e99ebddd032622`.
- **Stable / Latest:** `v10.18-r3` — без змін.
- **Поточний тестовий реліз:** `v10.19-r4 — Test Portable`.
- r4 prerelease: 4 Portable + START + SHA256, без Setup.

## 10.19-r4 — що завершено

1. Додано typed fact contract для `text`, `date`, `integer`, `person_ref`, `vehicle_ref`, `pairs`, `participants`, `sections`, `table_rows`.
2. Додано окремий структурний in-memory renderer.
3. Renderer працює на deep copy перевіреної власної редакції `CompanyTemplates`.
4. Відсутні required поля, неправильні типи, unknown facts/placeholders і невірна ширина dynamic-table дають явну помилку.
5. Person/vehicle refs використовують stable ID + snapshot-поля, сумісні з `entity_choices`.
6. Preview не змінює TemplateLibrary/CompanyTemplates, не пише в main DB, не створює наказ/інструктаж, не створює DocumentArchive і файли DOCX/PDF.
7. Fact normalization і renderer розділені на окремі модулі; main.py не роздуто.

Проміжний CI-fail під час розділення модулів був спричинений зайвим escape у regex імен змінних; до merge/release виправлено. У release source regex коректний.

## Exact-main перевірки r4

Для `a408ddbea823defdc91d1dd562e99ebddd032622`:
- START/source — `43607027278` SUCCESS;
- Windows — `43607027231` SUCCESS;
- Windows 7 — `43607027233` SUCCESS;
- macOS Intel + ARM — `43607027263` SUCCESS;
- Windows/Win7 Defender — PASS;
- post-scan integrity/hash verification — PASS.

Publisher:
- `43607894395` — SUCCESS;
- immutable release `v10.19-r4`;
- target = exact product source `a408ddbea823defdc91d1dd562e99ebddd032622`;
- 6 assets.

## Наступна дія

**Наступна кодова ревізія — 10.19-r5.**

UI збору/вибору fact-ів із чинних реєстрів Taxo та показ in-memory чернетки:
- text/date/integer — звичайні поля;
- person_ref/participants — вибір із реєстру працівників;
- vehicle_ref — вибір із реєстру ТЗ;
- pairs — існуючий безпечний контракт пар водій–ТЗ;
- preview не створює бізнес-факт;
- DOCX/PDF/DocumentArchive не змішувати в цей slice.

## Незмінні правила

- Виданий номер ревізії не переписувати і не використовувати повторно.
- Повний успішний exact-SHA комплект усіх платформ → Test prerelease.
- Stable/Latest змінювати лише за прямим рішенням власника.
- Не створювати нових монолітів і не переносити feature-логіку в main.py.
- Recovery: START_HERE.md → цей файл → PROJECT_STATE.md → live GitHub → Issue #61.
