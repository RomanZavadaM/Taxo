# AUDIT — Taxo 10.2-r6 secondary-window UI consistency

**Дата:** 21.09.2026  
**Stable baseline:** Taxo 10.1 / `v10.1`  
**Work branch:** `work/v10.2-r6-secondary-window-style`

## Причина

Після переходу на новий application shell частина великих secondary windows ще відкривалась у старому Tk/Ttk вигляді без брендованої шапки. Це створювало візуальну різницю між головним workspace і службовими вікнами.

## Рішення

Додано один helper `_decorate_secondary_window()`, який:
- викликає базове оформлення Toplevel;
- задає заголовок `Taxo / <підприємство> — <розділ>`;
- додає єдину верхню брендовану смугу;
- використовує dynamic enterprise name;
- показує актуальну версію.

Helper застосовано до 12 великих робочих/звітних вікон.

## Межі revision

Навмисно не перебудовуються дрібні modal edit forms. Їх можна переводити на компактний modal-style окремим наступним revision, щоб не змішувати великий batch із десятками різних форм.

## Regression

`tests/test_v10_2_r6.py` перевіряє:
- version marker 10.2-r6;
- dynamic branding helper;
- використання helper у всіх 12 цільових вікнах;
- відсутність SQL/schema mutations у самому UI helper.

## Release policy

Після green source/Windows/macOS gate публікується окремий immutable START prerelease `v10.2-r6`. Stable `v10.1` не змінюється.
