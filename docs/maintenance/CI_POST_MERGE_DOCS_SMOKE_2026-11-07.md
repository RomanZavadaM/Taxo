# CI post-merge docs-only smoke — 2026-11-07

Purpose: verify the integrated CI rules on current `main` after PR #220.

Expected PR behavior:
- required `build-windows` runs in lightweight documentation mode;
- Windows heavy regression/packaging steps are skipped;
- Win7 and macOS PR workflows do not start.

Expected behavior after merge to `main`:
- ordinary docs-only push does not start Windows, Win7, macOS or START heavy workflows;
- release publisher does not start.
