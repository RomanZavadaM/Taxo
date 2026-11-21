# PROJECT_STATE — Taxo

**Підтверджено GitHub 21.11.2026 після публікації Test 10.23-r5.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`.

**Current Test:** [10.23-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r5), exact source `dc5dcaa3aa86b4d42cfdec8019fbc73c73f2be3a`, 8 assets, prerelease. Publisher #44927558482 — SUCCESS.

## Stable r4

Stable r4 залишається вручну прийнятою власником версією. Вона містить каталог документів, власні папки, скани/паперовий підпис, редагування учасників наказу, регульовані робочі області та адаптивний перегляд наказу. 37 strict live routes.

## Test r5

r5 додає small-viewport hardening «Документи → Каталог»:
- viewport 760×470;
- компактні дерево/таблиця;
- горизонтальна прокрутка;
- 12 основних дій і 6 дій власних папок у видимій області;
- адаптивні ширини великих фільтрів;
- strict route `documents.catalog_small_viewport`, разом 38 маршрутів після інтеграції.

Бізнес-логіка документів, фізичні файли, DocumentVault та БД у r5 не змінювалися.

Exact-source CI `dc5dcaa3aa86b4d42cfdec8019fbc73c73f2be3a`:
- START #44926983535 — SUCCESS;
- Windows #44926983543 — SUCCESS, Defender/integrity PASS;
- Win7 #44926983541 — SUCCESS, Defender/integrity PASS;
- macOS Intel/ARM #44926983524 — SUCCESS;
- publisher #44927558482 — SUCCESS.

## Документна архітектура / AI-ready

21.11.2026 додано обов'язкову вимогу: існуючу базу документів у майбутньому має бути можливо безпечно проінвентаризувати й класифікувати за допомогою ШІ. Детальний нормативний документ підготовлено у draft PR #580; Issue #543 містить принципи й план r6.

Наступний кодовий крок після docs checkpoint — **10.23-r6 read-only inventory**: рекурсивний scan regular files, relative path/name, size, MIME, mtime, SHA256, duplicate groups та versioned manifest/import_batch. Без OCR, AI-класифікації, move/delete або реєстрації у Vault у першому кроці.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
