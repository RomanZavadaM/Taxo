# Taxo 10.11-r9 — workflow supply-chain hardening

**Дата:** 06.11.2026  
**Статус:** робочий candidate slice; ще не release.  
**Stable:** без змін, `v10.10-r5`.  
**Попередній immutable candidate:** `v10.11-r8`.

## Мета

Закрити finding #11 з Issue #175: active GitHub Actions workflows не повинні виконувати рухомий сторонній код через major refs `@v4/@v5`.

## Зміна

У всіх active workflow офіційні actions pinned до конкретних commit SHA, звірених з поточними major refs GitHub 06.11.2026:

- `actions/checkout@v4` → `11d5960a326750d5838078e36cf38b85af677262`;
- `actions/setup-python@v5` → `a26af69be951a213d495a4c3e4e4022e16d87065`;
- `actions/upload-artifact@v4` → `ea165f8d65b6e75b540449e92b4886f43607fa02`.

Після SHA лишено коментар `# v4` / `# v5`, щоб майбутнє контрольоване оновлення major line було зрозумілим людині.

## Межі

Історичні workflow у `docs/history/workflows/` не переписуються: вони є архівом виданих ревізій. Runtime/business logic, БД, UX і build naming не змінюються.

## Maintenance rule

Оновлення action допускається лише окремою зміною: звірити офіційний major ref у репозиторії action, зафіксувати новий commit SHA, пройти повний platform CI і regression. Не повертатися до рухомих `@vN` у active workflows.

## Regression

`tests/test_v10_11_r9.py` перевіряє:
- current identity r9;
- усі supported official action refs в active workflows мають 40-символьний SHA;
- SHA збігаються з зафіксованим allowlist;
- рухомі `@v4/@v5` не повернулися;
- коментар major-version поруч із pin збережений.
