# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 17.11.2026.**

- Актуальна продуктова ревізія: **10.21-r4**, інтегрована й опублікована як Test prerelease.
- Product PR #500 merged; exact immutable release source `abc0d8848752b70d50f8d2d55983ed83159f24a7`.
- Exact-source CI: START `44125366421` — **1454/1454**; Windows `44125366461`, Win7 `44125366427`, macOS Intel/ARM `44125366431` — SUCCESS. Defender та post-scan integrity PASS.
- Release-trigger PR #501 merged `d575f1b51caaf8f659dd2c2dc5f24b73271138af`; publisher `44127599704`, attempt 2 SUCCESS після transient HTTP 503 artifact egress в attempt 1.
- [v10.21-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r4): Test prerelease, 6 файлів — 4 Portable, START і SHA256, exact tag target `abc0d8848752b70d50f8d2d55983ed83159f24a7`.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), повний випуск із 8 файлів, source `b104f94ace0ae355df79c914b3be6f39417bd6e9`, без змін.

## Інтегрований результат 10.21-r4

- Натискання заголовка «Дата» в каталозі «Документи» перемикає сортування: новіші ▼ / старіші ▲.
- Сортування відбувається після існуючих пошуку та фільтрів, але до пагінації.
- Порожні й некоректні дати показуються в кінці незалежно від напряму.
- Однакові дати не втрачають відносний порядок поточного джерела.
- Зміна суто read-only: сховище, скани, готові файли, backup/restore, бізнес-статуси та схема БД без змін.
- КЕП, OCR, auto «підписано» та нові залежності не додавалися.

## Активна кодова ревізія

Немає. **10.21-r5 ще не розпочата.**

## Наступна дозволена ревізія

**10.21-r5** після fresh GitHub verification і вибору одного вузького кроку з Issue #289. Старі ревізії та immutable теги не використовувати повторно; Stable змінюється лише прямою командою власника.

## Recovery

Читати `START_HERE.md` → `HANDOFF_CURRENT.md` → private `profile/taxo` → live GitHub (у тому числі гілки без PR). Issue #61 — live журнал, WORKLOG — технічна історія. Детальний аудит r4: [сортування дати](docs/maintenance/AUDIT_DOCUMENT_DATE_SORT_10_21_R4.md).

На старті r4 перевірено 412 refs; r4 branch/PR не існували. Перший START на проміжному head мав одну помилку нового тесту (порядок документів з однаковою датою), виправлено очікування без продуктових змін. Після цього 1454/1454 і повні платформи PASS.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
