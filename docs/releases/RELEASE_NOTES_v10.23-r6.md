# Taxo 10.23-r6 — read-only inventory існуючого архіву

**Робочий Test-кандидат. Stable/Latest залишається 10.23-r4; останній опублікований Test — 10.23-r5.**

- read-only inventory вибраної папки без запису в source;
- SHA256, MIME, розмір, modified time, source path/relative path, stable candidate_id;
- machine-readable manifest `taxo.document-inventory.v1`;
- exact duplicates — лише однаковий SHA256;
- symlink-и не проходяться;
- повторний scan незміненого файла зберігає candidate identity;
- змінений файл стає новим кандидатом;
- AI-поля порожні, `review_state=inventory`; класифікація/APPLY ще не виконуються.

У r6 немає UI import, OCR, AI-запитів, move/rename/delete/copy або запису в DocumentVault. Це read-only фундамент dry-run імпорту за `docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md`.
