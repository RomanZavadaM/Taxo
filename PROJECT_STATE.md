# PROJECT_STATE — Taxo

**Підтверджено GitHub 27.11.2026 після promotion v10.24-r9 у Stable/Latest.**

**Stable/Latest:** [10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact product source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, draft=false, GitHub Latest.

**Previous Stable:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`.

## Stable 10.24-r9

- Нові/замінені копії документів ТЗ: `Data/VehicleDocuments/<vehicle_id>/<doc_type>/...` + source path + size + SHA-256.
- UI/відкриття перевіряють реальний файл; selected backup/restore перевіряє bytes, включно з archived records.
- Якщо історичні bytes відсутні у workspace, source та старих backup, SQLite не може їх відтворити.
- Product PR #643 merged; exact product source `e3770aa72b0744eee192979a2e569651bac4f257`.
- Initial Test publisher #46004721962 — SUCCESS.
- Повторне isolated acceptance-тестування: 1712/1712 PASS; 6/6 спеціальних r9 vehicle-document scenarios PASS; реальна робоча база не відкривалась.
- Stable promotion PR #651: START #46013308335, Windows #46013308203, Win7 #46013308379, macOS #46013308340 — SUCCESS; Windows/Win7 Defender/integrity PASS.
- PR #651 merged `3dfefa67ad9385ac18c8ee182c0a99a5a5a0effa`; publisher #46014386874 SUCCESS.
- Release `v10.24-r9`: 8 canonical assets, prerelease=false, draft=false, GitHub Latest; tag target лишився `e3770aa72b0744eee192979a2e569651bac4f257`.

## Open boundaries / next package

Issue #642 прийнята власником після isolated virtual round-trip test і закривається completed. Це не відновлює історичні файли, bytes яких уже немає ніде.

Наступна дозволена кодова ревізія — **10.24-r10** після вибору наступного змістовного пакета. Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge лишаються окремо заблокованими. Draft #543/#395 лишаються відкритими.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
