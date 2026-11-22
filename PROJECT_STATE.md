# PROJECT_STATE — Taxo

**Підтверджено GitHub 22.11.2026 після публікації Test 10.23-r9.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`.

**Current Test:** [10.23-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r9), exact source `9f41c46a4745815cfc7518f7319f6c6f941ba559`, 8 assets, prerelease. Publisher #45045127128 — SUCCESS.

## Stable r4

Stable r4 залишається вручну прийнятою власником версією. Вона містить каталог документів, власні папки, скани/паперовий підпис, редагування учасників наказу, регульовані робочі області та адаптивний перегляд наказу. 37 strict live routes.

## Test r9

r9 продовжує AI-ready шлях після r6 INVENTORY, r7 atomic batch store і r8 verified preview:
- read-only `ANALYZE → PROPOSE` поверх verified batch view;
- versioned proposal format і deterministic ruleset;
- hints для дати, номера, виду, категорії й описової назви;
- confidence/reason/rule version для кожного припущення;
- ambiguity → `needs_review`, без автоматичного вибору;
- існуючі структуровані реквізити не перезаписуються;
- source не перечитується, persisted batch не змінюється;
- немає OCR, зовнішнього AI API, APPLY, DocumentVault/DB write або фізичного сортування.

Exact-source CI `9f41c46a4745815cfc7518f7319f6c6f941ba559`: START #45043933564, Windows #45043933540, Win7 #45043933535, macOS Intel/ARM #45043933592 — SUCCESS; Windows/Win7 Defender + post-scan integrity PASS; publisher #45045127128 — SUCCESS.

## Документна архітектура / AI-ready

Нормативна модель: `docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md`. r6 = INVENTORY, r7 = atomic batch store, r8 = verified deterministic preview, r9 = read-only ANALYZE/PROPOSE. Наступна **10.23-r10** — REVIEW: окреме versioned збереження явних confirm/reject/needs_review рішень без APPLY.

Після r10 — окремий модуль вхідної/вихідної кореспонденції за draft #543. APPLY імпортних пропозицій — лише після окремого рішення власника.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
