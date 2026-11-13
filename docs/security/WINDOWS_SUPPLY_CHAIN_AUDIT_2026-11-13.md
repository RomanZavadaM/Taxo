# Taxo — Windows supply-chain audit after r9 (2026-11-13)

**Scope:** read-only investigation and safeguards design. This audit branch starts from verified r9 exact head `7537478bd4e60237cc3fc5d5f15a971ada927bdf`. It does **not** change `main`, Stable `v10.18-r3`, released r8 binaries, the owner-triggered publisher, or functional modules. Do not merge it as a new functional revision.

## Evidence and limits

1. Firefox blocked the earlier r8 Actions ZIP with a generic dangerous/virus warning; no detection name or vendor-specific classification was captured. A browser download block does **not** by itself identify malware or its entry point.
2. The r8 source and integration Windows portable packages had the same package layout and the same 1116 member paths. The executable had equal length and differed by six PE header/checksum-related bytes; the other identified changes were packaging metadata. This reduces evidence for an injection *between those two builds* but cannot exclude a shared compromised dependency in both.
3. The r8 Windows build was produced using PyInstaller 6.22.2. The `upx=True` spec setting was not accompanied by evidence that UPX actually executed on the runner, so UPX was not a proven root cause.
4. r9 tested Defender (signature 1.463.284.0) against the unpacked Windows and Win7 bundles, Portable ZIP and Setup EXE, and rechecked package SHA-256 before upload. The r9 exact-head four-platform CI passed. This is an important gate, **not** an independent all-vendor malware clearance.
5. The r9 Windows build log shows unpinned transitive versions selected by pip, e.g. `lxml==6.1.3`, `numpy==2.5.4`, `pyinstaller-hooks-contrib==2026.10`, `setuptools==84.2.1`. `requirements.txt` pins top-level runtime packages but not these transitive dependencies or their distribution SHA-256 hashes.
6. `packaging/installer/Taxo.iss` is compiled by Inno Setup; on a runner where ISCC is missing, the Windows workflow invokes `choco install innosetup` without a version/hash lock. This is an additional external input.
7. GitHub Actions checkout, setup-python, and upload-artifact actions in the inspected workflow are pinned by commit SHA. This limits action-version drift but does not authenticate everything downloaded by pip, Chocolatey, the runner image, or all transitive artifacts.

## Independent byte-level artifact comparison (read-only, no executable launch)

Three saved GitHub Actions Windows artifact archives were opened as ZIP files (r8 exact-source, r8 integration, r9 final), then their nested Portable ZIP members were checked by relative path and SHA-256. The **outer** artifact hashes were:

- r8 source outer ZIP: `c60a403439f09486331c217c05ad3d1a78cdf9e842e175c67481ff6e088f6785`;
- r8 integration outer ZIP: `a3ff09b16ab4b377cbd786a91bbfc4361e9b5ddd578c07e5131a5400a2c065bf`;
- r9 final outer ZIP: `0ce0034b0e81e2d4446db5c9bb1a25bbe98510db7123b203fa0948a3f9b68384` (matches GitHub artifact digest).

All three nested Portable packages contained exactly **1116 relative file paths**, with no additions/removals between the sampled builds. Exactly 1113 files had identical SHA-256 content across all three. Only three paths differed:
`Taxo.exe`, `_internal/base_library.zip`, and `_internal/numpy-2.5.4.dist-info/RECORD`.

- r8 source vs r8 integration `Taxo.exe`: six changed bytes, at offsets `264,265,344,345,249828,249829`. Offset 264 is PE COFF timestamp, offset 344 is PE checksum; 249828 mirrors timestamp-associated bytes.
- r8 source vs r9 `Taxo.exe`: eleven changed bytes at `264,265,344,345,346,249828,249829,3079925,3486805,3486806,3486808`. Not all are PE header offsets; do **not** describe all eleven as just a changed build timestamp.
- The 154 uncompressed members inside `base_library.zip` have **identical SHA-256 contents** across all three packages, despite different outer ZIP hashes.
- The observed difference in NumPy `RECORD` is limited to two hash lines for `../../Scripts/f2py.exe` and `../../Scripts/numpy-config.exe`; their actual executables are not part of the compared Portable tree. The rest of the RECORD file was unchanged.

**Interpretation:** no new Portable file path or broad injected payload was detected between these builds. This evidence is narrower than a security clearance. A shared contaminated dependency or malicious code already present in all three packages remains possible; packed PyInstaller internals require a separate code/provenance audit.

## Threats to distinguish

- **Browser reputation:** an unsigned, freshly built executable/archive can trigger reputation-based warnings. Hypothesis only; needs Firefox / Safe Browsing / anti-malware vendor verdict.
- **Third-party supply-chain tampering:** compromised wheel, PyInstaller hook, or Inno Setup installer could affect both builds identically. Compare archived wheel hashes, provenance, dependency lock and vendor advisories rather than relying on source diffs.
- **Build environment tampering:** GitHub-hosted runner image, toolchain, cache, network resolution and downloaded binaries are additional trust boundaries. No evidence currently identifies a compromised runner.
- **Repository-level insertion:** review unexpected changes to product imports, `.spec`, GitHub workflow permissions, and hooks between the last accepted checkpoint and r8; the six-byte comparison alone does not cover earlier compromise.

## Required next controls (security task; no silent activation)

1. Capture full installation reports with download URLs and SHA-256 of **all resolved wheel files**, for Windows x64 and Win7 separately. Preserve wheel provenance as private or CI artifacts, not in public document-template archives.
2. Build from a reviewed, platform-specific lock containing every transitive dependency and each wheel SHA-256, using `pip install --require-hashes --only-binary :all:`. A partial lock is not sufficient; do not switch to this until the platform-specific hashes are reviewed.
3. Pin Inno Setup to an approved version and independently verified package digest or vendor-signed installer; fail closed if unavailable. Log actual ISCC version/hash.
4. Record runner image version, Python patch version, exact `git rev-parse HEAD`, full `pip freeze`, spec hash, wheel hashes, `Taxo.exe` hash, ZIP hash, and full SHA256SUMS in the build provenance.
5. Compare two fresh Windows builds with the same reviewed wheelhouse; normalize only documented non-deterministic PE metadata and check all remaining byte differences. Any unexplained executable/code difference is a release blocker.
6. Obtain the precise Firefox block classification (browser/OS/vendor) from the r8 download-only test; no execution or security-warning bypass is needed.
7. Run an independent scanner/vendor analysis on the r8 and r9 EXE and ZIP. A clean Defender scan alone cannot close the original Firefox security incident.
8. Keep user-facing functional test packages as uniquely named source START/BAT ZIPs without suspected EXEs. A source test that installs dependencies online is **not supply-chain-independent**; use reviewed wheels when possible.

## Release hold and ownership

- Owner-triggered GitHub Actions publisher is user-owned and must not be canceled or modified by this audit task.
- Stable/Latest `v10.18-r3` remains untouched.
- Do not classify the r8 Firefox warning as false positive or claim a verified infection without a concrete detection.
- Security hardening must be validated in a separate exact-head CI before executable publication; no reusing issued revision identifiers.
