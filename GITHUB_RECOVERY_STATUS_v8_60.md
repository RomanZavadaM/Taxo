# GitHub recovery status — Taxo v8.60

Updated: 11.09.2026

## Synchronization complete

The `release-v8.60` branch is now synchronized with the authoritative recovered v8.60 runtime snapshot.

Verified byte-for-byte against `/Taxo/Releases/Taxo_v8_60_source.zip`:

- `main.py` — SHA-256 `bb11ecc39e2f7b54fd9926d4023d72b282556efa869922b1e0b7abfc98f31a8c`, Git blob `8d19b94d7fea2d8f77ccb2e40fccbad0465bf214`.
- `tachograph.py` — SHA-256 `6018a71b4a283dbbba640e1daa313eff9f26cdde931aa4cba77884a5141d20cc`, Git blob `8d372a7a4529cb9972ccb32a311a5af13b624b87`.
- `START.bat` — SHA-256 `34e208569f33da88ead4656a0638068b84d71cec5c6ea4e67dce7afcdc370864`, Git blob `4fb6a3a48622b8e283304be28e77d354373714c0`.
- `requirements.txt` — SHA-256 `09acc97b519dd17aca54991b45b6183cc7dddd4597ce317db3f3d54fc226688e`, Git blob `1d3dfdc0d26a3896acf6103cda2c2e46bb5ac0e5`.
- `VERSION.txt` — SHA-256 `8dc330cb0a42d870fc4991852aad1bfe89498d9a7d0d5a26d9ccea705bfb60d7`, Git blob `f197a1b620e55bac836726712c6ab4b1df73337d`.
- `Бланк підтвердження.docx` — SHA-256 `47aeb545509af8d43102f76de772838b36de1fa85a2d09bae2d2ce7798358ec0`, Git blob `a434a24a888ea56c313aa30ce582b3050ad00880`.

The exact recovered `main.py` was synchronized by GitHub Actions commit `7edc68314a5570cab2fbcadd6d0e44c15072f1da`. Before committing, the workflow verified the v8.56 base hash, reconstructed the exact recovery patch, verified the final v8.60 SHA-256, and ran `python -m py_compile main.py tachograph.py` successfully.

## Recovery copies

- Authoritative source archive in ChatGPT Library: `/Taxo/Releases/Taxo_v8_60_source.zip`.
- Archive SHA-256: `edb7c7c87df0c320bbe091daadbd6b8263072835de1c66b4f6f20ad6683f2664`.
- Additional independent Library copies: `Taxo_v8_60_TEST.zip`, `Taxo_v8_60_CONTROL.zip`, `Taxo_v8_60_RECOVERED.zip`.
- `SOURCE_MANIFEST_v8_60.sha256` records the authoritative runtime hashes.
- `releases/Taxo_v8_56_to_v8_60_EXACT.patch.part01` … `part04` preserve the exact reproducible source delta from the v8.56 `main.py` to the v8.60 `main.py`.

## Branch policy

- `main` remains the last explicitly accepted stable v8.56 release until a separate decision is made to promote v8.60.
- `release-v8.60` is now a complete, verified development baseline for v8.60.
- Next development version: `v8.61`, to be branched from the synchronized `release-v8.60` state or from the authoritative v8.60 control archive.

## Startup order for future work

Read `RECOVERY_INDEX.md`, `AI_HANDOFF.md`, `PROJECT_STATE.md`, `VERSION.txt`, `SOURCE_MANIFEST_v8_60.sha256`, and this file before changing Taxo.
