# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main head after docs closeout:** `01c8c90d90f1be4641796f6aedcbd7c4ad7d9da4`  
**Latest issued fast-test:** Taxo **10.6-r5** / `v10.6-r5`  
**Issued r5 source/tag target:** `118d4111e183528c49e8060e8782479fa4436377` — immutable by project policy  
**Active code revision:** **10.6-r6**  
**Work branch:** `work/v10.6-r6-vehicle-toolbar-responsive`  
**Scope:** адаптивна панель команд реєстру транспортних засобів; UI-only  
**Live ledger:** Issue #61

## DOING — 10.6-r6

- [x] pre-flight: stable/main/r5 release перевірені, відкритих PR немає;
- [x] підтверджено UI-дефект: шість кнопок базового `build_vehicles` + довгий r1-прапорець складаються в один горизонтальний ряд;
- [x] створено work-гілку від post-r5 docs/process head;
- [x] додано outer runtime layer `v1066_features.py`;
- [x] усі шість дій і прапорець збережені в початковому порядку;
- [x] контроли переносяться на наступний рядок за фактичною шириною toolbar;
- [x] існуючі callback-и та `BooleanVar` фільтра не замінюються;
- [x] «Сховати неактивні автомобілі» лишається `True` за замовчуванням;
- [x] дані ТЗ, статуси, документи й БД не змінюються;
- [x] додано regression contract `tests/test_v10_6_r6.py`;
- [ ] синхронізувати `main.APP_VERSION` = `10.6-r6`;
- [ ] отримати green full regression / clean START на exact source;
- [ ] заморозити exact issued source і опублікувати immutable `v10.6-r6` START prerelease;
- [ ] синхронізувати docs/state/ledger після видачі.

## PRESERVED

- `v10.6-r5` і попередні issued fast-test не пересуваються й не переписуються;
- `v10.6-r3` лишається latest full multi-platform checkpoint у `main`;
- stable `v10.3` не пересувається;
- business logic, plan/fact, шляхівки та тахографічні дані r6 не змінює;
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Синхронізувати runtime identity, пройти final regression/START verify і видати `v10.6-r6` як окремий GitHub prerelease.

## BLOCKED

Немає.
