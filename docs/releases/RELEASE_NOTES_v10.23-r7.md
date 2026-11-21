# Taxo 10.23-r7 — атомарні dry-run inventory batches

**Робочий Test-кандидат. Stable/Latest залишається 10.23-r4; поточний опублікований Test — 10.23-r6.**

- dry-run inventory з r6 зберігається тільки у керованому workspace;
- шлях: `Data/DocumentLibrary/import_batches/<batch_id>`;
- `inventory.json` містить повний machine-readable manifest;
- `report.json` містить summary, exact duplicates, errors і checksum manifest;
- весь batch публікується атомарно після повного запису staging-каталогу;
- повторне збереження того самого batch з тим самим вмістом є idempotent;
- той самий batch ID з іншим вмістом відхиляється fail-closed;
- пошкодження manifest визначається за SHA256;
- заборонено створювати batch-store всередині source-архіву.

У r7 немає OCR, AI ANALYZE/PROPOSE/APPLY, move/rename/delete/copy source-файлів або автоматичного сортування. Source-архів лишається read-only.
