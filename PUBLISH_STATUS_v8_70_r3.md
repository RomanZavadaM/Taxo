# Taxo v8.70 candidate r3 — publication status

- Target branch: `work/v8.70-waybill-r3`.
- Base commit: v8.66 candidate r10, `ece9e4165b44c6cc9b169c3166a1307c46dd052d`.
- Stable `main` remains v8.65 until manual acceptance.
- Draft PR targets `main`.
- Windows workflow produces:
  - `Taxo_v8_70_TEST_r3_Setup_Windows_x64.exe`;
  - `Taxo_v8_70_TEST_r3_Windows_x64_Portable.zip`;
  - SHA-256 checksums.
- macOS workflow produces native portable packages for `arm64` and `x86_64`.
- Databases, cache files and user output are forbidden in every artifact.
