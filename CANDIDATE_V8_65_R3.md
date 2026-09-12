# Taxo v8.65 candidate r3 — frozen checkpoint

Date: 2026-09-12

Stable `main` remains v8.64 at `c2ebee7bb832680e1c98a447cb90ebd115349fed`.

Current test candidate archives are stored in the project Library:
- `Taxo_v8_65_TEST_r3.zip` — SHA-256 `0951e5f5b92176e40a1f6ac4b3f56eb74fd7220e033f1de33e7c85c578bf74c7`
- `Taxo_v8_65_source_r3.zip` — SHA-256 `8f33e916279b69d3c1656c7a041b445ba3cf43aed1a2252fce80747db7c3e797`
- `main.py` — SHA-256 `bce9018ed9365c97778867380a21d0ac756b854763a73447a285cdc468890e2a`

r3 fixes:
- centralized handling of locked/open PDF/XLSX output files with Retry / Create copy / Cancel;
- local GUI exception logging;
- graphical schedule labels are no longer hidden for short edited intervals.

Candidate r2 remains frozen. Do not merge r3 into `main` until Windows testing is complete.
