# Taxo v8.66 candidate r10 — publication checkpoint

Date: 2026-09-14

- Stable `main`: v8.65 @ `f9101c1a41d7c036bade5ce66989171399189d4b`.
- Candidate branch: `work/v8.66-ui-polish-r10`.
- Verified code commit: `7076a8dd24937e0925a87e03789e03bb8159ce0d`.
- Canonical code blobs: `main.py` = `21c3036237c6d50619890154a9c952f042475ac4`; `tachograph.py` = `d5d8e71e0601e951b39432ade123e2be99509cd0`.
- Core UI change: `Тахограф — шайби` now uses `Перегляд` / `Результати` sub-tabs with independent scrolling.
- r9 route merge is retained: one user-facing `Маршрути` model, one route = one exact time scenario.
- Authoritative r8 monthly schedule/PDF behavior is retained.
- Exact assembled GitHub candidate passed compile + TAHO layout/scroll regression + monthly PDF stale-state regression.
- Recognition algorithm is unchanged.
- Intermediate distribution remains START.bat; next full executable milestone is v8.70.

This file is the recovery point if chat context is lost.
