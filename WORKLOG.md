# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main head after docs closeout:** `01c8c90d90f1be4641796f6aedcbd7c4ad7d9da4`  
**Latest issued fast-test:** Taxo **10.6-r7** / `v10.6-r7`  
**Issued r7 source/tag target:** `e3f1666bafbd82e37ac2e63b08bfed2d265bae30` — immutable by project policy  
**Active code revision:** **10.6-r8**  
**Work branch:** `work/v10.6-r8-vehicle-document-form-responsive`  
**Scope:** адаптивна форма додавання/редагування документа ТЗ; UI-only  
**Live ledger:** Issue #61

## DOING — 10.6-r8

- [x] pre-flight: stable/main/r7 release перевірені, відкритих PR немає;
- [x] підтверджено UI-дефект у `VehicleDocumentsWindow._form`: багато вертикальних рядків, fixed `wraplength=520`, нижня кнопка «Зберегти»;
- [x] створено work-гілку від post-r7 docs head `f3a80ceb3f6120786572768467400bc84b4ec8f6`;
- [x] додано outer runtime layer `v1068_features.py`;
- [x] на висоті <620 px стандартні вертикальні відступи форми ущільнюються;
- [x] поле «Примітка» на невисокому вікні зменшується з 4 до 3 рядків;
- [x] пояснення про архівацію та поточну копію отримують динамічний `wraplength` 240…520 px;
- [x] існуючий `_form()` і його `save()` closure не переписуються;
- [x] валідація строків, архівація, копії документів, SQL і DB semantics не змінюються;
- [x] `v1068` встановлено outermost поверх `v1067`;
- [x] START packaging guard вимагає `v1068_features.py`;
- [x] regression contract: `tests/test_v10_6_r8.py`;
- [x] `main.APP_VERSION` синхронізовано як `10.6-r8`, one-shot updater прибрано;
- [ ] отримати green full regression / clean START на exact source;
- [ ] опублікувати immutable `v10.6-r8` START prerelease;
- [ ] синхронізувати docs/state/ledger після видачі.

## PRESERVED

- `v10.6-r7` і попередні issued fast-test не пересуваються й не переписуються;
- `v10.6-r3` лишається latest full multi-platform checkpoint у `main`;
- stable `v10.3` не пересувається;
- document save/business logic, plan/fact, шляхівки та тахографічні дані r8 не змінює;
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Пройти final regression/START verify на точному r8 source, заморозити issued SHA і видати `v10.6-r8` як окремий GitHub prerelease.

## BLOCKED

Немає.
