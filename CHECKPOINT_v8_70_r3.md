# Taxo v8.70 candidate r3 checkpoint

- Date: 14.09.2026.
- Base: preserved v8.70 candidate r2.
- Added a unified employee register, multi-role employee cards, personnel shifts and monthly personnel time summary.
- Migrates legacy drivers and r2 dispatch personnel/shifts without deleting source records.
- Added date-effective automatic/manual waybill number pools and immutable issue/reprint/void event history.
- Added route start/end locations, start direction, D+ bounds, route-point types and separate D+ values for arrival/departure.
- Updated both pages of vector form № 1-АП to show official series/number, route endpoints and multi-day outbound/return schedules.
- Reprint does not consume a number; annulled numbers are not returned to the pool; reissue receives a new number.
- Candidate is delivered through START.bat and built by GitHub Actions as Windows Setup/Portable plus native macOS arm64/x86_64 artifacts.
- Publication uses branch `work/v8.70-waybill-r3`; stable `main` is not moved before manual acceptance.
- Tachograph recognition is unchanged.
