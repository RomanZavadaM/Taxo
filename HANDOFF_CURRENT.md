# HANDOFF_CURRENT — Taxo

**21.11.2026 — 10.23-r5 опубліковано як Test prerelease; Stable/Latest лишається 10.23-r4.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`, GitHub Latest.

**Test:** [10.23-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r5), exact source `dc5dcaa3aa86b4d42cfdec8019fbc73c73f2be3a`, 8 assets, prerelease. Tag незмінно вказує на exact source; publisher #44927558482 — SUCCESS.

Exact-source r5 CI: START #44926983535, Windows #44926983543, Win7 #44926983541, macOS Intel/ARM #44926983524 — SUCCESS; Defender/integrity PASS.

## Що додає r5

- «Документи → Каталог» придатний для малого viewport 760×470;
- дерево й таблиця мають компактний початковий розмір і розтягуються у вільний простір;
- горизонтальна прокрутка таблиці доступна;
- 12 основних дій і 6 дій «Мої папки» лишаються на екрані;
- великі фільтри стискаються лише у вузькому режимі й відновлюються при збільшенні;
- strict live route `documents.catalog_small_viewport` збільшує реєстр з 37 до 38 маршрутів;
- бізнес-логіка документів, БД та фізичне сховище не змінювалися.

## Нова обов'язкова вимога до архіву документів

Власник 21.11.2026 визначив, що система збереження/сортування має бути придатна для ШІ, який зможе розібрати вже існуючу базу документів. Нормативні принципи зафіксовані в Issue #543 і draft PR #580:

- оригінал не змінюється;
- один фізичний файл може мати кілька логічних представлень без копій;
- staging: INVENTORY → ANALYZE → PROPOSE → REVIEW → APPLY → VERIFY;
- SHA256 для точних дублікатів;
- окремі document/registration/received/sent/validity dates;
- AI confidence/reason/review state;
- idempotent повторний scan;
- import_batch + журнал + відкат;
- стабільний машинозчитуваний manifest.

Після закриття recovery r5 злити PR #580 і почати **10.23-r6** вузько з read-only inventory старої папки документів: шлях/назва/розмір/MIME/mtime/SHA256, без OCR/AI/move/delete.

#553/#556/#562 залишаються відкритими до окремого повного закриття. Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.
