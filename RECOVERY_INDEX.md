# Taxo — Recovery Index

**Authoritative current control version: v8.60**  
**Next development version: v8.61**  
**Recovery date: 11.09.2026**

## Mandatory startup rule

Before changing Taxo, do **not** infer the current version from chat memory. Read, in this order:

1. `RECOVERY_INDEX.md`
2. `AI_HANDOFF.md`
3. `PROJECT_STATE.md`
4. `VERSION.txt`
5. `SHA256SUMS.txt`

Then verify the available control ZIP/source snapshot.

## Recovered version chain

- v8.56 — last previously published base.
- v8.57 — attestation edit / soft-delete / restore / revisions / audit / backup before destructive actions.
- v8.58 — English company fields with fallback to Ukrainian.
- v8.59 — visible company Save button and automatic save before attestation create/edit.
- v8.60 — English driver surname/first/middle fields with per-field fallback and automatic DB migration.

The v8.57–v8.60 control ZIPs were recovered from user-provided archives on 11.09.2026 and stored in ChatGPT Library under `/Taxo/Releases/`.

## Development rule

Never edit the v8.60 control snapshot in place. Copy it to `Taxo_v8_61` and make the next change there. The planned next block is PDF/JPG output for the Attestation form while retaining DOCX.

## Data safety

- User SQLite databases are never packaged or published.
- Persistent user data stays under `%USERPROFILE%\Documents\DriverWorktime\`.
- Every release must be kept in at least two independent locations.
- For GitHub, a source ZIP may be stored as Base64 text parts plus SHA-256 when binary upload is unavailable.
