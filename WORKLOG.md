# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main head after docs closeout:** `01c8c90d90f1be4641796f6aedcbd7c4ad7d9da4`  
**Latest issued fast-test:** Taxo **10.6-r7** / `v10.6-r7`  
**Issued r7 source/tag target:** `e3f1666bafbd82e37ac2e63b08bfed2d265bae30` — immutable by project policy  
**Work branch:** `work/v10.6-r7-vehicle-doc-actions-responsive`  
**Live ledger:** Issue #61

## DONE — 10.6-r7

Причина: у картці документів конкретного транспортного засобу п'ять дій документа та прапорець «Показувати архів» були складені в один горизонтальний ряд і могли обрізатися на вузьких/масштабованих екранах.

Виконано:

- [x] додано outer runtime layer `v1067_features.py`;
- [x] action-bar переведено у responsive `grid` у тому самому контейнері;
- [x] збережено «Додати документ», «Редагувати», «Архівувати», «Відкрити копію», «Оновити» та «Показувати архів»;
- [x] порядок, callback-и та `show_archived` не замінюються;
- [x] таблиця документів і її горизонтальна/вертикальна прокрутка не змінені;
- [x] document schema, archive semantics, копії, строки дії, vehicle data та business logic не змінені;
- [x] `v1067` встановлено outermost поверх `v1066`;
- [x] START packaging guard вимагає `v1067_features.py`;
- [x] regression contract: `tests/test_v10_6_r7.py`;
- [x] exact-source regression: **562/562 OK**;
- [x] clean START verify run: `36463667268` — success;
- [x] Actions artifact: `Taxo_v10_6_candidate_r7_START`, ID `10989440117`;
- [x] prerelease publisher run: `36467902934` — success;
- [x] tag/release `v10.6-r7` вказує точно на `e3f1666bafbd82e37ac2e63b08bfed2d265bae30`;
- [x] GitHub Release asset: `Taxo_v10_6_candidate_r7_START.zip`;
- [x] Release asset SHA-256: `5fe124b6865419a14f4073d9bbb54efe18a3142a1e44aa03dc1339554e2a49fd`;
- [x] checksum manifest: `SHA256SUMS_v10_6_r7.txt`;
- [x] one-shot identity/publisher workflows прибрані після успішного виконання.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r7  
START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r7/Taxo_v10_6_candidate_r7_START.zip

## PRESERVED

- `v10.6-r7` issued source/tag не пересувається й не переписується;
- `v10.6-r6` і попередні issued fast-test також лишаються immutable;
- `v10.6-r3` лишається latest full multi-platform checkpoint у `main`;
- stable `v10.3` не пересувається;
- business logic, plan/fact, шляхівки та тахографічні дані r7 не змінює;
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Наступна кодова ревізія — тільки **10.6-r8**. Починати її після нового pre-flight/audit. `10.6-r7` у `main` не зливати без нової прямої команди власника.

## BLOCKED

Немає.
