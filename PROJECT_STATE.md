# PROJECT_STATE — Taxo

**Підтверджено GitHub 22.11.2026 після публікації Test 10.23-r10.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`.

**Current Test:** [10.23-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r10), exact source `f87991c624a971fe3ffd4112e5dfde9fd9e4b6cd`, 8 assets, prerelease. Publisher #45049398522 — SUCCESS.

## Stable r4

Stable r4 залишається вручну прийнятою власником версією. Вона містить каталог документів, власні папки, скани/паперовий підпис, редагування учасників наказу, регульовані робочі області та адаптивний перегляд наказу. 37 strict live routes.

## Test r10

r10 завершує безпечний перед-APPLY цикл старого архіву документів:
- r6 INVENTORY;
- r7 atomic batch store;
- r8 verified deterministic preview;
- r9 read-only ANALYZE/PROPOSE;
- r10 explicit REVIEW без APPLY.

REVIEW зберігається окремо, має confirm/reject/needs_review, exact proposal fingerprint, candidate/hash binding, atomic persistence та fail-closed перевірку stale/tampered стану. Source, import batch, DocumentVault/БД та паперовий підпис не змінюються.

Exact-source CI `f87991c624a971fe3ffd4112e5dfde9fd9e4b6cd`: START #45048321322, Windows #45048321299, Win7 #45048321313, macOS Intel/ARM #45048321471 — SUCCESS; Windows/Win7 Defender + post-scan integrity PASS; publisher #45049398522 — SUCCESS.

## Наступний етап

Після `10.23-r10` наступна ревізія — **10.24-r1**.

Починається окремий модуль **вхідної/вихідної ділової кореспонденції**: доменна модель і безпечне збереження реєстру, окремі нумерації incoming/outgoing, кореспонденти, тема, строки/контроль, відповіді та зв'язки з готовими документами. Не реалізовувати імпортний APPLY без окремого рішення власника.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
