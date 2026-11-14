# Taxo 10.19-r5 — UI збору фактів і перегляд in-memory чернетки

## Мета

Після backend renderer-а 10.19-r4 додано користувацький шлях:
**Власні шаблони → Підготувати чернетку → заповнити поля → переглянути**.

Це все ще не кінцевий документ і не бізнес-факт. r5 нічого не записує у
накази, інструктажі, DocumentArchive або вихідні DOCX/PDF.

## Що додано

- кнопка **«Підготувати чернетку»** у вікні власних шаблонів;
- окрема форма fact-ів, побудована з variables конкретної власної редакції;
- read-only adapter до чинних реєстрів Taxo через entity_choices:
  - працівники;
  - водії;
  - транспортні засоби;
- stable-ID snapshots замість пошуку лише за текстовим підписом;
- UI-контроли для всіх типів r4: text, date, integer, person_ref, vehicle_ref, participants, pairs, sections, table_rows;
- multi-select учасників;
- ручне складання конкретних пар водій–ТЗ із захистом від точного дубля;
- sections: розділи розділяються порожнім рядком;
- table_rows: рядок на рядок, клітинки розділяються Tab;
- окреме read-only вікно preview без Save/Export.

## Захист даних і thread-safety

- форма завантажує exact source_sha256 власної редакції;
- якщо шаблон змінився після відкриття форми, preview відмовляється рендерити іншу редакцію мовчки;
- усі Tk values зчитуються у UI thread;
- background renderer отримує лише plain Python facts;
- adapter реєстрів не виконує SQL write calls;
- preview не змінює TemplateLibrary, CompanyTemplates, main DB або архів.

## Модульність

Окремі модулі:
- company_template_fact_choices.py — read-only registry adapter;
- company_template_fact_codec.py — pure input codecs;
- company_template_fact_widgets.py — typed Tk controls;
- company_template_draft_form_ui.py — orchestration window;
- company_template_draft_preview_ui.py — read-only preview;
- existing company_template_draft.py — renderer.

Feature-логіка не переносилась у main.py.

## Не входить у r5

- збереження заповненої чернетки як документа;
- DOCX/PDF generation;
- друк;
- DocumentArchive;
- підпис/скан оригіналу;
- автоматичне створення наказу або інструктажу.

Наступний логічний slice після перевірки r5: **10.19-r6** — спроєктувати
immutable snapshot заповненої чернетки як проміжний документний стан перед
генерацією DOCX/PDF, не змішуючи його з бізнес-фактом або архівом оригіналів.

Stable/Latest v10.18-r3 не змінюється автоматично.
