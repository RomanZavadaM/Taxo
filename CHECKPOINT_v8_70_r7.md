# Taxo v8.70 candidate r7 — checkpoint

Date: 2026-09-15
Base: published `main` v8.70 r6 (`9ce67caea5257e334ac6cac98fae7813abccea51`)
Branch: `work/v8.70-route-distance-r7`

## Planned route mileage

- `routes.planned_distance_km` stores an optional positive whole-kilometre plan for one complete exact route scenario.
- Blank values remain valid and do not block route use or waybill issue.
- The route catalogue shows the plan and the route editor labels its full-scenario meaning explicitly.

## Waybill and checks

- `waybills.planned_distance_km` snapshots the plan used for an issued document.
- The form prints planned mileage separately from actual odometer-derived mileage.
- A start odometer plus plan shows a forecast end in the editor; this value is never stored as an actual reading.
- When both actual readings exist, deviation beyond `max(10 km, 10% of plan)` produces a non-blocking warning.
- Existing decreasing-reading and previous-history warnings remain active.
- The future `tachograph` source can use the same plan-versus-actual comparison without changing planned data.

## Safety and distribution

- Database migration is additive and does not delete existing records.
- Tachograph recognition is unchanged.
- No user database or personal data is included.
- Routine testing uses `START.bat`; executable packaging is not run for r7.
