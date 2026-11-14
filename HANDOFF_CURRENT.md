# HANDOFF_CURRENT — Taxo

**Актуально на 14.11.2026.**

## Поточний стан

- Поточний продуктовий checkpoint: **10.19-r6**.
- Exact product / release source: `eca31f5d61fc382cebc4663ec511619b9dcd69e7`.
- **Stable / Latest:** `v10.18-r3` — без змін.
- **Поточний тестовий реліз:** `v10.19-r6 — Test Portable`.
- r6 prerelease: 4 Portable + START + SHA256, без Setup.
- Product PR: #431.
- Release trigger PR: #432.
- Publisher: `43622926821` SUCCESS.

## 10.19-r6 — що завершено

1. Заповнену `CompanyTemplates` чернетку можна явно зберегти як окремий immutable prepared snapshot.
2. Snapshot зберігає exact `company_template_id`, `source_sha256`, `edit_revision`, normalized facts, rendered structure і rendered content.
3. Сховище окреме: workspace `Data/PreparedDocuments`; у r6 немає update/delete API для створеного snapshot-а.
4. Індекс і файли snapshot-ів перевіряються за SHA-256/розміром; небезпечні/невідомі об'єкти, сирітські файли та порушення індексу відхиляються.
5. Запис файлів атомарний; `PreparedDocuments` входить у повний backup/restore.
6. У preview додано явну дію **«Зберегти підготовлену чернетку»**; Tk-значення не читаються background worker-ом.
7. Snapshot не створює автоматично наказ/інструктаж, DOCX/PDF, фінальний архів, скан чи підпис.
8. Vendor `TemplateLibrary` лишається read-only; власні шаблони — `CompanyTemplates`.
9. Feature-логіка лишилася в окремих модулях; `main.py` не роздувався.

## Exact-main перевірки r6

Для exact product source `eca31f5d61fc382cebc4663ec511619b9dcd69e7`:
- START/source — `43622027078` SUCCESS;
- Windows — `43622027016` SUCCESS;
- Windows 7 — `43622027066` SUCCESS;
- macOS Intel + ARM — `43622027010` SUCCESS;
- Windows/Win7 Microsoft Defender — PASS;
- post-scan integrity/hash verification — PASS.

Publisher:
- `43622926821` — SUCCESS;
- immutable release `v10.19-r6`;
- target = exact product source `eca31f5d61fc382cebc4663ec511619b9dcd69e7`;
- 6 assets: Windows, Windows 7, macOS Intel, macOS ARM, START, SHA256.
- GitHub Latest лишається `v10.18-r3 — Stable`.

## Recovery note r6

Після нестабільного чату live GitHub показав, що r6 уже була розпочата на `work/v10.19-r6-prepared-snapshot`; ревізію не починали повторно. Незавершені version/START guards після обриву були узгоджені без зміни дизайну snapshot storage. Final branch exact head `1535bd7f92facf2d636f9dc7e656653a6eea1a24` пройшов повний платформний CI; PR #431 merged у exact product source вище. Після exact-main PASS PR #432 запустив guarded publisher без зміни Stable.

## Наступна дія

**Наступна кодова ревізія — 10.19-r7.**

Окремий slice: DOCX renderer/export для вже збереженого prepared snapshot-а:
- рендерити з immutable snapshot, а не повторно читати поточний шаблон;
- не змішувати в r7 PDF/print;
- не створювати в r7 фінальний DocumentArchive, scan/signature state або автоматичний business fact;
- зберегти provenance exact template revision і prepared snapshot ID у вихідному документному контексті;
- не переносити feature-логіку в `main.py`.

## Незмінні правила

- Виданий номер ревізії не переписувати і не використовувати повторно.
- Повний успішний exact-SHA комплект усіх платформ → Test prerelease.
- Stable/Latest змінювати лише за прямим рішенням власника.
- `TemplateLibrary` read-only; власні шаблони — `CompanyTemplates`.
- Не створювати нових монолітів; скорочення коду не є ціллю.
- Recovery: START_HERE.md → цей файл → PROJECT_STATE.md → live GitHub → Issue #61.
