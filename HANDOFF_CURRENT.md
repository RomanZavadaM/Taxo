# HANDOFF_CURRENT — Taxo

**21.11.2026 — 10.23-r7 опубліковано як Test prerelease; Stable/Latest лишається 10.23-r4.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`, GitHub Latest.

**Test:** [10.23-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r7), exact source `a60d1933ddde090f0cb5e8672c5070030647301d`, 8 assets, prerelease. Publisher #44944448052 — SUCCESS.

Exact-source r7 CI: START #44943282760, Windows #44943282736, Win7 #44943282765, macOS Intel/ARM #44943282733 — SUCCESS; Defender/integrity PASS.

## Що додає r7

- атомарне збереження read-only inventory batch у `Data/DocumentLibrary/import_batches/<batch_id>`;
- `inventory.json` — повний versioned manifest;
- `report.json` — summary, exact duplicates, errors/skipped та SHA256 manifest;
- staging-каталог публікується лише після повного запису;
- повторне збереження того самого batch із тим самим вмістом — idempotent;
- той самий batch ID з іншим вмістом — fail-closed;
- пошкодження manifest виявляється за checksum;
- batch-store не можна створювати всередині source-архіву;
- source-файли не move/rename/delete/copy; AI ANALYZE/PROPOSE/APPLY ще відсутні.

## Нормативна AI-ready модель

`docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md` уже в main. Канонічна структура — stable document identity + metadata + links; дерево папок лише представлення. Оригінали не змінюються. Масова робота має staging INVENTORY → ANALYZE → PROPOSE → REVIEW → APPLY → VERIFY, confidence/reason/review, import batch + rollback і dry-run перед APPLY.

## Наступний крок

**10.23-r8:** verified batch reader + deterministic sorting preview. Taxo має read-only відкрити збережений batch, перевірити checksum/формат і побудувати стабільний preview сортування за датою, номером, категорією/видом і source fallback із tie-breaker stable identity. Ніякого OCR, AI APPLY або фізичного сортування.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.
