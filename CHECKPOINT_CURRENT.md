# Taxo v8.66 candidate r10 — checkpoint

Date: 2026-09-14

## Authoritative state
- Stable `main`: v8.65 @ `f9101c1a41d7c036bade5ce66989171399189d4b`.
- Candidate branch: `work/v8.66-ui-polish-r10`.
- Verified code commit: `7076a8dd24937e0925a87e03789e03bb8159ce0d`.
- `main.py` Git blob: `21c3036237c6d50619890154a9c952f042475ac4`.
- `tachograph.py` Git blob: `d5d8e71e0601e951b39432ade123e2be99509cd0`.
- Recognition algorithm is unchanged.

## r9 route model retained
- User-facing `Шаблони маршрутів` is removed.
- One `Маршрут` = one exact time scenario.
- Display/selection label = `номер / назва` only.
- Route stores default vehicle, shift type, description, notes and exact work/driving segments.
- Workday editor uses `Застосувати маршрут`; no separate template selector is shown.
- Legacy `route_templates` / `route_template_segments` are preserved as a safety layer and copied automatically into the unified route model.

## r10 tachograph UI
- Right work area uses two sub-tabs: `Перегляд` and `Результати`.
- The scan catalog remains on the left and can still be hidden/restored.
- `Перегляд` contains disc metadata, 24-hour timeline and scan preview.
- `Результати` contains recognition refresh/edit actions, statistics/protocol actions and the interval table.
- Both sub-tabs have independent vertical scrollbars.
- Scan preview keeps independent vertical + horizontal scrolling.
- Interval table keeps independent vertical + horizontal scrolling.
- The previous vertical sash between preview/results is removed.
- Quick navigation buttons connect both sub-tabs: `До результатів →` / `← До перегляду`.

## Regression protection
- Authoritative r8 monthly-schedule behavior is retained: the selected schedule date controls month/year, Refresh marks the PDF stale, and Open PDF regenerates the current month when required.
- The canonical GitHub candidate differs from the older local r10 build only by retaining the newer r8 monthly-schedule implementation already published on GitHub.

## Verification
- Exact GitHub candidate exported as an Actions artifact and tested locally.
- Python compile PASS for `main.py`, `tachograph.py`, `attestation_render.py`.
- TAHO layout PASS at 900x600, 1024x700, 1200x760 and 1400x780.
- Both TAHO sub-tab vertical scrollbars were exercised at 900x600.
- All critical Results buttons are mapped and inside the window at 900x600.
- Monthly schedule source date 13.09.2026 resolves to September 2026.
- Dirty PDF state regenerates before opening; repeated dirty-state test regenerated twice.

Do not merge into stable `main` before manual Windows regression testing is confirmed.
