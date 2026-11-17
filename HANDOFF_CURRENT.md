# HANDOFF_CURRENT — Taxo

**Актуальний стан 17.11.2026, підтверджено live GitHub.**

## Поточний стан

- База перед recovery: main `d575f1b51caaf8f659dd2c2dc5f24b73271138af`.
- **10.21-r4 завершена, інтегрована й опублікована як Test prerelease.**
- Product PR #500 merged: immutable product/release source `abc0d8848752b70d50f8d2d55983ed83159f24a7`; final PR head `4540da0b17b85348195701f108adeaf33f5ad3f7`.
- Exact-source CI: START run `44125366421` — **1454/1454**; Windows `44125366461`; Win7 `44125366427`; macOS Intel/ARM `44125366431` — SUCCESS. Defender та post-scan integrity PASS.
- Release-trigger PR #501 merged як `d575f1b51caaf8f659dd2c2dc5f24b73271138af`; publisher run `44127599704` attempt 2 — SUCCESS. Attempt 1 зупинився на тимчасовому HTTP 503 (artifact egress) під час скачування вже зібраного Mac Intel; повторено лише публікатор, без зміни продукту.
- [v10.21-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r4): Test prerelease, **6 файлів** (4 Portable + START + SHA256); tag прив'язаний до exact `abc0d8848752b70d50f8d2d55983ed83159f24a7`.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), 8 файлів, без змін; stable marker `10.21-r2`.

## Зміни 10.21-r4

У загальному каталозі «Документи» натискання заголовка **«Дата»** перемикає новіші ▼ / старіші ▲. Сортується **повний відфільтрований список до пагінації**; записи без дати/з некоректною датою — останніми в обох напрямках. Однакові дати зберігають початковий відносний порядок. Сортування поєднується з пошуком, джерелом, типом, сканами та періодом.

Не змінено даних, сховища, файлів, scan/backup/restore, бізнес-статусів і доступу. Немає міграції, OCR, КЕП чи auto «підписано». Інші колонки не змінювались.

## Recovery та наступна дія

Fresh verification r4: main `96c3fd4516addc0e95a93f3df024f8e97a62f3ac`, 412 refs, гілок r4 не було; єдиний старий PR #395 — docs-only. Перший тест r4 знайшов одну невідповідність очікування порядку рівних дат; виправлено **лише тест**, продукт не змінювали. Після цього всі exact-source перевірки SUCCESS.

**10.21-r5 не розпочата.** Після наступної fresh GitHub verification вибрати один вузький пункт Issue #289. Не повторювати r4; не рухати Stable без прямої команди.

Порядок відновлення: `START_HERE.md` → `HANDOFF_CURRENT.md` → private `profile/taxo` → live GitHub (включно з refs без PR). TemplateLibrary read-only; власні шаблони — CompanyTemplates. Працювати через GitHub і хмарні перевірки, не запускати локальні executable.
