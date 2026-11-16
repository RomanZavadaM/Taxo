# HANDOFF_CURRENT — Taxo

**Підтверджено 16.11.2026 після live GitHub.**

## Поточний стан

- Завершена продуктова ревізія: **10.20-r2**.
- Product PR #449 merged; product merge commit: `1519ebda983649a524a03fe0d14c8924d53fe2ff`.
- Exact product/release source після release-notes PR #450: `21eb1f668fbd6e915321afe40e2c78d105cdd48b`.
- Test prerelease: [v10.20-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r2), 6 assets (Windows, Win7, macOS Intel, macOS ARM, START, SHA256).
- Release-trigger PR #451 merged; release-trigger main commit `8ec2d07c4e7332748e419e9c7fad1eb6384888df`.
- Stable / GitHub Latest: **v10.18-r3**, без змін.

## Що зроблено в 10.20-r2

Додано окремий модуль `document_vault_store.py` — базове захищене ядро універсального сховища готових та архівних документів.

- запис відбувається лише явною дією для конкретної контрольованої prepared DOCX-редакції;
- у `Data/DocumentVault` зберігається незмінна точна копія файла, а не посилання на змінний зовнішній DOCX;
- реєстр фіксує PaperDocuments ID, prepared snapshot ID, family/revision, CompanyTemplate ID/revision/source SHA, content SHA-256, назву, тип, дату і статус `ready` або `archived`;
- повторна реєстрація тієї самої редакції відхиляється;
- підміна index/object, невідомі поля, orphan-файли та невідповідність source/hash виявляються fail-closed;
- старі PaperDocuments автоматично не переносяться;
- статус «підписано», скан, оригінал чи digital signature не виводяться автоматично.

Це **core без користувацького інтерфейсу**: у r2 ще немає кнопки перенесення prepared-документа в DocumentVault та окремого списку сховища.

## Перевірки

- Final product PR head: `633922f32f4594fc0b6b4db9b8ed181fc4306447`.
- Exact product/release source: `21eb1f668fbd6e915321afe40e2c78d105cdd48b`.
- Exact-main START/source `43832998489` — SUCCESS, **1379/1379**.
- Windows `43832998423` — SUCCESS.
- Windows 7 `43832998510` — SUCCESS.
- macOS Intel + ARM `43832998365` — SUCCESS.
- Windows/Win7 Defender malware gates + post-scan integrity — PASS.
- Publisher `43834523785` — SUCCESS; release target exactly product SHA above, 6 assets.
- Stable/Latest через GitHub API: `v10.18-r3`.

## Що ще не зроблено

- UI-міст із конкретної prepared DOCX-редакції у DocumentVault.
- Окремий read-only список/картка записів DocumentVault.
- Auto-migration чинних PaperDocuments.
- Опціональні скани/оригінали та підписні докази.
- Digital signature і будь-який автоматичний статус «підписано».

## Одна наступна дія

**Наступна дозволена кодова ревізія: 10.20-r3.** Додати окремим UI-модулем явну дію «Зберегти у сховищі документів» для вибраної prepared DOCX-редакції та read-only перелік/картку DocumentVault із title, kind, date, status, revision, source provenance і SHA-256. Не роздувати `main.py`; не додавати auto-migration, scans/originals, digital signature чи автоматичний статус «підписано».

Перед кодом: START_HERE → HANDOFF_CURRENT → private profile → live GitHub → READ/VERIFY/RECONCILE.

Незмінні правила: TemplateLibrary read-only; власні шаблони — CompanyTemplates; Stable/Latest змінюється тільки за прямою командою власника; executable не запускати для перевірки безпеки.
