# AUDIT — Taxo 9.1 candidate r9.5

**Дата:** 19.09.2026  
**Baseline:** Taxo 9.1 candidate r9.4  
**Stable:** Taxo 9.0.1  
**Причина нового candidate:** дефект тестового START-пакета, виявлений під час ручного operational gate.

## Виявлена проблема

Користувач запустив `START.bat` безпосередньо з відкритого ZIP у Windows/7-Zip. Архіватор тимчасово витягнув BAT-файл без решти пакета. У результаті pip отримав:

`Could not open requirements file ... requirements.txt`

Сам `START.bat` уже переходив у власну папку через `cd /d "%~dp0"`, тому першопричина — не current working directory, а **неповне тимчасове витягання файлів із ZIP**.

## Виправлення r9.5

- START перевіряє `requirements.txt` і `taxo_app.py` до pip;
- неповний пакет завершується exit code 2;
- користувач отримує інструкцію повністю розпакувати ZIP;
- окремо перевіряється Python launcher `py`;
- додано `00_README_START.txt`;
- додано `release_naming.py`;
- виправлено dotted revision у назвах архівів;
- source workflow перевіряє обов'язкові файли в ZIP;
- Windows CI відтворює сценарій «є лише START.bat».

## Regression coverage

`tests/test_v9_1_r9_5.py` перевіряє:
- r9.4 → `candidate_r9_4`;
- r9.5 → `candidate_r9_5`;
- stable 9.0.1 naming не змінений;
- guard START стоїть перед pip;
- `00_README_START.txt` існує.

Окремий Windows workflow-крок запускає копію START.bat у порожній директорії та очікує exit code 2 + повідомлення про ZIP.

## Межа змін

Функціональна логіка графіків, П-5, персоналу, табеля, №340, шляхівок, тахографа і резервування не змінювалась. r9.5 є **пакувально-запускним hotfix candidate** поверх r9.4.

## Manual gate

Після публікації r9.5:
1. завантажити новий START ZIP;
2. повністю розпакувати;
3. запустити START.bat;
4. підтвердити нормальний старт;
5. продовжити operational gate з функціональними сценаріями r9.4.

Окремо можна перевірити негативний сценарій: запуск START.bat без сусідніх файлів має дати зрозуміле повідомлення про необхідність розпакування, а не pip error.

До завершення manual gate `main` залишається на stable 9.0.1.
