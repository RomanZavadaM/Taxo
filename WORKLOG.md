# WORKLOG — Taxo

**Оновлено:** 30.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.6-r10** / `v10.6-r10`  
**Latest issued fast-test:** **10.8-r3** / `v10.8-r3` → `d8ec901b9b80f74b5b85cd1bda202dd58c86a7bd`  
**Issued START:** `Taxo_v10_8_candidate_r3_START.zip` · SHA-256 `aa75661658194425f7dc95c353516a6f1c44f98040989f72d402985e2f023d00`  
**Active integration:** PR #105 → `main`; власник прямо наказав повний checkpoint («зливай в main»)  
**Next code revision:** **10.8-r4**  
**Live ledger:** Issue #61

## 10.8-r3 — READY FOR MAIN

- виправлено падіння відомості ТЦК на даті `ДД.ММ.РРРР`;
- підтримуються `ДД.ММ.РРРР`, ISO, `date`, `datetime`;
- додано «Реквізити ТЦК» у картці ТЗ;
- реквізити необов'язкові для звичайної картки;
- використано існуючу `vehicle_military_transport_statement_data`;
- regression/source START gate пройдено;
- Windows exact-issued gate — success;
- macOS exact-issued gate — success;
- `v10.8-r3` видано, тег/джерело не рухати;
- код r3 заморожений; після merge тільки документаційне/релізне завершення без зміни коду.

## DOING

1. Merge PR #105 у `main`.
2. Перевірити main CI.
3. Доповнити release `v10.8-r3` повними Windows/macOS пакетами з exact issued source `d8ec901b9b80f74b5b85cd1bda202dd58c86a7bd`.
4. Оновити `PROJECT_STATE.md`, release index і Issue #61.
5. Підчистити лише явно службові/одноразові елементи, не видаляючи історичні regression anchors.

## NEXT

Після повного checkpoint 10.8-r3 наступна кодова ревізія — **10.8-r4**.
