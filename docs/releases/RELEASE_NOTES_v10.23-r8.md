# Taxo 10.23-r8 — verified batch reader і deterministic sorting preview

**Робочий Test-кандидат. Stable/Latest залишається 10.23-r4; поточний опублікований Test — 10.23-r7.**

- відкриває тільки керований r7 import batch, а не source-архів;
- перевіряє format, batch ID, source root і checksum manifest;
- unknown future inventory format / missing / malformed batch — fail-closed;
- read-only preview режими: `date_desc`, `number_asc`, `category_asc`, `source_asc`;
- порожні/невідомі дата, номер і категорія йдуть у кінець;
- natural number sort: `2-A` перед `10-A`;
- stable candidate/document identity — остаточний tie-breaker;
- exact duplicate groups, errors і skipped records зберігаються у preview;
- однаковий batch дає однаковий порядок між запусками.

У r8 немає OCR, AI ANALYZE/PROPOSE/APPLY, registry write або move/rename/delete/copy source-файлів. Це verified read-only view для майбутнього AI та ручного review.
