# Taxo v8.65 candidate r2 — frozen test checkpoint

Date: 2026-09-12

Status: current test candidate. Do not merge into `main` yet.

Stable production baseline remains `v8.64` on `main` at commit `c2ebee7bb832680e1c98a447cb90ebd115349fed`.

## Current v8.65 r2 model

- Existing entered schedule data are treated as planned driving-time intervals.
- Planned working-time intervals are stored in parallel.
- For migration, working start/end initially copy driving start/end 1:1; later the user can edit working-time boundaries independently.
- Every segment therefore has two explicit interval pairs:
  - working start / working end;
  - driving start / driving end.
- Durations are derived from interval boundaries; they are not standalone primary values.
- `Без тахо — стандартні 8 год` remains working time 8:00 with driving time 0:00.
- Regulation №340 analysis uses driving intervals for driving limits and working intervals for working-time/rest logic.
- Tachograph data must remain FACTUAL/ACTUAL driving evidence and must not overwrite planned schedules automatically.

## Frozen archives

Library release archive names:
- `Taxo_v8_65_TEST_r2.zip`
- `Taxo_v8_65_source_r2.zip`

SHA-256:
- TEST r2: `4d7587e3a85797b65a40352b128cd690f6ea437f4a24bb223ec65751c447aeba`
- SOURCE r2: `cdd6fcf31828ab77a2959713527a70369ec561f87e367010c8838b1ea0f617b2`

The user is now performing extended Windows testing. Any subsequent code change must be treated as a new candidate revision (r3 or later), not silently overwrite r2.
