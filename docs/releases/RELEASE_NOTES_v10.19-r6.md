# Taxo 10.19-r6 — immutable snapshot підготовленої чернетки

## Мета

Після read-only preview у 10.19-r5 додано окремий проміжний стан документа:
користувач може явно зберегти вже заповнену та відрендерену чернетку як
immutable snapshot перед майбутньою генерацією DOCX/PDF.

Snapshot не створює наказ, інструктаж чи інший бізнес-факт автоматично.

## Що додано

- окреме workspace-сховище `Data/PreparedDocuments`;
- незмінний ID snapshot-а та окремий JSON-файл для кожної збереженої чернетки;
- фіксація exact `company_template_id`, `source_sha256` та `edit_revision`;
- фіксація normalized facts, опису variables, rendered structure і rendered content;
- SHA-256 та розмір кожного snapshot-а в індексі;
- перевірка цілісності при читанні та fail-closed реакція на підміну, сирітський файл або небезпечний об'єкт;
- атомарна заміна файлів через temp + fsync + replace;
- явна дія **«Зберегти підготовлену чернетку»** у preview;
- серіалізація збереження без Tk-read у background worker;
- `PreparedDocuments` включено до повного workspace backup/restore.

## Незмінність і межі

У r6 немає API редагування або видалення вже створеного snapshot-а.
Нова чернетка створює новий snapshot, не переписуючи попередній.

Не входить у r6:

- DOCX/PDF generation;
- друк;
- фінальний DocumentArchive;
- скани або підписи;
- автоматичне створення наказу/інструктажу;
- зміна vendor `TemplateLibrary`;
- зміни release/build/security механізмів.

Feature-логіка залишається в окремих модулях
`prepared_document_codec.py` та `prepared_document_store.py`; у `main.py`
додано лише нову версійну ідентичність.

Stable/Latest `v10.18-r3` не змінюється автоматично.

Наступний окремий slice після приймання r6: DOCX renderer/export для
підготовленого snapshot-а. PDF/print і фінальний архів залишаються подальшими
окремими етапами.
