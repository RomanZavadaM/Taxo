# Taxo 9.1 candidate r9.6

Windows START compatibility hotfix поверх **Taxo 9.1 candidate r9.5**.

Stable baseline залишається **Taxo 9.0.1**. Функціональна логіка r9.4 не змінюється.

## Чому потрібен r9.6

Після публікації r9.5 ручний тест на реальному Windows показав, що `cmd.exe` некоректно розбирає `START.bat`: окремі частини рядків виконуються як команди (`'xist' is not recognized`, `'auncher' is not recognized` тощо).

Пакет був повністю розпакований, `requirements.txt` і `taxo_app.py` знаходилися поруч. Отже це вже не проблема запуску з ZIP, а **регресія самого BAT-файла**.

Найризикованіша зміна r9.5 — UTF-8/український текст у BAT разом із `chcp 65001`. У r9.6 цей ризик повністю прибрано.

## START.bat r9.6

- тільки ASCII-символи;
- без `chcp`;
- Windows CRLF;
- українська інструкція винесена в `00_README_START.txt`;
- перевірка повноти папки виконується до Python/pip;
- перевіряється саме Python 3.13 через `py -3.13`;
- додано технічний режим `TAXO_START_PREFLIGHT_ONLY=1` для CI;
- нормальний запуск не змінений: встановлення requirements → запуск `taxo_app.py`.

## Реальні Windows CI-сценарії

### Повністю розпакований пакет
Windows runner реально виконує `START.bat` у повній папці з:
`TAXO_START_PREFLIGHT_ONLY=1`.

Очікується:
- exit code 0;
- текст `START preflight OK.`.

Це перевіряє, що `cmd.exe` може коректно прочитати весь BAT.

### Неповна папка
Windows runner копіює лише `START.bat` у порожню директорію.

Очікується:
- exit code 2;
- пояснення про необхідність повністю розпакувати ZIP;
- pip не запускається.

## Контроль пакета

Source package CI додатково перевіряє:
- `START.bat` присутній;
- `requirements.txt`, `taxo_app.py`, `00_README_START.txt`, `release_naming.py` присутні;
- START.bat ASCII-only;
- START.bat не містить `chcp`;
- START.bat має CRLF;
- БД, SQLite, кеші та персональні дані відсутні.

## Regression tests

Додано `tests/test_v9_1_r9_6.py`.

Він перевіряє:
- коректне ім'я `r9.6` START archive;
- ASCII-only START;
- відсутність codepage switch;
- повний і неповний preflight paths;
- package guard до Python/pip.

## Статус r9.5

`v9.1-r9.5` лишається immutable історичним release і не пересувається, але **не рекомендується для подальшого ручного тестування** через Windows CMD parsing regression.

Після зеленого CI поточним тестовим пакетом має бути тільки r9.6.

## Функціональний baseline

Без змін з r9.4:
- canonical exact intervals;
- «Аудит графіків…»;
- окремий «Контроль №340»;
- Персонал / режими;
- П-5 PDF/XLSX;
- архів бланків;
- місячний контроль;
- backup/restore.

## Manual gate

Після публікації r9.6:
1. завантажити новий START ZIP;
2. повністю розпакувати;
3. запустити `START.bat`;
4. підтвердити нормальний старт;
5. продовжити operational gate.

До завершення gate `main` залишається на stable 9.0.1.
