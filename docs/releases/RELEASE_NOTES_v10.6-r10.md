# Taxo 10.6-r10 — виправлення експорту табеля П-5

**Дата:** 28.09.2026  
**Тип:** candidate / fast-test  
**Stable baseline:** `v10.3`  
**Latest full checkpoint у `main`:** `v10.6-r3`

## Виправлено

Під час реального формування PDF офіційного табеля П-5 виникала помилка:

`TypeError: export_p5_pdf() got multiple values for argument 'edrpou'`.

Причина була у compatibility-layer `v1043_features.py`: він перевіряв тільки keyword-параметр `edrpou`, тоді як актуальний Reports UI передавав ЄДРПОУ позиційно. Wrapper додавав другий `edrpou`, і Python відхиляв виклик.

У 10.6-r10:

- позиційний та keyword `edrpou` нормалізуються до одного значення;
- явно переданий ЄДРПОУ зберігається;
- порожнє значення отримує fallback з реквізитів підприємства;
- виправлення діє для PDF та XLSX П-5;
- historical `v1043_features.py` не переписується — r10 встановлює зовнішній compatibility layer;
- додано regression-тести на positional/keyword виклики PDF/XLSX.

## Не змінено

- розрахунок табеля та його коди;
- plan/fact semantics;
- робочий час, графіки та тахографічні дані;
- БД і схема даних;
- інші звіти;
- видані tags/releases.

## Repository hygiene correction

Під час окремого post-r9 cleanup було виявлено, що historical publisher/build workflow-файли використовуються regression suite як immutable release anchors. Вони відновлені; старі релізи при цьому не перевидаються і не пересуваються.

## Нумерація

`10.6-r10` завершує ревізії 10.6. Після його immutable issuance наступна кодова ревізія — тільки **10.7-r1**.
