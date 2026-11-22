# PROJECT_STATE — Taxo

**Підтверджено GitHub 22.11.2026 після публікації Test 10.24-r1.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`.

**Current Test:** [10.24-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r1), exact source `adb6ae40e966d77018c6dc8c1c4fdcbde6a6a827`, 8 assets, prerelease. Publisher #45053863942 — SUCCESS.

## Stable r4

Stable r4 залишається вручну прийнятою власником версією. Вона містить каталог документів, власні папки, скани/паперовий підпис, редагування учасників наказу, регульовані робочі області та адаптивний перегляд наказу. 37 strict live routes.

## Current Test 10.24-r1

10.24-r1 відкриває окрему лінію ділової кореспонденції:
- domain store/service для incoming та outgoing;
- independent annual numbering;
- stable correspondence ID;
- semantic dates не зливаються в одну;
- external correspondent number окремо від нашого реєстраційного номера;
- correspondent/subject/summary/delivery/responsible/due/status metadata;
- explicit response/related links;
- stable document_ref без copy bytes;
- atomic persistence і fail-closed numbering validation;
- workspace full backup/restore зберігає реєстр і next number.

Exact-source CI `adb6ae40e966d77018c6dc8c1c4fdcbde6a6a827`: START #45052687870, Windows #45052687839, Win7 #45052687867, macOS Intel/ARM #45052687880 — SUCCESS; Windows/Win7 Defender + post-scan integrity PASS; publisher #45053863942 — SUCCESS.

Немає UI, attachment store, e-mail automation, OCR/AI APPLY або зміни Stable.

## AI-ready archive path

r6 INVENTORY → r7 batch store → r8 verified preview → r9 ANALYZE/PROPOSE → r10 REVIEW. Цикл лишається без APPLY; source, batch, DocumentVault/БД і паперовий підпис не змінюються. APPLY — тільки після окремого рішення власника.

## Наступна ревізія

**10.24-r2:** контрольовані файли/вкладення кореспонденції + backup/restore. Потрібні immutable bytes або stable link на existing vault, SHA256/metadata, stable attachment ID, correspondence link, safe history semantics. Не вважати attachment доказом відправлення/отримання. UI/e-mail/OCR/AI — пізніше.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
