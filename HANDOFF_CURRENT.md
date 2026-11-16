# HANDOFF_CURRENT — Taxo

**Підтверджено 16.11.2026 після live GitHub.**

## Поточний стан

- Завершена продуктова ревізія: **10.20-r3**.
- Product PR #454 merged; product merge commit: `42e7a1d71fbf80cc1b4c85551bb710d2f4d13496`.
- Release-notes PR #455; exact product/release source: `eec360a965738ecab97f38aeaa5ab8a7452ee1dd`.
- Test prerelease: [v10.20-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r3), 6 assets (Windows, Win7, macOS Intel, macOS ARM, START, SHA256).
- Release-trigger PR #456 merged as `fefeb885b81b54709e69010a1251051ef7faf842`; publisher `43844149251` SUCCESS.
- Stable / GitHub Latest: **v10.18-r3**, без змін.

## Що зроблено в 10.20-r3

Завершено користувацький міст між контрольованою prepared DOCX-редакцією та DocumentVault без повторення r2 core.

- у каталозі підготовлених документів є явна дія **«Зберегти вибрану редакцію у сховищі»**;
- у DocumentVault реєструється тільки конкретна вибрана prepared DOCX-редакція через чинний immutable core;
- запис виконується поза Tk UI thread, а UI отримує лише результат;
- додано окремий read-only перегляд DocumentVault зі списком і карткою;
- видно title/kind/date/status, document revision, PaperDocuments/PreparedDocuments/CompanyTemplate provenance та exact SHA-256;
- повторне збереження тієї самої редакції дає зрозуміле повідомлення, а порушення index/object/hash лишаються fail-closed;
- `main.py` не отримав нової бізнес-логіки;
- auto-migration, scans/originals, digital signature та implicit «підписано» не додавались.

## Перевірки

- Final product PR head: `b5fd4e2a4223d3cfef2d1ea09279b7e7cee3a376`.
- Product merge: `42e7a1d71fbf80cc1b4c85551bb710d2f4d13496`.
- Exact product/release source: `eec360a965738ecab97f38aeaa5ab8a7452ee1dd`.
- Exact-main START/source `43842526461` — SUCCESS, **1385/1385**.
- Windows `43842526290` — SUCCESS.
- Windows 7 `43842526261` — SUCCESS.
- macOS Intel + ARM `43842526193` — SUCCESS.
- Windows/Win7 Defender malware gates + post-scan integrity — PASS.
- Publisher `43844149251` — SUCCESS; release target exactly product/release source above, 6 assets.
- Stable/Latest через GitHub API: `v10.18-r3`.

## Що ще не зроблено

- DocumentVault поки відкривається окремим read-only переглядом, а не як джерело в основному агрегованому списку «Документи».
- Один і той самий логічний документ у PaperDocuments і DocumentVault ще не об'єднується в одну картку з двома походженнями.
- Auto-migration чинних PaperDocuments.
- Опціональні scans/originals і вкладення.
- Signature evidence / digital signature та будь-який автоматичний статус «підписано».

## Одна наступна дія

**Наступна дозволена кодова ревізія: 10.20-r4.** Додати DocumentVault як read-only source-adapter до чинного агрегованого каталогу «Документи» й безпечно об'єднати той самий prepared-документ із PaperDocuments + Vault в одну логічну картку з видимими джерелами. Не зливати записи лише за назвою/датою; ідентичність має спиратися на збережені source IDs/provenance. Без auto-migration, scans/originals, signatures, зміни бізнес-статусів або роздування `main.py`.

Перед кодом: START_HERE → HANDOFF_CURRENT → private profile → live GitHub → READ/VERIFY/RECONCILE.

Незмінні правила: TemplateLibrary read-only; власні шаблони — CompanyTemplates; Stable/Latest змінюється тільки за прямою командою власника; executable не запускати для перевірки безпеки.
