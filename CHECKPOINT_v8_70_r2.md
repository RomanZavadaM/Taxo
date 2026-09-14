# Taxo v8.70 candidate r2 checkpoint

- Date: 14.09.2026
- Base: verified v8.70 r1 candidate, itself based on v8.66 r10.
- Stable GitHub main remains v8.65 (`f9101c1a41d7c036bade5ce66989171399189d4b`).
- r2 completely replaces the scanned-background waybill renderer with a two-page vector form № 1-АП.
- Route records now own outbound/return stop schedules for the reverse side.
- Doctors and mechanics have a separate per-date I/II-shift register used by waybill generation.
- Driver personnel number, vehicle garage number and company waybill series/column/brigade are additive database fields.
- Existing data is preserved; tachograph recognition is unchanged.
- Delivery: START.bat candidate pending the user's visual/printing review.
