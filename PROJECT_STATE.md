# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 15.11.2026.**

- Завершений product checkpoint: **10.19-r9** (PR #440).
- Exact product/release source SHA `bc2bb95d26f0d89d40acb98a3c37efaee6ab060b`.
- Test prerelease [v10.19-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r9), publisher `43754690935` SUCCESS; 4 portable + START + SHA256.
- Stable/Latest: **v10.18-r3** unchanged.
- Release PR #441 merged as `0749e99403c681dbab3701208c02ef79660e2076`.

## Функціональний результат

r9 закриває наступний розрив у шляху шаблон → чернетка → prepared snapshot → DOCX → каталог. Збережені PreparedDocuments можна повторно знайти після перезапуску, переглянути, повторно експортувати або явно додати до каталогу.

Prepared DOCX тепер має контрольовану історію зовнішніх Word-редакцій: окрема копія для редагування, імпорт назад як r2/r3…, незмінний попередній файл, family/revision/previous-ID/content-SHA lineage. Пряме редагування файла каталогу не пропонується. Старі r8 prepared-записи сумісні як r1 без міграції. Паралельні записи PaperDocuments серіалізовані, щоб не губити index.json.

Це все ще стан `prepared`: він не створює факту проведення, затвердження чи підпису.

## CI та security gates

Exact-main: START `43753739079`, Windows `43753739074`, Win7 `43753739194`, macOS Intel/ARM `43753739130` — всі SUCCESS. Windows/Win7 Defender і post-scan integrity PASS. Publisher `43754690935` SUCCESS; release target — exact product SHA, 6 assets. GitHub Latest/Stable підтверджено як v10.18-r3.

## Наступна ревізія

**10.19-r10** — окремий PDF/print path із вибраної контрольованої редакції prepared-документа. Не перезаписувати DOCX, не додавати в цей slice DocumentVault, скани/оригінали чи автоматичний статус підпису/проведення. Нові зразки не вносити у read-only TemplateLibrary; CompanyTemplates — користувацькі копії.

## Recovery

Читати START_HERE.md → HANDOFF_CURRENT.md → private profile `profile/taxo` → звірити live GitHub. Issue #61 — журнал змін; `WORKLOG.md` — історія.

## Історичний якір (збережено)

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
