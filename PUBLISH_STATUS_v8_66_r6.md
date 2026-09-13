# Taxo v8.66 candidate r6 — publication status

Published branch: `work/v8.66-ui-polish-r6`
Published on: 2026-09-13
Stable baseline kept unchanged: `main` / v8.65 / `f9101c1a41d7c036bade5ce66989171399189d4b`

## Verified source identity

The published source files match the tested START.bat package byte-for-byte by Git blob SHA:

- `main.py`: `a672b42c8d93e790032b6ebfb8e5d6a39bd8700d`
- `tachograph.py`: `5df2ce239ac3fef55a346fc3c72e546c147e5852`
- `VERSION.txt`: `00ce8085b40ad2ab0a379e10194fb8f0e65acc72`
- `CHECKPOINT_CURRENT.md`: `55e656d36a2d4c91c7e3dce2aec11065ac36cb33`
- `RELEASE_NOTES_v8_66.md`: `67e12def08f23b7f793c7376cf2a59d63694f038`
- `TEST_REPORT_v8_66_r6.txt`: `febe7b83eaf90000f0effd59423ec1ed55e126f1`

## Test status

- Python syntax compilation: PASS.
- Full application smoke start: PASS.
- All 9 main tabs at 900×600 and 1024×700: PASS.
- Tachograph critical controls at 900×600, 1024×700 and 1200×760: PASS.
- Database schema: unchanged.
- Tachograph recognition algorithm: unchanged.

The candidate is published for user regression testing and is not yet promoted to stable `main`.
