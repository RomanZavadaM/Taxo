# PROJECT_STATE — Taxo

**Підтверджено GitHub 27.11.2026 після публікації Test v10.24-r9.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, draft=false, GitHub Latest.

**Current Test:** [10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 assets, prerelease=true, draft=false. Publisher #46004721962 — SUCCESS.

## Test 10.24-r9

- vehicle-document attachments are stored as Taxo-owned copies in `Data/VehicleDocuments`;
- new/replaced copies retain source-path provenance, size and SHA-256;
- UI reports actual file state instead of treating a non-empty DB path as proof that bytes exist;
- archive state does not remove or detach the managed copy;
- selected vehicle-document backup validates all registered copies, including archived records, and fails closed when unrecoverable bytes are missing/damaged;
- legacy external/source references that still exist can be materialized into the staged backup without mutating the live DB;
- restore revalidates the declared vehicle-document file set;
- SQLite alone cannot recreate historical bytes that no longer exist in workspace/source/older backup.

Candidate #643 final head `99f3fcf3b12214adf664e6d401735dd94f00d391`: START #46002324307, Windows #46002324733, Win7 #46002324330, macOS #46002324335 — SUCCESS; Defender/integrity PASS.

Exact issued source `e3770aa72b0744eee192979a2e569651bac4f257`: START #46003120544, Windows #46003120782, Win7 #46003120506, macOS #46003120628 — SUCCESS; Defender/integrity PASS.

Release trigger #644 head `df993b869cc9fa518ede010da48a5cdd6927f81c`, merged `574f3acd2e078ffc1fd25a5690f5853cfe19c017`: START #46003987406, Windows #46003987089, Win7 #46003987064, macOS #46003987034 — SUCCESS; Defender/integrity PASS. Publisher #46004721962 — SUCCESS.

## Open boundaries / next package

Stable remains 10.24-r3.

Issue #642 stays open pending manual acceptance on the owner's real workspace. Next action is to inspect existing vehicle-document records/scans on r9 and create a backup with vehicle-document copies selected; do not claim recovery for historical bytes that no longer exist. Next allowed code revision is 10.24-r10.

#553/#556/#562 remain open for their manual acceptance. Draft #543/#395 stay open. Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY and physical attachment purge remain separately blocked.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
