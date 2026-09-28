# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main head after docs closeout:** `01c8c90d90f1be4641796f6aedcbd7c4ad7d9da4`  
**Latest issued fast-test:** Taxo **10.6-r4** / `v10.6-r4`  
**Issued r4 source/tag target:** `3961bde3708a13de6352b8c30438d2b65351110c` — immutable  
**Active code revision:** **10.6-r5**  
**Work branch:** `work/v10.6-r5-vehicle-doc-report-responsive`  
**Scope:** адаптивна панель фільтрів звіту «Стан документів транспортних засобів»; UI-only  
**Live ledger:** Issue #61

## DOING — 10.6-r5

- [x] pre-flight: підтверджено r4 immutable і current main 10.6-r3;
- [x] визначено конкретний UI-дефект: дата + календар + два довгі прапорці в одному горизонтальному рядку;
- [x] створено окрему work-гілку поверх post-r4 state;
- [x] додано outer runtime layer `v1065_features.py`;
- [x] дата/поле/календар збережені однією логічною групою;
- [x] прапорці можуть переноситися на наступний рядок при нестачі ширини;
- [x] business logic, SQL, export та значення фільтрів не змінюються;
- [x] фільтр активних ТЗ лишається `True` за замовчуванням;
- [x] додано regression contract `tests/test_v10_6_r5.py`;
- [ ] отримати green full regression / clean START на exact source;
- [ ] заморозити exact issued source і опублікувати immutable `v10.6-r5` START prerelease;
- [ ] синхронізувати release notes / PROJECT_STATE / ledger після видачі.

## PRESERVED

- `v10.6-r4` не пересувається й не переписується;
- `v10.6-r3` лишається latest full multi-platform checkpoint у `main`;
- stable `v10.3` не пересувається;
- таблиця звіту документів ТЗ і обидві прокрутки лишаються;
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Дочекатися green source-package CI на exact r5 source, потім опублікувати окремий immutable START prerelease `v10.6-r5`.

## BLOCKED

Немає.
