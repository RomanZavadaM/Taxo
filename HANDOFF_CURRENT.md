# HANDOFF_CURRENT — Taxo

**Підтверджено 15.11.2026 після live GitHub.**

## Поточний стан

- Продуктова ревізія: **10.19-r10**. Product PR #443 merged.
- Exact product/release source: `ff93ab2ddfe92f4eb8079d890ad8e7ffd7fe03e2`.
- Test prerelease: [v10.19-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r10), 6 assets (4 portable, START, SHA256); publisher `43758634481` SUCCESS.
- Stable / GitHub Latest: **v10.18-r3**, без змін.
- Release trigger PR #444 merged; release-trigger main commit `dade651e451f6ba89de7580348cad705ea8e170e`.

## Що зроблено в r10

При підготовці документа з власного CompanyTemplates, якщо шаблон використовує `company.name`, Taxo підставляє актуальну назву підприємства з таблиці `company` активної робочої БД. Це лише початкове значення конкретної чернетки: `TemplateLibrary` і `CompanyTemplates` не переписуються, поле залишається редагованим до preview.

У каталозі для контрольованої prepared DOCX-редакції додано **«PDF / друк…»**. PDF формується саме з вибраної r1/r2/r3…, зберігається окремо в `Output` і відкривається чинним переглядачем Taxo, де доступний друк. Створення PDF не змінює DOCX, історію редакцій, prepared/signature/business status.

Конвертер використовує наявні python-docx + ReportLab, без нової залежності. Він переносить текст, заголовки, таблиці, базове вирівнювання і page breaks. Якщо DOCX має вкладені зображення, Taxo відмовляється від неповного PDF з явним поясненням замість тихої втрати оформлення.

## Перевірки

- Final PR head `14d41a88fd622547f04ef4eebc07a061210d51a3`: START 1362/1362, Windows, Win7, macOS Intel/ARM — SUCCESS; Defender/integrity PASS.
- Exact-main START `43757634383` SUCCESS, 1362 regression tests.
- Windows `43757634381` SUCCESS; Windows 7 `43757634387` SUCCESS.
- macOS Intel + ARM `43757634384` SUCCESS.
- Windows/Win7 Microsoft Defender + post-scan integrity PASS.
- Publisher `43758634481` SUCCESS; release target exactly `ff93ab2ddfe92f4eb8079d890ad8e7ffd7fe03e2`, 6 assets.
- Stable/Latest через GitHub API підтверджено як `v10.18-r3`.

## Що ще не зроблено

- Перенесення вкладених зображень та складнішого Word-layout у prepared PDF.
- Універсальний DocumentVault, скани/оригінали, підписні докази та життєвий цикл фінальних документів.
- Prepared DOCX/PDF не означає, що документ проведений, затверджений або підписаний.

## Одна наступна дія

Після r10 номерна лінія переходить на **10.20-r1**. Наступний безпечний slice: підтримати вкладені зображення у контрольованому prepared DOCX → PDF/print без тихої втрати даних і без одночасного введення DocumentVault чи статусів підпису. Перед кодом — READ → VERIFY → RECONCILE за `START_HERE.md`, live GitHub і приватним Taxo-profile.

Незмінні правила: TemplateLibrary read-only, власні шаблони CompanyTemplates, код не концентрувати в main.py, Stable/Latest тільки за прямою командою власника, executable не запускати для перевірки безпеки.
