# PROJECT_STATE — Taxo

**Підтверджено GitHub 21.11.2026 після публікації Test 10.23-r7.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`.

**Current Test:** [10.23-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r7), exact source `a60d1933ddde090f0cb5e8672c5070030647301d`, 8 assets, prerelease. Publisher #44944448052 — SUCCESS.

## Stable r4

Stable r4 залишається вручну прийнятою власником версією. Вона містить каталог документів, власні папки, скани/паперовий підпис, редагування учасників наказу, регульовані робочі області та адаптивний перегляд наказу. 37 strict live routes.

## Test r7

r7 продовжує безпечний AI-ready шлях після read-only inventory r6:
- dry-run inventory batch зберігається лише у керованому workspace;
- atomic staging → publish;
- `inventory.json` + `report.json` + checksum manifest;
- idempotent reuse того самого batch;
- fail-closed conflict для однакового batch ID з іншим вмістом;
- checksum verification пошкодженого manifest;
- source archive лишається read-only.

Exact-source CI `a60d1933ddde090f0cb5e8672c5070030647301d`: START #44943282760, Windows #44943282736, Win7 #44943282765, macOS Intel/ARM #44943282733 — SUCCESS; Defender/integrity PASS; publisher #44944448052 — SUCCESS.

## Документна архітектура / AI-ready

21.11.2026 нормативну модель інтегровано в main: `docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md`. r6 реалізує INVENTORY, r7 — атомарне збереження dry-run batch/report. Наступна **10.23-r8** — verified batch reader + deterministic sorting preview без AI APPLY.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
