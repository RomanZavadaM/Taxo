# Taxo 10.19-r7 — DOCX export із immutable prepared snapshot

## Мета

Після immutable prepared snapshot у 10.19-r6 додано перший файловий формат:
editable DOCX створюється **тільки з уже збереженого і перевіреного snapshot-а**.
Поточна редакція CompanyTemplates під час export не перечитується.

## Що додано

- окремий модуль `prepared_document_docx.py`;
- структурний DOCX renderer для heading, paragraph, numbered/bullet list, static/dynamic table, page break, signature/attachment/figure placeholder, nested blocks та appendices;
- exact provenance у DOCX metadata і footer: prepared snapshot ID, company-template ID, edit revision і source SHA-256;
- atomic export через temp-файл + fsync + replace;
- відмова від мовчазного overwrite без explicit `overwrite=True`;
- в preview кнопка **«Експорт DOCX…»** disabled до успішного commit snapshot-а;
- background export отримує тільки workspace path, snapshot ID і target path; Tk state у worker не читається.

## Межі r7

Не входить у r7:

- PDF;
- print workflow;
- фінальний документний архів;
- scan/signature state;
- автоматичне створення наказу, інструктажу чи іншого business fact;
- write у vendor `TemplateLibrary`;
- повторне читання поточної CompanyTemplates revision під час DOCX export.

`TemplateLibrary` лишається read-only; користувацькі шаблони — `CompanyTemplates`.
Feature-логіка не переноситься в `main.py`.

Stable/Latest `v10.18-r3` не змінюється автоматично.

Наступний окремий slice після приймання r7: PDF/print path із prepared snapshot / DOCX без змішування з final archive.
