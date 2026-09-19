# AUDIT — Taxo 9.1 candidate r9.6

**Дата:** 19.09.2026  
**Stable:** Taxo 9.0.1  
**Функціональний baseline:** Taxo 9.1 candidate r9.4  
**Попередній пакет:** r9.5 — не рекомендується для тестування через CMD parsing regression.

## Факт із ручного тесту

На реальному Windows у повністю розпакованій папці `START.bat` r9.5 почав виконувати фрагменти власного тексту як окремі команди:
- `'xist' is not recognized...`;
- `'auncher' is not recognized...`;
- `'omplete' is not recognized...`;
- інші уривки рядків.

На скріншоті одночасно видно `requirements.txt`, `taxo_app.py` та інші файли в тій самій папці. Це спростовує попередню гіпотезу, що проблема лише в запуску без розпакування.

## Root cause / mitigation

Ризик внесений r9.5: UTF-8/український текст безпосередньо в BAT + `chcp 65001`.

Щоб не залежати від поведінки `cmd.exe` щодо UTF-8 batch parsing:
- весь START.bat тепер ASCII-only;
- `chcp` прибрано;
- файл має CRLF;
- локалізований текст винесено з BAT.

## Нові автоматичні gates

1. Python test: усі байти START.bat < 128.
2. Python test: відсутній `chcp`.
3. Python test: є CRLF.
4. Windows full-folder preflight: exit 0 + `START preflight OK.`.
5. Windows incomplete-folder simulation: exit 2.
6. Source ZIP verification: mandatory files + ASCII/CRLF BAT.

## Release rule

r9.6 не публікувати, доки:
- Windows 101+ tests green;
- full START preflight green;
- incomplete START guard green;
- macOS ARM64/Intel green;
- source package green.

`v9.1-r9.5` не змінювати і не перезаписувати.

## Manual retest

Після публікації r9.6 перша ручна дія — тільки повторний запуск START з повністю розпакованої папки. Лише після цього продовжувати функціональний operational gate.
