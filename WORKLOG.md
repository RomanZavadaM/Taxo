# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main head after docs closeout:** `01c8c90d90f1be4641796f6aedcbd7c4ad7d9da4`  
**Latest issued fast-test:** Taxo **10.6-r8** / `v10.6-r8`  
**Issued r8 source/tag target:** `09f0e6e6cf3809b6d0efc6c9cdad7937a44d78d3` — immutable by project policy  
**Active code revision:** **10.6-r9**  
**Work branch:** `work/v10.6-r9-vehicle-doc-header-responsive`  
**Scope:** адаптивний header картки документів транспортного засобу; UI-only  
**Live ledger:** Issue #61

## DOING — 10.6-r9

- [x] pre-flight: stable/main/r8 release перевірені, відкритих PR немає;
- [x] підтверджено UI-дефект: назва авто та довгий `summary_var` конкурують за один horizontal header-row;
- [x] додано outer runtime layer `v1069_features.py`;
- [x] широкий header лишається в один ряд;
- [x] при нестачі ширини title + summary переходять у два рядки;
- [x] вузький summary отримує динамічний `wraplength`;
- [x] `summary_var`, розрахунок стану документів, таблиця, action-bar, архівні правила та DB semantics не змінюються;
- [x] `v1069` встановлюється outermost поверх `v1068`;
- [x] START packaging guard вимагає `v1069_features.py`;
- [x] додано regression contract `tests/test_v10_6_r9.py`;
- [x] r8 regression переведено в historical identity mode;
- [ ] синхронізувати `main.APP_VERSION` = `10.6-r9`;
- [ ] отримати green full regression / clean START на exact source;
- [ ] опублікувати immutable `v10.6-r9` START prerelease;
- [ ] синхронізувати docs/state/ledger після видачі.

## PRESERVED

- `v10.6-r8` і попередні issued fast-test не пересуваються й не переписуються;
- `v10.6-r3` лишається latest full multi-platform checkpoint у `main`;
- stable `v10.3` не пересувається;
- document status calculation, архівування, копії, plan/fact, шляхівки та тахографічні дані r9 не змінює;
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Синхронізувати runtime identity, пройти final regression/START verify і видати `v10.6-r9` як окремий GitHub prerelease.

## BLOCKED

Немає.
