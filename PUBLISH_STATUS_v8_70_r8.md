# Taxo v8.70 candidate r8 — publication status

- Base: merged GitHub `main` v8.70 r7, commit `7c91135297e15622bf967f109ded42c52197d172`.
- Target branch: `work/v8.70-personnel-timesheet-r8`; target base: `main`.
- Local syntax, 21-unit-test suite, XLSX inspection and PDF rendering passed before publication.
- Routine PR CI compiles/tests source only. The accepted r8 checkpoint additionally launches one controlled release workflow.
- Release outputs: Windows Setup, Windows Portable, macOS arm64, macOS x86_64, source ZIP and one SHA-256 manifest.
- After all builds pass, obsolete assets on the existing v8.70 pre-release are replaced by unambiguous r8 files; historical branches remain preserved.
- Never commit user databases, caches, generated QA output or personal data.

Source implementation: merged through PR #17, commit `4706ebf3dcaa0cca8afdf15bafa8c1d0f78dcd00`. Executable publication: pending release workflow.
