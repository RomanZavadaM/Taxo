# Taxo v8.70 candidate r9 — publication status

- Base: published executable checkpoint v8.70 r8, GitHub `main` commit `448cabcb81f7f7a9fc1dd2099b9a1bc202ce8dbb`.
- Target branch: `work/v8.70-workspace-r9`; target base: `main`.
- Local compilation, 31-test suite, workspace migration/locking tests and workflow YAML validation passed before publication.
- PR CI compiles and tests source on Windows and macOS without producing routine executable artifacts.
- After verified merge, `publish-v8.70-r9.yml` builds Windows Setup/Portable, native macOS arm64/x86_64, source START ZIP and shared SHA-256 checksums.
- The executable checkpoint is published under a separate `v8.70-r9` pre-release tag. Historical `v8.70` and `v8.70-r8` releases remain untouched.
- No database, scan, generated document, cache or personal data is committed or packaged.
