# HANDOFF_CURRENT — Taxo

**Актуально на 14.11.2026.**

## Поточний стан

- Поточний продуктовий checkpoint: **10.19-r3**.
- Exact product / release source: `a89291553bca88a1b792d45f56cc99d5e93876b7`.
- **Stable / Latest:** `v10.18-r3` — без змін.
- **Поточний тестовий реліз:** `v10.19-r3 — Test Portable`.
- r3 prerelease: 4 Portable + START + SHA256, без Setup.
- Виданий `v10.19-r2` не переписаний; r3 є окремою коригувальною ревізією.

## 10.19-r3 — що виправлено

Після публікації r2 у статичному перегляді UI-коду знайдено, що save-worker редактора читав Tk `StringVar` напряму з background thread.

У r3:
1. Назва шаблону зчитується в UI thread **до** запуску worker.
2. Worker отримує звичайний Python-рядок і не звертається до Tk.
3. Додано regression-контракт, який забороняє `title.get()` у save-worker.
4. Функціональність r2 не розширювалась.
5. Vendor `TemplateLibrary` лишається read-only.
6. `CompanyTemplates`, історія власних редакцій та SHA-concurrency працюють за контрактом r2.

## Exact-main перевірки r3

Для `a89291553bca88a1b792d45f56cc99d5e93876b7`:
- START/source — `43598231924` SUCCESS;
- Windows — `43598231921` SUCCESS;
- Windows 7 — `43598231945` SUCCESS;
- macOS Intel + ARM — `43598231954` SUCCESS;
- Windows і Windows 7 — Microsoft Defender PASS;
- post-scan integrity/hash verification — PASS.

Publisher:
- `43599116472` — SUCCESS;
- immutable release `v10.19-r3`;
- release target = exact product source `a89291553bca88a1b792d45f56cc99d5e93876b7`;
- 6 assets: Windows, Windows 7, macOS Intel, macOS ARM, START, SHA256.

## Release rule

Повний успішний exact-SHA комплект START + Windows + Windows 7 + macOS Intel + macOS ARM після security/integrity gates → **Test prerelease**, якщо такого release ще немає. Stable автоматично не змінюється.

## Одна наступна дія

**Наступна кодова ревізія — 10.19-r4.**

Повернутись до відкладеного функціонального slice:
- типізована підстановка фактичних даних у вибрану власну редакцію;
- in-memory чернетка для preview;
- шаблон при preview не змінюється;
- відсутні обов'язкові поля дають явну помилку;
- не робити сліпий string-replace, який руйнує блокову структуру;
- preview не створює бізнес-факт наказу/інструктажу;
- Word/PDF і `DocumentArchive` не змішувати в цей slice.

## Незмінні правила

- Виданий номер ревізії не переписувати і не використовувати повторно.
- Stable/Latest змінювати лише за прямим рішенням власника.
- Не просити власника вручну запускати CI/build, якщо це можна зробити через GitHub.
- Код лишається модульним і читабельним для людини.
- Recovery: `START_HERE.md` → цей файл → `PROJECT_STATE.md` → live GitHub → Issue #61.
