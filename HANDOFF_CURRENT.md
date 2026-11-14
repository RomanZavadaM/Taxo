# HANDOFF_CURRENT — Taxo

**Актуально на 14.11.2026.**

## Поточний стан

- Поточний продуктовий checkpoint: **10.19-r5**.
- Exact product / release source: `0ab0cc761078b38e391c1998ddf9feee7447d3a8`.
- **Stable / Latest:** `v10.18-r3` — без змін.
- **Поточний тестовий реліз:** `v10.19-r5 — Test Portable`.
- r5 prerelease: 4 Portable + START + SHA256, без Setup.

## 10.19-r5 — що завершено

1. У `CompanyTemplates` додано дію **«Підготувати чернетку»**.
2. Форма будується з typed variables конкретної власної редакції.
3. Реєстри працівників/водіїв/ТЗ читаються через чинний `entity_choices` зі stable ID + snapshot-полями.
4. Є UI-контроли для `text`, `date`, `integer`, `person_ref`, `vehicle_ref`, `participants`, `pairs`, `sections`, `table_rows`.
5. Учасники підтримують multi-select; пари водій–ТЗ складаються явно.
6. Pair invariant узгоджений з чинними наказами: один ТЗ може мати кількох водіїв, але один водій не може одночасно мати кілька різних ТЗ у межах однієї чернетки; точний дубль блокується.
7. Форма прив'язана до exact `source_sha256`; якщо власна редакція змінилась після відкриття, preview відмовляється рендерити іншу редакцію мовчки.
8. Усі Tk values збираються в UI thread; background renderer отримує plain Python facts.
9. Preview read-only: не змінює TemplateLibrary, CompanyTemplates, main DB, накази/інструктажі, DocumentArchive і не створює DOCX/PDF.

## Exact-main перевірки r5

Для `0ab0cc761078b38e391c1998ddf9feee7447d3a8`:
- START/source — `43614552144` SUCCESS;
- Windows — `43614552146` SUCCESS;
- Windows 7 — `43614552095` SUCCESS;
- macOS Intel + ARM — `43614552161` SUCCESS;
- Windows/Win7 Defender — PASS;
- post-scan integrity/hash verification — PASS.

Publisher:
- `43615561706` — SUCCESS;
- immutable release `v10.19-r5`;
- target = exact product source `0ab0cc761078b38e391c1998ddf9feee7447d3a8`;
- 6 assets.

## Recovery note r5

Перед merge strict ruleset показав branch як `behind`. Перевірено, що 5 службових main-комітів змінювали лише recovery-документи, яких r5 не торкалась. Main був підтягнутий у r5 звичайним merge commit з двома батьками, без force; після цього required `build-windows` PASS і PR #428 merged.

## Наступна дія

**Наступна кодова ревізія — 10.19-r6.**

Immutable snapshot заповненої чернетки як проміжний документний стан перед DOCX/PDF:
- зафіксувати exact company-template revision SHA/edit_revision;
- зафіксувати normalized facts і rendered structured content;
- snapshot після створення не редагувати in-place;
- окремо від робочого наказу/інструктажу: snapshot не створює business fact автоматично;
- не змішувати в r6 генерацію DOCX/PDF, DocumentArchive, скани чи підписи;
- визначити безпечний workspace-relative storage/index і атомарний commit;
- backup/restore coverage додати разом зі snapshot storage.

## Незмінні правила

- Виданий номер ревізії не переписувати і не використовувати повторно.
- Повний успішний exact-SHA комплект усіх платформ → Test prerelease.
- Stable/Latest змінювати лише за прямим рішенням власника.
- Не створювати нових монолітів і не переносити feature-логіку в main.py.
- Recovery: START_HERE.md → цей файл → PROJECT_STATE.md → live GitHub → Issue #61.
