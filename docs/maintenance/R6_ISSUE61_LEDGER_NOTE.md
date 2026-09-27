# Issue #61 ledger note — Taxo 10.4-r6

Fast-test checkpoint issued 27.09.2026.

- Issued code head: `d25cac1427911e2640db0be126c5f63410cb4e56`
- START run: `36342480624` — success
- START artifact: `Taxo_v10_4_candidate_r6_START`, ID `10939860812`
- SHA-256: `e823f41492b48e7de2d08abb6c783eeffd842c47afffe53fa0160ad3e7cd9948`
- Regression: `323/323 OK`

P0 fixed: control №340 previously used plan-derived worklog/route data as if they were factual and collapsed split work parts into one envelope. This hid a long internal night rest and could label a short daytime gap such as 3:35 as an insufficient intershift rest.

r6 now uses exact planned work intervals, supports the current ordinary daily-rest split model 3+9, does not auto-classify every short gap as a <9h violation, and labels plan-derived findings as `ПЛАН:`. Route/waybill reverse = plan. `fact_work_*`, tachograph and confirmed factual documents remain the factual layer; handwritten waybill fact is not digital fact until entered.

r6 is immutable after issuance. Next code revision: `10.4-r7`.
