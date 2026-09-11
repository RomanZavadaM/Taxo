# AI_HANDOFF — Taxo

This file exists specifically to prevent loss of project state across long chats.

## Current checkpoint

- **Current control version:** v8.60
- **Next version:** v8.61
- **Do not resume from v8.56/v8.57 just because a chat memory says so.**
- Primary truth: `RECOVERY_INDEX.md` + `PROJECT_STATE.md` + control ZIP/source snapshot.

## v8.57 → v8.60 changes that must not be lost

- v8.57: edit existing Attestations; soft delete; restore; revision number; `attestation_audit`; archive replaced/deleted DOCX; automatic DB backup before EDIT/DELETE/RESTORE; fixed 48-month attestation purge.
- v8.58: English company fields `name_en`, `address_en`, `signer_name_en`, `signer_position_en`, `place_en`; per-field fallback to Ukrainian.
- v8.59: visible `Зберегти реквізити підприємства`; auto-save current company fields before create/edit/regenerate of Attestation.
- v8.60: English driver fields `last_name_en`, `first_name_en`, `middle_name_en`; per-field fallback; automatic old-DB schema migration.

## Non-negotiable project rules

- Never include the user's main SQLite DB in ZIP/GitHub.
- Dates in UI: `ДД.ММ.РРРР`.
- A4 for office documents; A4 landscape for wide monthly schedules/timesheets.
- Monthly timesheet day cells show hours only.
- Attestation default activity = 16; exactly one activity 14–19 per period.
- Attestation document date = calendar date of `Період по`.
- Tachograph scans are selective control only; they must not auto-correct the main work schedule.

## Next agreed work

Start v8.61 from an untouched copy of v8.60. Add Attestation output in PDF and JPG in addition to DOCX, preferably without requiring Microsoft Word.

## Recovery procedure

If chat context is missing, stop coding. First obtain v8.60 from Library/GitHub, verify SHA-256, then continue. Never recreate a guessed version from an older checkpoint.
