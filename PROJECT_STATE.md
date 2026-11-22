# PROJECT_STATE — Taxo

**Підтверджено GitHub 22.11.2026 після публікації Test 10.23-r8.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`.

**Current Test:** [10.23-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r8), exact source `d3d34f7a0fc3de88280324eaeb2d97a72c172359`, 8 assets, prerelease. Publisher #44948759163 — SUCCESS.

## Stable r4

Stable r4 залишається вручну прийнятою власником версією. Вона містить каталог документів, власні папки, скани/паперовий підпис, редагування учасників наказу, регульовані робочі області та адаптивний перегляд наказу. 37 strict live routes.

## Test r8

r8 продовжує AI-ready шлях після read-only inventory r6 та atomic batch store r7:
- verified read-only batch reader;
- format/batch/checksum validation з fail-closed поведінкою;
- deterministic preview sorting за датою, номером, категорією/видом і source fallback;
- порожні/невідомі значення сортуються в кінець;
- natural number sort;
- stable identity tie-breaker;
- duplicates/errors/skipped/unresolved metadata не приховуються;
- source archive і збережений batch не змінюються.

Exact-source CI `d3d34f7a0fc3de88280324eaeb2d97a72c172359`: START #44947743150, Windows #44947743153, Win7 #44947743132, macOS Intel/ARM #44947743115 — SUCCESS; Windows/Win7 Defender + post-scan integrity PASS; publisher #44948759163 — SUCCESS.

## Документна архітектура / AI-ready

Нормативна модель: `docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md`. r6 = INVENTORY, r7 = atomic batch store, r8 = verified deterministic preview. Наступна **10.23-r9** — read-only ANALYZE/PROPOSE contract і deterministic metadata hints без OCR, зовнішніх AI-викликів та APPLY.

Кореспонденція лишається окремим наступним модулем за draft #543 після безпечної основи документного імпорту.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
