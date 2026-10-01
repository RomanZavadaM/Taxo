# Taxo 10.9-r1 — підсумок інтегрованого checkpoint

Дата: 01.10.2026.

## Інтеграція

За прямою командою власника кумулятивний PR #118 було інтегровано в `main`.

- main merge: `843a38243dd4eeeb02b40f8de59cc630ef4dce09`;
- immutable tag/source: `v10.9-r1` → `b0eebbf88b22fbd7761544640d9804416a328acb`;
- exact-source regression: 730/730 OK;
- START: `Taxo_v10_9_candidate_r1_START.zip`;
- START SHA-256: `0c819f9f3e4b31f58e6b86e2b4f1d72086901c0bd2a26a499e4c17f6de9c1766`.

## Повний комплект

Full-package run `36857771398` завершився успішно. До release `v10.9-r1` додано:

- Windows x64 Portable;
- Windows x64 Setup;
- Windows 7 SP1 x64 Portable;
- Windows 7 SP1 x64 Setup;
- macOS arm64 Portable;
- macOS x86_64 Portable;
- platform SHA-256 manifests;
- `SHA256SUMS_v10_9_r1_ALL.txt`.

Windows 7 compatibility перевірена на окремій Python 3.8 / PyInstaller 5.13.2 лінії з PE compatibility gate.

## Функціональний та архітектурний підсумок

Кумулятивно від 10.8-r4 до 10.9-r1 у головну лінію ввійшли СТОІР, прогноз ТО й заявки на ремонт, а також послідовне розвантаження монолітного `main.py`: `output_files.py`, `feature_layers.py`, `application_context.py`, `backup_migration.py`, `database_runtime.py`, `data_access.py`.

Архітектурний напрямок для наступних великих функцій: `domain → service → repository/data access → infrastructure`, UI — окремий зовнішній шар. Це не означає перехід на мікросервіси: Taxo лишається модульним desktop monolith з чіткими внутрішніми межами.

## Cleanup

Після інтеграції закрито проміжні stacked/tupik PR, які більше не повинні зливатися окремо: #108–#113, #103, #94, #93, #91. Історичні tags/releases та Git history збережені. Старі branch refs не використовуються як кодова база.

## Далі

- stable лишається `v10.3` до окремого рішення власника;
- `v10.9-r1` заморожений;
- наступна кодова зміна: **10.9-r2**;
- старт нової роботи тільки від актуального `main`.