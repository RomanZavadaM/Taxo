# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main head after docs closeout:** `01c8c90d90f1be4641796f6aedcbd7c4ad7d9da4`  
**Latest issued fast-test:** Taxo **10.6-r6** / `v10.6-r6`  
**Issued r6 source/tag target:** `90ab67ae00be381f8b2bc14e18f9614574e3493f` — immutable by project policy  
**Work branch:** `work/v10.6-r6-vehicle-toolbar-responsive`  
**Live ledger:** Issue #61

## DONE — 10.6-r6

Причина: у реєстрі транспортних засобів шість основних кнопок і довгий прапорець «Сховати неактивні автомобілі» могли не вміститися в один горизонтальний ряд на вузьких/масштабованих екранах.

Виконано:

- [x] додано outer runtime layer `v1066_features.py`;
- [x] усі шість основних дій і прапорець збережені в початковому порядку;
- [x] контроли автоматично переносяться на наступний рядок відповідно до фактичної ширини toolbar;
- [x] існуючі callback-и та `BooleanVar` фільтра не замінюються;
- [x] «Сховати неактивні автомобілі» лишається `True` за замовчуванням;
- [x] дані ТЗ, статуси, документи, БД і business logic не змінені;
- [x] `v1066` встановлено outermost поверх `v1065`;
- [x] START packaging guard вимагає `v1066_features.py`;
- [x] regression contract: `tests/test_v10_6_r6.py`;
- [x] exact-source regression: **554/554 OK**;
- [x] clean START verify run: `36462366765` — success;
- [x] Actions artifact: `Taxo_v10_6_candidate_r6_START`, ID `10988412209`;
- [x] prerelease publisher run: `36462529738` — success;
- [x] tag/release `v10.6-r6` вказує точно на `90ab67ae00be381f8b2bc14e18f9614574e3493f`;
- [x] GitHub Release asset: `Taxo_v10_6_candidate_r6_START.zip`;
- [x] Release asset SHA-256: `7493202b3282ffba5238342136dd3a19a5cd7f663514c12eb3827451eff83e79`;
- [x] checksum manifest: `SHA256SUMS_v10_6_r6.txt`;
- [x] one-shot identity/publisher workflows прибрані після успішного виконання.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r6  
START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r6/Taxo_v10_6_candidate_r6_START.zip

## PRESERVED

- `v10.6-r6` issued source/tag не пересувається й не переписується;
- `v10.6-r5` і попередні issued fast-test також лишаються immutable;
- `v10.6-r3` лишається latest full multi-platform checkpoint у `main`;
- stable `v10.3` не пересувається;
- business logic, plan/fact, шляхівки та тахографічні дані r6 не змінює;
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Наступна кодова ревізія — тільки **10.6-r7**. Починати її після нового pre-flight/audit. `10.6-r6` у `main` не зливати без нової прямої команди власника.

## BLOCKED

Немає.
