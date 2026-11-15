# HANDOFF_CURRENT — Taxo

**Підтверджено 15.11.2026 після live GitHub.**

## Поточний стан

- Продуктова ревізія: **10.19-r9**. Product PR #440 merged.
- Exact product/release source: `bc2bb95d26f0d89d40acb98a3c37efaee6ab060b`.
- Test prerelease: [v10.19-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r9), 6 assets (4 portable, START, SHA256); publisher `43754690935` SUCCESS.
- Stable / GitHub Latest: **v10.18-r3**, без змін.
- Release trigger PR #441 merged; release-trigger main commit `0749e99403c681dbab3701208c02ef79660e2076`.

## Що зроблено в r9

Збережені immutable `PreparedDocuments` тепер мають окремий список: після перезапуску Taxo чернетку можна знайти, переглянути, повторно експортувати в DOCX або явно додати до каталогу, не заповнюючи шаблон заново.

Для prepared DOCX додано контрольовану історію Word-редакцій. Taxo створює **зовнішню копію для редагування**, а змінений DOCX приймає назад як нову редакцію `r2`, `r3` і далі. Попередній файл не перезаписується. Зберігаються family ID, номер редакції, ID попередньої редакції та SHA-256 фактичного DOCX. Старі r8 prepared-записи читаються як r1 без міграції.

Prepared-файл із каталогу не відкривається напряму для редагування: Taxo пропонує контрольовану копію. Імпорт перевіряє DOCX і відхиляє незмінений файл, небезпечний шлях та спробу підмінити файл каталогу. Записи `PaperDocuments/index.json` серіалізовані одним store-level lock, щоб два вікна Taxo не втрачали записи при одночасному збереженні.

## Перевірки

- Exact-main START `43753739079` SUCCESS, 1352 regression tests.
- Windows `43753739074` SUCCESS; Windows 7 `43753739194` SUCCESS.
- macOS Intel + ARM `43753739130` SUCCESS.
- Windows/Win7 Microsoft Defender + post-scan integrity PASS.
- Publisher `43754690935` SUCCESS; release target exactly `bc2bb95d26f0d89d40acb98a3c37efaee6ab060b`, 6 assets.
- Stable/Latest через GitHub API підтверджено як `v10.18-r3`.

## Що ще не зроблено

- PDF/print із вибраної контрольованої редакції prepared-документа.
- Універсальний DocumentVault, скани/оригінали, підписні докази та окремий життєвий цикл фінальних документів.
- Prepared DOCX і надалі не означає, що документ проведений, затверджений або підписаний.

## Одна наступна дія

**Наступна дозволена кодова ревізія: 10.19-r10.** Додати окремий PDF/print path із вибраної контрольованої редакції prepared-документа: без перезапису DOCX, без автоматичного статусу підпису/проведення і без одночасного введення DocumentVault чи сканів. Спершу READ → VERIFY → RECONCILE за `START_HERE.md`, live GitHub і приватним Taxo-profile.

Незмінні правила: TemplateLibrary read-only, власні шаблони CompanyTemplates, код не концентрувати в main.py, Stable/Latest тільки за прямою командою власника, не запускати executable для перевірки безпеки.
