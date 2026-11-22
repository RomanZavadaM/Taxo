# Taxo 10.23-r9 — read-only ANALYZE → PROPOSE metadata hints

**Робочий Test-кандидат. Stable/Latest залишається 10.23-r4; поточний опублікований Test — 10.23-r8.**

10.23-r9 продовжує безпечний AI-ready імпорт старої бази документів після r6 INVENTORY, r7 atomic batch store і r8 verified preview.

## Що додано

- versioned read-only proposal format `taxo.document-import-proposals.v1`;
- deterministic ruleset `taxo.document-metadata-hints.v1`;
- пропозиції для `document_date`, `document_number`, `document_kind`, `category` і описової `title`;
- кожна пропозиція має confidence, reason і версію правила;
- неоднозначні дати або категорії не вгадуються, а переходять у `needs_review`;
- вже наявні структуровані реквізити не переписуються;
- короткі маркери та номерні позначки мають межі токенів, щоб не класифікувати випадкові підрядки;
- для незмінного verified batch результат детермінований.

## Межі безпеки

- аналіз працює тільки з verified in-memory view r8 batch;
- source-файли не відкриваються повторно і не змінюються;
- persisted inventory/report batch не змінюється;
- немає OCR, зовнішніх AI/model API або автоматичного APPLY;
- немає запису в DocumentVault/БД, зміни паперового підпису чи юридично значимих реквізитів;
- немає move/rename/delete/copy або фізичного сортування архіву.

## Перевірки

Функціональний prep PR #599 на фінальній голові пройшов 1615/1615 regression-тестів у START та повні Windows, Windows 7 і macOS Intel/ARM gates; Windows/Win7 також пройшли Defender та integrity.

Stable/Latest змінюється тільки окремим рішенням власника.
