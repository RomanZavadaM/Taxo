# Taxo — CURRENT CHECKPOINT

Date: **2026-09-17**

## Stable baseline

- Version: **9.0**
- Release: **stable**
- Git tag: `v9.0`
- Baseline commit: `a8e6b80d34d114e6d2c82f602d03468f1529e98a`
- GitHub Release: `Taxo 9.0 — stable release`
- Previous verified development line: `v8.70 candidate r11`

## Current development mode

Taxo 9.0 is no longer in rapid feature-development mode. The next phase is **field operation and data accumulation**.

Changes should be driven by real observed problems and follow the maintenance rules in `docs/system/MAINTENANCE_POLICY.md`.

## Current functional scope

- company and bilingual attestation details;
- employees, roles and driver cards;
- vehicles and odometer history;
- exact route/time scenarios;
- graphical driver schedule;
- driver monthly timesheet with split shifts;
- personnel plan/fact timesheet;
- official waybill № 1-АП workflow with numbering, revisions and void history;
- confirmation-of-activities documents with audit/archive;
- analog tachograph scans, recognition candidates and confirmed intervals;
- single-driver №340 control;
- separate weekly work-time balance to 60:00 and driving balance to 56:00;
- editable driver selection inside the control window;
- editable report formation date;
- standalone 60-day minute-by-minute driver activity register;
- configurable local/network/cloud-synchronized workspace;
- backups, archives and error logs.

## Non-negotiable invariants

- plan does not automatically become fact;
- tachograph fact never overwrites plan `worklog/work_segments`;
- missing time in the 60-day register remains `Невизначено`;
- release packages contain no user database or personal data;
- preview does not consume a waybill number;
- reprint preserves number and creates a revision;
- ordinary voiding does not return the number to the pool;
- one active Taxo instance per shared workspace;
- user-facing dates remain `DD.MM.YYYY`.

## Distribution

Stable v9.0 has verified packages for:

- Windows x64 Setup;
- Windows x64 Portable;
- macOS arm64 Portable;
- macOS x86_64 Portable;
- START source ZIP;
- SHA-256 manifest.

All three executable-platform builds and stable publication workflow completed successfully before release.

## Documentation source of truth

Start at `docs/README.md`.

The most complete continuation checkpoint is:

`docs/system/DEVELOPMENT_STATE_v9.0.md`

Operational instructions:

`docs/guides/README.md`

## Next step

Do **not** start another broad feature wave yet. Use 9.0 in production-like operation, populate the database, collect real tachograph samples and record defects/awkward workflows. Fix them incrementally with regression tests and protected PRs.
