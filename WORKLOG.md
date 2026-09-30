# WORKLOG — Taxo

**Оновлено:** 30.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.8-r3** / `v10.8-r3`  
**Latest integrated code checkpoint:** **10.8-r3** — PR #105 merged to `main`  
**Main merge:** `db444a37ead421c8083558cfcf81ee97adc241f6`  
**Issued source/tag:** `v10.8-r3` → `d8ec901b9b80f74b5b85cd1bda202dd58c86a7bd`  
**Issued START:** `Taxo_v10_8_candidate_r3_START.zip` · SHA-256 `aa75661658194425f7dc95c353516a6f1c44f98040989f72d402985e2f023d00`  
**Full package run:** `36741933852` — success  
**Next code revision:** **10.8-r4**  
**Live ledger:** Issue #61

## DONE — 10.8-r3

Тема: **відомість ТЦК — дата та реквізити транспортного засобу**.

### Реалізовано

- виправлено падіння відомості ТЦК на звичайній для Taxo даті `ДД.ММ.РРРР`;
- підтримуються `ДД.ММ.РРРР`, ISO, `date`, `datetime`;
- додано «Реквізити ТЦК» у картці ТЗ;
- реквізити необов'язкові для звичайної картки;
- використано існуючу `vehicle_military_transport_statement_data`;
- додано regression-тести для дати та round-trip реквізитів;
- exact issued source/tag заморожено й не пересувалось.

### Інтеграція

- PR #105 merged у `main`;
- merge commit: `db444a37ead421c8083558cfcf81ee97adc241f6`;
- stable `v10.3` не змінювався.

### Повний multi-platform checkpoint

Run `36741933852` завершився **success** по всіх jobs:

- exact-source verify/regression;
- Windows x64 Portable + Setup;
- Windows 7 SP1 x64 Portable + Setup;
- Windows 7 Python 3.8 + PE compatibility gate;
- macOS arm64 Portable;
- macOS x86_64 Portable;
- platform SHA-256 manifests;
- загальний `SHA256SUMS_v10_8_r3_ALL.txt`;
- фінальна перевірка повного набору release assets.

Усі binary assets зібрано з exact issued source `d8ec901b9b80f74b5b85cd1bda202dd58c86a7bd`.

## CLEANUP

- актуальний стан зведено у `PROJECT_STATE.md`, `WORKLOG.md` та release index;
- службовий full-package workflow лишено на окремій `ops/v10.8-r3-full-package`, а не в `main`;
- історичні workflows/regression anchors не видалялись;
- старі issued tags/releases не змінювались;
- робочі БД, скани, кеші та персональні дані не публікувались.

## NEXT

Наступна кодова ревізія — **10.8-r4**. Перед кодовими змінами виконати pre-flight за `START_HERE.md` і взяти наступну підтверджену помилку/недоробку з аудиту, не повертаючись до замороженого r3.
