# Taxo 10.6-r10 — виправлення експорту табеля П-5

**Дата:** 29.09.2026  
**Тип:** candidate / full multi-platform checkpoint  
**Stable baseline:** `v10.3`  
**Latest full checkpoint:** `v10.6-r10`

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

## Перевірки

- exact-source regression: **588/588 OK**;
- clean START verify: `36476665666` — success;
- Windows PR gate: `36479012210` — success;
- macOS PR gate: `36479012232` — success;
- full package build: `36485005797` — усі чотири platform jobs зібрані й перевірені;
- binary publication: `36485643153` — success;
- Windows 7 PE compatibility gate — success.

## Повний комплект збірок

У той самий release `v10.6-r10`, без пересування tag, додано виконувані пакети, зібрані з exact issued source `0baad010d0c0d4f29db62f26c29d512c71058928`:

- `Taxo_v10_6_candidate_r10_Windows_x64_Portable.zip`;
- `Taxo_v10_6_candidate_r10_Setup_Windows_x64.exe`;
- `Taxo_v10_6_candidate_r10_Windows7_x64_Portable.zip`;
- `Taxo_v10_6_candidate_r10_Setup_Windows7_x64.exe`;
- `Taxo_v10_6_candidate_r10_macOS_arm64_Portable.zip`;
- `Taxo_v10_6_candidate_r10_macOS_x86_64_Portable.zip`;
- platform SHA-256 manifests;
- `SHA256SUMS_v10_6_r10_ALL.txt`;
- раніше виданий `Taxo_v10_6_candidate_r10_START.zip` збережено без зміни.

## Не змінено

- розрахунок табеля та його коди;
- plan/fact semantics;
- робочий час, графіки та тахографічні дані;
- БД і схема даних;
- інші звіти;
- immutable source/tag `v10.6-r10`.

## Repository hygiene

Historical publisher/build workflow-файли, що використовуються regression suite як immutable release anchors, збережені. Старі релізи не пересуваються і не перевидаються.

## Нумерація

`10.6-r10` завершує ревізії 10.6. Наступна кодова ревізія — тільки **10.7-r1**.
