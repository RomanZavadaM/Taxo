# Taxo — поточна контрольна точка

**Дата:** 09.11.2026  
**Stable / Latest:** [Taxo 10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4).  
**Поточний інтегрований кандидат:** Taxo **10.14-r8**, main `98c9f2daea8398c1bf18b64e5f96163c6c02e4cc`.  
**Наступна кодова ревізія:** **10.14-r9**.

## Що змінилось після stable

Під час реального тестування наказів виявлено два різні класи втрати функції:

1. масовий вибір ТЗ/водіїв був доступний при створенні нового наказу, але не був нормально доступний у «Редагувати наказ» для вже існуючого;
2. уже відкрите вікно перегляду могло залишатися з порожнім кешованим списком після додавання пар і передавати цей старий список у DOCX/PDF/JPG.

У 10.14-r8 існуючий наказ показує свої закріплення та прямі дії для керування ними; збереження пар перевіряється в транзакції; перед друком дані перечитуються з БД.

## Доказ перевірок

- PR #280, final head `30d0df632c9c1cff562d9a51556632311440f16d`: Windows #1395, Win7 #371, macOS #1296 — SUCCESS.
- Exact main `98c9f2daea8398c1bf18b64e5f96163c6c02e4cc`: Windows #1396, Win7 #372, macOS Intel/ARM #1297, START #2511 — **SUCCESS**.
- Exact-main START regression: **1033 tests OK**.
- Окремі r8 PASS: existing order → edit → bulk picker; single+bulk pairs → commit → DB reopen → print layout; open empty preview → add pair → DOCX receives fresh pair.
- Exact-main START artifact #13677776040, 1 748 707 байт, SHA256 `e75beea340ea24088a05d90fcb37c7c96edbed7f6c2d41e81a586cf0494e7284`.
- Google Drive backup: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.14-r8_2026-11-09_START.zip`, file ID `1lC9JVUXd6X46zIeEzxxrJDHKsyGInJ6z`.

## Feature Loss Guard

10.14-r7 ввів строгий live-gate. У r8 сценарій редагування існуючого наказу додано як окремий **26-й** critical route `operations.assignment_existing`. Issue #275 не закривати повністю: ще треба системно вирішити випадок, коли нову критичну UI-дію розробник узагалі забув зареєструвати.

## Далі

Ручне приймання r8 на робочому сценарії: додати кілька пар → перевірити вкладку закріплень → закрити/відкрити наказ → «Редагувати наказ» → сформувати DOCX/PDF/JPG. Stable v10.14-r4 не змінювати без окремого рішення власника.
