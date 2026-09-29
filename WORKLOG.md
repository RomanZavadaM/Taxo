# WORKLOG — Taxo

**Оновлено:** 29.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.6-r10** / `v10.6-r10`  
**Latest integrated code checkpoint in `main`:** Taxo **10.6-r10**  
**Main:** `109d3c64f2a54a29c5b88eb190a934f0a890245d`  
**Active revision:** **10.7-r1**  
**Branch:** `work/v10.7-r1-tachograph-safety`  
**Base:** `main` after full 10.6-r10 closeout  
**Live ledger:** Issue #61

## DOING — 10.7-r1

Тема: безпечне повторне розпізнавання аналогових тахографічних шайб.

Підтверджені в актуальному коді дефекти:

- повторне розпізнавання повністю видаляло `intervals`, включно з `source='manual'`;
- імпорт запускав `recognize_all()` для всього каталогу;
- вибір порожнього запису міг неявно створити автокандидати;
- warning про невиявлене коло був недосяжним;
- circular run через 00:00 міг втрачати хвіст;
- timeline неправильно малював інтервали через 00:00.

Реалізовано в `v1071_features.py`:

- заміна тільки `source='auto'`, ручні інтервали не видаляються;
- автоматичне розпізнавання після імпорту тільки нових записів;
- простий вибір шайби не змінює дані;
- коректне попередження при невиявленому колі;
- circular-run helper для межі 00:00;
- правильне split-відображення midnight interval на шкалі;
- `main.APP_VERSION`, `VERSION.txt`, `taxo_app.py` синхронізовані на `10.7-r1`;
- додано `tests/test_v10_7_r1.py`;
- аудит: `docs/maintenance/AUDIT_10.7-r1_TACHOGRAPH.md`;
- release notes: `docs/releases/RELEASE_NOTES_v10.7-r1.md`.

## VERIFY

Source/START workflow для актуального head запущений: run `36535317613`.

## NEXT

1. Дочекатися green regression/START verify.
2. Якщо green — відкрити PR 10.7-r1, перевірити PR gates.
3. Видати immutable fast-test `v10.7-r1` + `Taxo_v10_7_candidate_r1_START.zip`.
4. Дати власнику пряме посилання для тестування.
5. Після ручного тесту перейти до 10.7-r2 з наступним підтвердженим дефектом.

## PRESERVED

- stable `v10.3` не пересувається;
- `v10.6-r10` і всі historical tags/releases immutable;
- основний `worklog`, табель, plan/fact і робоча БД цим slice не змінюються;
- незалежний зовнішній аудит використовується як список гіпотез, але код змінюється лише після локального підтвердження дефекту.

## BLOCKED

Немає; очікується CI/START verify.
