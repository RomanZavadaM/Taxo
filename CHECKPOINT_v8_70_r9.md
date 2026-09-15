# Taxo v8.70 candidate r9 — configurable workspaces

Date: 2026-09-15
Base: published executable checkpoint v8.70 r8 (`448cabcb81f7f7a9fc1dd2099b9a1bc202ce8dbb`)
Branch: `work/v8.70-workspace-r9`

## Workspace model

- Default: `Documents/DriverWorktime`, preserving every existing installation without manual migration.
- Select or attach through `Файл → Робоче сховище…`.
- Supported paths: local disk, UNC/SMB/NAS and locally synchronized cloud folders.
- Mutable layout: `Data`, `Backups`, `Output`, `Logs`; tachograph scans and both SQLite databases are included.
- A per-user local JSON contains only the selected root path. No business data is stored there.

## Safety

- Workspace lock metadata contains token, computer, user, PID, version, start time and 30-second heartbeat.
- A second copy is blocked while the first owns the shared lock.
- Shared workspaces must only be opened by r9 or newer; older releases do not understand the lock.
- A dead same-computer lock is recovered automatically. A stale different-computer lock requires explicit confirmation and is archived under `Logs`.
- SQLite uses a 30-second busy timeout, `DELETE` journal mode and `FULL` synchronization; WAL is deliberately avoided for shared filesystems.
- Migration copies the two live databases through the SQLite backup API, validates them with `quick_check`, copies all other mutable files and keeps the source unchanged.
- Existing target data is never overwritten by migration.
- If a configured share is unavailable, startup does not silently create a new local empty database; it asks for another workspace or exits.

## Portability

- Waybill, waybill-event, attestation/audit and tachograph-scan paths use `workspace://` relative values.
- Legacy absolute paths are normalized automatically, including Windows paths opened later on macOS/Linux.
- The same synchronized dataset can therefore live under different local user-profile paths.

## Preserved constraints

- Worklog and personnel time records retain the rolling 48-month policy.
- Attestations and their audit remain indefinite until explicit permanent deletion.
- Backups remain SQLite-consistent and capped at the latest 30 copies.
- No database, scan, generated document, cache or personal data is bundled or committed.
- r8 personnel timesheet, r7 route distance and r6 odometer history are unchanged.
