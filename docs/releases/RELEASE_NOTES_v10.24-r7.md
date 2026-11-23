# Taxo 10.24-r7 — наскрізний контроль учасників наказу

**Test-кандидат. Stable/Latest залишається 10.24-r3; поточний опублікований Test до видачі цього кандидата — 10.24-r6.**

10.24-r7 продовжує контрольний аудит Taxo після r6. Бізнес-правила наказів не змінюються. Ревізія закриває наскрізну узгодженість структурованого блоку **«Учасники / ТЗ»** між реєстром, відкритим preview, DOCX/PDF, історією і backup/restore.

## Що захищено

- додавання працівників до структурованого переліку;
- додавання ТЗ;
- редагування ролі / примітки;
- вилучення учасника / ТЗ;
- автоматичне оновлення вже відкритого preview після add/edit/remove;
- зрозуміла історична подія `entity_update = «Змінено роль / примітку»`;
- preview прямо пояснює, що в DOCX/PDF/JPG структурований перелік друкується окремою сторінкою;
- DOCX і PDF використовують той самий frozen participant snapshot;
- full workspace backup/restore зберігає entity identity, role, note, snapshot і sequence;
- live UI preservation guard включає «Змінити роль / примітку…».

## Strict live-control

До r6-контролю додано три відсутні order-participant routes:
- `operations.entity_add_vehicle` — «Додати ТЗ…»;
- `operations.entity_remove` — «Прибрати вибрані»;
- `operations.entity_preview_sync` — автооновлення Preview після зміни учасників / ТЗ.

Разом із уже наявними `operations.entity_search_selection` і `operations.entity_edit` блок «Учасники / ТЗ» має 5 окремих live routes.

У Taxo тепер **58 strict routes** загалом. Historical r6 correspondence contract при цьому лишається точним: **17 correspondence routes** не змінені. r6 guard був виправлений так, щоб зберігати exact correspondence set, але дозволяти наступним ревізіям додавати маршрути інших модулів.

## Prep verification

Prep PR #630 final head `d252143339c5406264868bfe92f804a75d348fab`:
- START #45213479378 — SUCCESS;
- Windows #45213479658 — SUCCESS;
- Windows 7 #45213479371 — SUCCESS;
- macOS Intel/ARM #45213479464 — SUCCESS;
- Windows/Win7 Defender та post-scan integrity — SUCCESS.

Prep merged у main як `31153fb3c706c746b711c5382c37edc2ecddab53`.

## Межі r7

- не змінюється логіка статусів наказу;
- не змінюється нумерація наказів;
- не змінюються правила паперового підпису;
- не додаються нові типи документів;
- correspondence r1–r6 не змінюється;
- automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не входять у r7.

Stable/Latest змінюється тільки за прямим рішенням власника.
