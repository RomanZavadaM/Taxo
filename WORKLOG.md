# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main head after docs closeout:** `01c8c90d90f1be4641796f6aedcbd7c4ad7d9da4`  
**Latest issued fast-test:** Taxo **10.6-r6** / `v10.6-r6`  
**Issued r6 source/tag target:** `90ab67ae00be381f8b2bc14e18f9614574e3493f` — immutable by project policy  
**Active code revision:** **10.6-r7**  
**Work branch:** `work/v10.6-r7-vehicle-doc-actions-responsive`  
**Scope:** адаптивна панель дій картки документів транспортного засобу; UI-only  
**Live ledger:** Issue #61

## DOING — 10.6-r7

- [x] pre-flight: stable/main/r6 release перевірені, відкритих PR немає;
- [x] підтверджено UI-дефект у `VehicleDocumentsWindow._build`: п'ять кнопок + «Показувати архів» в одному горизонтальному рядку;
- [x] таблиця документів уже має вертикальну й горизонтальну прокрутку — її не змінюємо;
- [x] створено work-гілку від post-r6 docs head;
- [x] додано outer runtime layer `v1067_features.py`;
- [x] action-bar переводиться у responsive `grid` у тому самому контейнері;
- [x] порядок, callback-и та `show_archived` збережені;
- [x] document schema, archive semantics, копії та строки дії не змінюються;
- [x] додано regression contract `tests/test_v10_6_r7.py`;
- [ ] синхронізувати `main.APP_VERSION` = `10.6-r7`;
- [ ] отримати green full regression / clean START на exact source;
- [ ] опублікувати immutable `v10.6-r7` START prerelease;
- [ ] синхронізувати docs/state/ledger після видачі.

## PRESERVED

- `v10.6-r6` і попередні issued fast-test не пересуваються й не переписуються;
- `v10.6-r3` лишається latest full multi-platform checkpoint у `main`;
- stable `v10.3` не пересувається;
- business logic, plan/fact, шляхівки та тахографічні дані r7 не змінює;
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Синхронізувати runtime identity, пройти final regression/START verify і видати `v10.6-r7` як окремий GitHub prerelease.

## BLOCKED

Немає.
