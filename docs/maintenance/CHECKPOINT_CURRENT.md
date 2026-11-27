# Поточна контрольна точка Taxo

**27.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r9.**

## Stable

- Release: [v10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3)
- Exact source: `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`
- 8 canonical assets; GitHub Latest; prerelease=false; draft=false.
- Stable не змінювати без окремого рішення власника.

## Current Test

- Release: [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9)
- Exact source: `e3770aa72b0744eee192979a2e569651bac4f257`
- 8 canonical assets; prerelease=true; draft=false.
- Документи ТЗ: Taxo-owned bytes + source provenance + size/SHA-256.
- Реальний file-state замість хибного «Є» за самим шляхом БД.
- Архівування не видаляє копію.
- Selected backup vehicle documents: materialize recoverable legacy source → validate all DB references → restore validation.
- Candidate #643: START #46002324307, Windows #46002324733, Win7 #46002324330, macOS #46002324335 — SUCCESS; Defender/integrity PASS.
- Exact source: START #46003120544, Windows #46003120782, Win7 #46003120506, macOS #46003120628 — SUCCESS; Defender/integrity PASS.
- Release-trigger #644 merged as `574f3acd2e078ffc1fd25a5690f5853cfe19c017`; publisher #46004721962 — SUCCESS.
- GitHub release exact target `e3770aa72b0744eee192979a2e569651bac4f257`; 8 canonical assets verified.
- Stable/Latest verified separately as v10.24-r3.

## Далі

Ручне приймання #642 на реальному робочому сховищі: відкрити старі протоколи/документи ТЗ, подивитися фактичний стан копії та створити backup з відміткою документів ТЗ. Відсутні bytes не вважати відновленими без фактичного файла.

Наступна кодова ревізія: **10.24-r10**. #553/#556/#562 та draft #543/#395 лишаються відкритими у своїх межах.
