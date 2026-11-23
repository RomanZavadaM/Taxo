# Taxo 10.24-r8 — контроль повторного відкриття учасників наказу

**Опублікований Current Test. Stable/Latest залишається 10.24-r3.**

10.24-r8 — вузька control-only ревізія після reconciliation #553/#556/#562. Бізнес-правила наказів, схема БД і формати документів не змінюються. Ревізія доводить окремий залишок наскрізного сценарію **«Учасники / ТЗ»**: дані та контекст наказу повинні переживати повне закриття й повторне створення UI.

## Що захищено

- fresh UI reopen читає наказ повторно з робочої SQLite-БД, а не зі старого віджета;
- після reopen видно той самий номер, дату, тему і стан наказу;
- роль, примітка та рядок учасника не губляться;
- перехід наказу **«Чернетка» → «Діє в Taxo»** змінює стан наказу, але не переписує учасника;
- після refresh того самого наказу зберігається вибраний рядок учасника;
- frozen `snapshot_json` та `sequence_no` лишаються незмінними;
- r7-контроль add/edit/remove, live preview sync, DOCX/PDF та backup/restore не послаблюється і не дублюється новою бізнес-логікою.

## Prep verification

Prep PR #638 final head `f95aac5ef1344b5c851411dd2bc6d1ea1f9ddf50`:
- START #45231841871 — SUCCESS;
- Windows #45231841838 — SUCCESS;
- Windows 7 #45231842010 — SUCCESS;
- macOS Intel/ARM #45231841929 — SUCCESS;
- Windows/Win7 Defender та post-scan integrity — SUCCESS.

Prep merged у main як `06189dc472d6ca8c3063defb9c0b20c20626fda4`.

Перший prep head `6985c047aaa3a8a567fbfca91b9d24ed960f9e37` виявив платформну помилку самого тесту: на macOS ARM синтетична `<<TreeviewSelect>>` подія не доставлялася прихованому тестовому Treeview. Тест виправлено на реальний public refresh-callback, продуктову логіку не змінювали; повторний all-platform прогін пройшов.

## Публікація

- Candidate PR #639 final head `f8ef99d7cfe07e2d8064878e41da5d09657930fe`: START #45234694758, Windows #45234694250, Win7 #45234694546, macOS Intel/ARM #45234694225 — SUCCESS; Defender/integrity PASS.
- Exact issued source: `d24b1bc96115de52d6088813992aca3b410fe243`.
- Exact-source checks: START #45235704945, Windows #45235704686, Win7 #45235704998, macOS Intel/ARM #45235705102 — SUCCESS; Defender/integrity PASS.
- Guarded release-trigger PR #640: START #45236768940, Windows #45236768934, Win7 #45236769035, macOS Intel/ARM #45236768791 — SUCCESS; Defender/integrity PASS.
- Publisher #45237831016 — SUCCESS.
- GitHub Release [v10.24-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r8): exact target `d24b1bc96115de52d6088813992aca3b410fe243`, 8 canonical assets, prerelease=true, draft=false.
- GitHub Latest / Stable лишається [v10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3).

## Межі r8

- не змінюються бізнес-правила наказів;
- не змінюється схема БД;
- не змінюються нумерація, паперовий підпис, DOCX/PDF/JPG або correspondence;
- #562 лишається реалізованою, але відкритою до ручного UI-приймання;
- #553/#556 не закриваються автоматично без ручного приймання власником;
- automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не входять у r8.

Stable/Latest змінюється тільки за прямим рішенням власника.
