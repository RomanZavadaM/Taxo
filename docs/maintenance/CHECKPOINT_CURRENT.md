# Taxo — поточна контрольна точка

**Дата:** 09.11.2026  
**Stable / Latest:** [Taxo 10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4).  
**Поточний інтегрований кандидат:** Taxo **10.14-r8**, exact main `98c9f2daea8398c1bf18b64e5f96163c6c02e4cc`.  
**Наступна кодова ревізія:** **10.14-r9**.

## Що змінилось після stable

Після stable r4 експлуатаційне тестування дало кілька вузьких виправлень. r5 прибрав залишкове блокування додатків до наказів. r6–r7 посилили контроль втрати функцій у живому UI.

У r8 owner-test наказу №27 виявив глибшу проблему: після додавання водіїв/ТЗ вже відкрите вікно «Перегляд наказу» тримало старий порожній список. Через це DOCX/PDF/JPG могли мати порожню таблицю, хоча пари вже були додані.

r8 виправляє весь ланцюг:
- одиночне і масове додавання перевіряють реальний запис пар до commit;
- regression перевіряє дані після закриття й повторного відкриття БД;
- друк перед кожним форматом перечитує актуальні дані з БД;
- існуючий наказ має прямий доступ до поточних закріплень і mass picker;
- порожній новий наказ веде користувача у вкладку закріплень, а не в порожній Preview;
- raw запис не ховається через INNER JOIN.

## Доказ перевірок

### PR #280 / head r8
- Windows #1395 — SUCCESS;
- Win7 #371 — SUCCESS;
- macOS Intel/ARM #1296 — SUCCESS;
- Windows regression: **1033 tests / OK**.

### Exact main `98c9f2d…`
- START #2511 — SUCCESS, **1033 tests / OK**;
- Windows #1396 — SUCCESS;
- Win7 #372 — SUCCESS;
- macOS Intel/ARM #1297 — SUCCESS.

Окремо у логах PASS:
- `test_single_and_bulk_pairs_survive_database_reopen_and_feed_print_layout`;
- `test_open_preview_reloads_pairs_before_document_generation`;
- `test_existing_order_edit_shows_rows_and_opens_bulk_picker`.

## Резерв

- GitHub artifact #13677776040: `Taxo_v10_14_candidate_r8_START`, 1 748 707 байт.
- SHA256: `e75beea340ea24088a05d90fcb37c7c96edbed7f6c2d41e81a586cf0494e7284`.
- Google Drive `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.14-r8_2026-11-09_START.zip`, file ID `1ObOoSjHZvMmOzMgkNDULCCnQ0M42B7F3`, 1 748 707 байт.

## Backlog

Актуальні окремі напрями: #246, #237, #164, #251; #61 — live ledger.  
Застарілий docs PR #278 закрито без злиття після інтеграції r7/r8.

## Далі

Ручне приймання r8 на реальній БД:
1. одна пара;
2. кілька пар;
3. закрити/відкрити вікно;
4. звірити `закріплень: N`;
5. сформувати DOCX/PDF/JPG;
6. усі пари мають залишитись у базі й бути в таблиці наказу.

Stable v10.14-r4 не змінювати без окремого рішення власника.
