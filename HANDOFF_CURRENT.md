# HANDOFF_CURRENT — Taxo

**20.11.2026 — 10.23-r4 прийнято власником і підвищено до Stable/Latest.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 файлів, `prerelease=false`, GitHub Latest. Stable promotion workflow #44811800328 — SUCCESS. Тег не пересувався.

**Поточний Test:** [10.23-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r5), exact source `dc5dcaa3aa86b4d42cfdec8019fbc73c73f2be3a`, 8 файлів, prerelease=true. **Stable/Latest лишається 10.23-r4.** v10.23-r3 навмисно не публікувався.

## Що входить у Stable r4

- Усі можливості r1: каталог документів, шаблони/Word-редакції, DocumentVault, скани, паперовий підпис, власні папки, пари водій–ТЗ, календар шляхівок.
- r2: редагування ролі/примітки вже доданого учасника/ТЗ.
- r3 (інтегрований без окремого релізу): регульована область «Документи → Бланки», регульоване дерево каталогу, накопичення вибору учасників при пошуку, тема активного наказу й прямий перехід до закріплень.
- r4: адаптивні кнопки DOCX/PDF/JPG і нижні дії у перегляді наказу; виправлено приховування блоку форматів при 760×560; опис «Експлуатації» адаптується до ширини.
- Реєстр захисту має **37 strict live routes**.

Exact-source CI для stable source: START #44803423646, Windows #44803423874, Win7 #44803423649, macOS Intel/ARM #44803423740 — SUCCESS; Defender/integrity PASS.

Власник 20.11.2026 повідомив, що 10.23-r4 працює, і прямо наказав злити її в Stable. Це є ручним прийманням саме r4. #553/#556 залишаються відкритими як ширші задачі повного наскрізного контролю, а не як блокер stable r4.

## Активна робота

**10.23-r5 уже розпочата:** PR #576 `feature/10.23-r5-document-catalog-small-viewport`, head `3a084fa47784d9d7765f733a84e9f8951b0d4a03`. Це один пов'язаний пакет із залишку #556 для малого viewport «Документи → Каталог»: дерево, таблиця, горизонтальна прокрутка, 12 основних дій і 6 дій власних папок у межах 760×470. Бізнес-логіка/БД/файли не змінюються.

Exact-head CI PR #576 завершено повністю: START, Windows, Win7, macOS Intel/ARM — SUCCESS. **PR #576 ще не merged і не є релізом.** За CI кандидат готовий до інтеграції; Stable/Latest до окремого рішення власника залишається 10.23-r4.

#562/#553/#556 не закривати автоматично; draft #543/#395 не чіпати. GitHub — джерело коду й релізів; Google Drive — резерв документації/стану/методології, а не дубль кожної збірки.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.

## 10.23-r5 і наступний документний крок

10.23-r5 опублікована як Test prerelease після guarded publisher #44927558482 — SUCCESS. Пакет доводить «Документи → Каталог» для малого viewport 760×470 і додає 38-й strict live route `documents.catalog_small_viewport`. Stable не змінювався.

Після r5 власник визначив нову обов'язкову вимогу: існуюча база документів має бути придатна для безпечного сортування за допомогою ШІ. Нормативна специфікація вже в main: `docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md`. Принципи: незмінний оригінал; один фізичний файл — багато логічних представлень; staging INVENTORY→ANALYZE→PROPOSE→REVIEW→APPLY→VERIFY; SHA256 exact duplicates; стабільний document_id/manifest; окремі види дат; confidence/review; idempotent повторний scan; import batch + rollback; dry-run перед APPLY.

**Наступний кодовий slice — 10.23-r6: inventory/dry-run core для існуючої бази документів без фізичного переміщення/перейменування файлів.**
