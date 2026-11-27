# Поточна контрольна точка Taxo

**27.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r9.**

## Stable

- Release: [v10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3)
- Exact source: `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`
- 8 canonical assets; GitHub Latest; prerelease=false; draft=false.
- Stable не змінювати без окремого рішення власника.

## Current Test

- Release: [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9)
- Exact product source: `e3770aa72b0744eee192979a2e569651bac4f257`
- 8 canonical assets; prerelease=true; draft=false.
- Product PR #643 завершено; Issue #642 **OPEN** до ручного приймання на реальному робочому сховищі.
- Root cause від 10.2-r1 (21.09.2026): vehicle-document DB row міг пережити втрату файла; source path не зберігався; UI міг показувати «Копія: Є» лише за непорожнім path; vehicle-document bytes у manual backup були optional.
- r9: Taxo-owned copy у `Data/VehicleDocuments` + source path + size + SHA-256; factual file state; integrity check on open.
- Selected backup з документами ТЗ перевіряє зареєстровані bytes, включно з archived records; доступний legacy external/source file може бути перенесений у staging backup без зміни live DB.
- Restore повторно перевіряє vehicle-document bytes; архівування запису не видаляє копію.
- Exact-product main checks: START #46003120544, Windows #46003120782, Win7 #46003120506, macOS Intel/ARM #46003120628 — SUCCESS; Windows/Win7 Defender/integrity PASS.
- Release trigger main `574f3acd2e078ffc1fd25a5690f5853cfe19c017`; publisher #46004721962 — SUCCESS.
- GitHub release exact target `e3770aa72b0744eee192979a2e569651bac4f257`; 8 canonical assets verified.

## Recovery / acceptance

- Public recovery #646 and current-page synchronization #648 are merged; final recovery files remove stale r8 «next action» instructions.
- Private `profile/taxo`, Issue #61 і Drive mirror мають бути синхронізовані з цим станом; Issue #642 не закривати до ручного приймання.
- Owner acceptance: attach/replace a vehicle-document copy → archive record → create backup with «Копії документів транспортних засобів» → restore into a test workspace → open the restored copy. Якщо виявлено новий дефект, наступна кодова ревізія — **10.24-r10**.
- Historical bytes missing from workspace, source and old full backups cannot be recreated from SQLite alone.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY and physical attachment purge do not start automatically.

Draft #543/#395 stay open.
