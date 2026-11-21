# PROJECT_STATE — Taxo

**Підтверджено GitHub 21.11.2026 після публікації Test 10.23-r6.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`.

**Current Test:** [10.23-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r6), exact source `5a321e98c39443f3d37c89837352402df4542551`, 8 assets, prerelease. Publisher #44933358679 — SUCCESS.

## Stable r4

Stable r4 залишається вручну прийнятою власником версією. Вона містить каталог документів, власні папки, скани/паперовий підпис, редагування учасників наказу, регульовані робочі області та адаптивний перегляд наказу. 37 strict live routes.

## Test r6

r6 додає перший безпечний кодовий фундамент для майбутнього AI-ready імпорту існуючих документів:
- read-only recursive inventory regular files;
- relative/source path, name, size, MIME, mtime, SHA256;
- stable candidate identity для незміненого файла;
- versioned machine-readable manifest;
- exact duplicates тільки за однаковим SHA256;
- symlink skip;
- без OCR, AI-класифікації, move/rename/delete/copy та без APPLY.

Exact-source CI `5a321e98c39443f3d37c89837352402df4542551`:
- START #44932279502 — SUCCESS;
- Windows #44932280241 — SUCCESS, Defender/integrity PASS;
- Win7 #44932279586 — SUCCESS, Defender/integrity PASS;
- macOS Intel/ARM #44932279465 — SUCCESS;
- publisher #44933358679 — SUCCESS.

## Документна архітектура / AI-ready

21.11.2026 нормативну модель інтегровано в main: `docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md`. r6 реалізує лише INVENTORY. Наступна ревізія **10.23-r7** — атомарне збереження dry-run manifest/report у Taxo workspace з batch identity і без змін source-архіву. AI ANALYZE/PROPOSE/APPLY ще не реалізовувати.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
