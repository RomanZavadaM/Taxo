# GitHub recovery status — Taxo v8.60

Updated: 11.09.2026

## What is safely preserved

- The authoritative recovered v8.60 source archive is stored in ChatGPT Library as `/Taxo/Releases/Taxo_v8_60_source.zip`.
- SHA-256 of that exact archive: `edb7c7c87df0c320bbe091daadbd6b8263072835de1c66b4f6f20ad6683f2664`.
- Additional independent Library copies exist as `Taxo_v8_60_TEST.zip`, `Taxo_v8_60_CONTROL.zip`, and `Taxo_v8_60_RECOVERED.zip`.
- This branch contains the recovery metadata, version history, recovery rules and cumulative `main.py` patch artifacts from v8.56 to v8.60.

## Important limitation

The root `main.py` on `release-v8.60` is NOT yet guaranteed to be byte-for-byte identical to the authoritative recovered v8.60 `main.py`. The exact source snapshot in the Library archive remains the source of truth for starting v8.61.

Do not reconstruct v8.61 from chat memory and do not start it from the branch root `main.py` until the exact recovered source has been synchronized or independently verified.

The Base64 file `releases/Taxo_v8_60_source.zip.b64.p00` is only a partial archival experiment and MUST NOT be treated as a complete source archive.

## Branch policy

- `main` remains the last stable v8.56 line until v8.60 is explicitly accepted as stable.
- `release-v8.60` is the recovery/preservation branch.
- Next development version: v8.61, created only from the authoritative recovered v8.60 snapshot.

## Startup order for future work

Read `RECOVERY_INDEX.md`, `AI_HANDOFF.md`, `PROJECT_STATE.md`, `VERSION.txt`, and this file before changing Taxo.
