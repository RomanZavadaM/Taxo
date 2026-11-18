# HANDOFF_CURRENT — Taxo

**Live GitHub state — 18.11.2026.**

- **10.22-r5 інтегрована й опублікована:** product PR #534 merged; immutable exact source `576f93acd7d070a6786cfcd3c28af1d5f29d98c0`, final work head `c7f79db2384ec359dc9cd5e62902f58c0a3fcdd9`.
- Exact-source START #44375223718 **1531/1531**; Windows #44375224479, Win7 #44375223666, macOS Intel/ARM #44375223669 SUCCESS; Windows/Win7 Defender/integrity PASS.
- Release-trigger PR #535 merged `ef8f63bdf5771d2a365509d5786bbf9ab6a115e8`; publisher #44376388134 SUCCESS.
- [v10.22-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r5): Test Portable prerelease, 6 assets, tag points exactly to product source above.
- **Stable/Latest remains [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2)**.

## Що зроблено у r5

У загальному каталозі **«Документи»** для запису DocumentVault з'явилась окрема колонка **«Папір / підпис»** та дія **«Паперовий підпис…»**. Користувач явно вказує дату фактичного паперового підписання. Позначку можна скасувати, попередній запис залишається в історії. Скан не позначає документ підписаним автоматично; можна мати підпис без скана і скан без позначки підпису. Це облікова позначка, не електронний підпис та не криптографічне підтвердження.

Журнал `Data/DocumentVault/paper_original_events.json` входить до повного backup/restore. Суворе сховище приймає саме цей валідований файл; інші невідомі файли, пошкоджений журнал і небезпечні посилання не допускаються. Документи, скани, SQLite, бізнес-статуси, накази, пари та Stable не змінювалися.

## Що далі

**10.22-r6 ще не починалася.** Спочатку `START_HERE.md` і звірка live GitHub з цим HANDOFF, включно з гілками без PR та CI. Потім один наступний вузький крок з Issue #289 або нове зауваження власника. Stable не змінювати без прямої команди.
