# HANDOFF_CURRENT — Taxo

**Актуально на 14.11.2026.**

## Поточний стан

- Поточний продуктовий checkpoint: **10.19-r2**.
- Exact product / release source: `6414e0fbeeca3f60d8bf609bc15fbf66482e5e82`.
- **Stable / Latest:** `v10.18-r3` — без змін.
- **Поточний тестовий реліз:** `v10.19-r2 — Test Portable`.
- r2 prerelease: 4 Portable + START + SHA256, без Setup.
- Після product commit у `main` є тільки release/recovery maintenance; продукт r2 не переписувався.

## 10.19-r2 — що завершено

1. У `CompanyTemplates` з'явився окремий список власних шаблонів і редактор.
2. Vendor `TemplateLibrary` залишається read-only; редактор його не змінює.
3. Редагуються тільки користувацькі текстові частини: назва, опис, тексти/примітки блоків, пункти списків, статичні таблиці та додатки.
4. Службова структура, ID, типи блоків, змінні та data source через редактор не змінюються.
5. Підтримані великі тексти для інструкцій та інструктажів.
6. Кожне «Зберегти» створює новий файл власної редакції; попередній файл зберігається.
7. SHA-256 використовується як optimistic-concurrency token: застаріле друге вікно не може мовчки перезаписати новішу редакцію.
8. «Скасувати» і X попереджають про незбережені зміни.
9. Storage, editor service, list UI та editor UI розділені; редактор не перенесено в `main.py`.
10. Word/PDF, підстановка фактичних даних і `DocumentArchive` у r2 не входять.

## Exact-main перевірки r2

Для `6414e0fbeeca3f60d8bf609bc15fbf66482e5e82`:
- START/source — `43595242155` SUCCESS;
- Windows — `43595242166` SUCCESS;
- Windows 7 — `43595242114` SUCCESS;
- macOS Intel + ARM — `43595242059` SUCCESS;
- Windows і Windows 7 — Microsoft Defender PASS;
- post-scan integrity/hash verification — PASS.

Publisher:
- `43595998112` — SUCCESS;
- immutable release `v10.19-r2`;
- release target = exact product source `6414e0fbeeca3f60d8bf609bc15fbf66482e5e82`;
- 6 assets: Windows, Windows 7, macOS Intel, macOS ARM, START, SHA256.

## Release rule

Якщо нова ревізія вже має повний успішний exact-SHA набір START + Windows + Windows 7 + macOS Intel + macOS ARM і security/integrity gates пройдені, її публікуємо як immutable **Test prerelease**, якщо такого release ще немає. Stable автоматично не змінюється.

## Одна наступна дія

**Наступна кодова ревізія — 10.19-r3.**

Наступний slice: підстановка типізованих фактичних даних у вибрану власну редакцію та формування **чернетки для preview**, без зміни шаблону і без запису готового документа в архів:
- явна помилка для відсутніх обов'язкових полів;
- не робити сліпий string-replace, який руйнує структуру;
- не створювати факти наказу/інструктажу самим preview;
- Word/PDF і `DocumentArchive` не змішувати в цей slice, якщо це зробить його надто великим.

## Незмінні правила

- Виданий номер ревізії не переписувати і не використовувати повторно.
- Stable/Latest змінювати лише за прямим рішенням власника.
- Не просити власника вручну запускати CI/build, якщо це можна зробити через GitHub.
- Код лишається модульним і читабельним для людини.
- Recovery: `START_HERE.md` → цей файл → `PROJECT_STATE.md` → live GitHub → Issue #61.
