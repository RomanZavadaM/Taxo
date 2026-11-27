# HANDOFF_CURRENT — Taxo

**27.11.2026 — Stable/Latest = 10.24-r9.**

**Stable/Latest:** [10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, `prerelease=false`, `draft=false`, GitHub Latest.

## Що завершено

- Інцидент зі зниклими копіями документів ТЗ технічно виправлено у 10.24-r9: нова/замінена копія є Taxo-owned файлом у `Data/VehicleDocuments`, зберігаються source path, size та SHA-256; UI перевіряє фактичну наявність/цілісність.
- Архівування запису не видаляє копію; selected backup з документами ТЗ перевіряє bytes, restore перевіряє їх повторно.
- 27.11.2026 на прохання власника виконано повторний ізольований віртуальний прогін без доступу до робочої бази: 1712/1712 tests PASS; усі 6 r9 vehicle-document scenarios PASS, включно з archive → backup → restore у чистий temporary workspace → ідентичні bytes.
- Promotion PR #651: START #46013308335, Windows #46013308203, Win7 #46013308379, macOS Intel/ARM #46013308340 — SUCCESS; Windows/Win7 Defender + integrity PASS.
- PR #651 merged як `3dfefa67ad9385ac18c8ee182c0a99a5a5a0effa`.
- Publisher #46014386874 — SUCCESS: існуючий immutable release `v10.24-r9` переведено у Stable/Latest без пересування тегу та без зміни exact product source.
- Issue #642 прийнята власником на підставі ізольованого тестування і закривається.
- Попередня Stable: `v10.24-r3`.

## Що далі

- Наступна дозволена кодова ревізія — **10.24-r10**, але не починати її автоматично без вибору наступного змістовного пакета з загального плану.
- Draft #543/#395 не закривати автоматично.
- Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не починати без окремого рішення власника.
- Старі вже фізично втрачені bytes неможливо відновити з SQLite, якщо їх немає у workspace, початковому файлі або старому backup.

Recovery: `START_HERE.md → HANDOFF_CURRENT.md → PROJECT_STATE.md → private profile/taxo → live GitHub`.
