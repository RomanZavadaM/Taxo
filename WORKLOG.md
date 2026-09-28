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
**Work branch:** `work/v10.6-r9-vehicle-document-header-responsive`  
**Scope:** адаптивний header картки документів ТЗ; UI-only  
**Live ledger:** Issue #61

## DOING — 10.6-r9

- [x] pre-flight: stable/main/r8 release перевірені, відкритих PR немає;
- [x] підтверджено UI-дефект: назва авто і довгий summary стану документів пакуються в один рядок left/right без переносу;
- [x] створено work-гілку від post-r8 docs head `54d111c489720ecb4ff13f97a40dd6779fc50bb8`;
- [x] додано outer runtime layer `v1069_features.py`;
- [x] header вимірює фактичні `winfo_reqwidth()` двох label-ів;
- [x] якщо вони вміщаються — лишаються в одному рядку;
- [x] якщо не вміщаються — summary переходить на другий рядок;
- [x] stacked summary отримує динамічний wraplength у межах 240…900 px;
- [x] `summary_var`, розрахунок стану документів, таблиця, action-bar і обидві прокрутки не змінені;
- [x] document schema, архівні правила, копії, строки дії, SQL та business logic не змінені;
- [x] `v1069` встановлено outermost поверх `v1068`;
- [x] START packaging guard вимагає `v1069_features.py`;
- [x] regression contract: `tests/test_v10_6_r9.py`;
- [x] історичний r8 regression переведено на historical identity contract;
- [x] `main.APP_VERSION` синхронізовано як `10.6-r9`, one-shot updater прибрано;
- [ ] отримати green full regression / clean START на exact source;
- [ ] опублікувати immutable `v10.6-r9` START prerelease;
- [ ] синхронізувати docs/state/ledger після видачі.

## PRESERVED

- `v10.6-r8` і попередні issued fast-test не пересуваються й не переписуються;
- `v10.6-r3` лишається latest full multi-platform checkpoint у `main`;
- stable `v10.3` не пересувається;
- document status/business logic, plan/fact, шляхівки та тахографічні дані r9 не змінює;
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Пройти final regression/START verify на точному r9 source, заморозити issued SHA і видати `v10.6-r9` як окремий GitHub prerelease.

## BLOCKED

Немає.
