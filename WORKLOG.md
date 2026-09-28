# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main head after docs closeout:** `01c8c90d90f1be4641796f6aedcbd7c4ad7d9da4`  
**Latest issued fast-test:** Taxo **10.6-r5** / `v10.6-r5`  
**Issued r5 source/tag target:** `118d4111e183528c49e8060e8782479fa4436377` — immutable by project policy  
**Work branch:** `work/v10.6-r5-vehicle-doc-report-responsive`  
**Live ledger:** Issue #61

## DONE — 10.6-r5

Причина: у звіті «Стан документів транспортних засобів» дата, кнопка календаря і два довгі прапорці були складені в один горизонтальний ряд. На вузьких або масштабованих екранах крайні елементи могли виходити за видиму область.

Виконано:

- [x] додано outer runtime layer `v1065_features.py`;
- [x] група `дата + поле + Дата…` не розривається;
- [x] прапорці «Тільки авто в експлуатації» та «Тільки проблемні / попередження» переносяться на наступний рядок при нестачі ширини;
- [x] «Тільки авто в експлуатації» лишається `True` за замовчуванням;
- [x] таблиця, вертикальна й горизонтальна прокрутка не змінені;
- [x] SQL, правила документів і експорт PDF/Excel не змінені;
- [x] `v1065` встановлено outermost поверх `v1064`;
- [x] START packaging guard вимагає `v1065_features.py`;
- [x] regression contract: `tests/test_v10_6_r5.py`;
- [x] exact-source regression: **546/546 OK**;
- [x] clean START verify run: `36452858366` — success;
- [x] Actions artifact: `Taxo_v10_6_candidate_r5_START`, ID `10984119034`;
- [x] prerelease publisher run: `36461104704` — success;
- [x] tag/release `v10.6-r5` вказує точно на `118d4111e183528c49e8060e8782479fa4436377`;
- [x] GitHub Release asset: `Taxo_v10_6_candidate_r5_START.zip`;
- [x] Release asset SHA-256: `8586e5aa6c07860ea4aeda5eaf76b409acc4719b41a9b60da991c3ca14ec27c9`;
- [x] checksum manifest: `SHA256SUMS_v10_6_r5.txt`.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r5  
START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r5/Taxo_v10_6_candidate_r5_START.zip

## PRESERVED

- `v10.6-r5` issued source/tag не пересувається й не переписується;
- `v10.6-r4` також лишається immutable fast-test;
- `v10.6-r3` лишається latest full multi-platform checkpoint у `main`;
- stable `v10.3` не пересувається;
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Наступна кодова ревізія — тільки **10.6-r6**. Починати її після нового pre-flight/audit. `10.6-r5` у `main` не зливати без нової прямої команди власника.

## BLOCKED

Немає.
