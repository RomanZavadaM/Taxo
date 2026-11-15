# HANDOFF_CURRENT — Taxo

**Підтверджено 15.11.2026 після live GitHub.**

## Поточний стан

- Продуктова ревізія: **10.19-r8**. Product PR #437 merged.
- Exact product/release source: `4829bc7e3369442cc7cee7ad9ec8797fc26362e5`.
- Test prerelease: [v10.19-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r8), 6 assets (4 portable, START, SHA256); publisher `43748041618` SUCCESS.
- Stable / GitHub Latest: **v10.18-r3**, без змін.
- Release trigger PR #438 merged; release-trigger main commit `882c9d5e44f919d63edd0f4574416838a82f503f`.

## Що зроблено в r8

Після створення власного CompanyTemplates → чернетки → immutable prepared snapshot у preview є окрема дія **«Зберегти DOCX у каталозі Taxo»**. Вона створює DOCX саме з перевіреного snapshot-а та реєструє його в існуючому `Data/PaperDocuments`, доступному через загальний каталог документів.

Зберігаються `prepared_snapshot_id`, `company_template_id`, редакція і SHA джерела, стан `prepared`, `paper_signed=false`. Дубль тієї самої чернетки відхиляється. Старі записи PaperDocuments, накази та інші робочі дані не мігруються й не переписуються. Окремий експорт DOCX у довільну папку не реєструє файл автоматично. Підготовка не дорівнює затвердженню чи підписанню.

## Перевірки

- Exact-main START `43747281993` SUCCESS (1341 regression tests).
- Windows `43747281941` SUCCESS; Windows 7 `43747281957` SUCCESS.
- macOS Intel + ARM `43747281991` SUCCESS.
- Windows/Win7 Microsoft Defender + post-scan integrity PASS.
- Publisher `43748041618` SUCCESS, target exactly `4829bc7e3369442cc7cee7ad9ec8797fc26362e5`.

## Що ще не зроблено

- Перегляд збережених PreparedDocuments через окремий список, без нового заповнення шаблону.
- Внесення назад у Taxo зовнішнього DOCX, який користувач відредагував у Word.
- Історія незмінних редакцій документів, універсальний DocumentVault, скани, PDF/print і підписні докази.

## Одна наступна дія

**Наступна дозволена кодова ревізія: 10.19-r9.** Продовжити наскрізний шлях документа: безпечне повторне відкриття/вибір уже збереженої чернетки та окремо контрольований запис редагованого DOCX як нової редакції без перезапису старого файлу. Спершу READ → VERIFY → RECONCILE за `START_HERE.md`, live GitHub і приватним Taxo-profile.

Незмінні правила: TemplateLibrary read-only, власні шаблони CompanyTemplates, код не концентрувати в main.py, Stable/Latest тільки за прямою командою власника, не запускати executable для перевірки безпеки.
