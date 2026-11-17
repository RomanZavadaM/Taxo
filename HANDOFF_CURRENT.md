# HANDOFF_CURRENT — Taxo

**Live GitHub state — 17.11.2026.**

- **10.21-r8 fully completed:** product PR #513 merged; immutable product source `c9dc9799c22565b56c737216983dd900265c29bd`, final PR head `55056ffccb9eb4c5de523e4d3109f2304cba0620`.
- Exact-source START #44167952855: **1475/1475**; Windows #44167952924, Win7 #44167952849, macOS Intel/ARM #44167952840 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #514 merged `293ddccfcf88433e7a331d79372e4fe1c71239b4`; publisher #44169744409 SUCCESS.
- [v10.21-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r8): Test prerelease, 6 files (Windows/Win7/macOS Intel/ARM Portable, START, SHA256). Tag points exactly to product source `c9dc9799c22565b56c737216983dd900265c29bd`.
- **Stable/Latest remains [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2)**, 8 files.

## Що зроблено

Виправлено першу частину Issue #511: Taxo більше не утворює пари водій↔ТЗ через тихе `zip` двох незалежних списків. У новому наказі користувач явно додає один ТЗ + одного або кількох водіїв у видиму таблицю конкретних пар; для іншого ТЗ операція повторюється. Незафіксований вибір блокує збереження замість мовчазного перегрупування. У наявному наказі масове додавання застосовує те саме безпечне правило. Старі збережені накази не переписуються. Regression-сценарій 12 конкретних пар продовжує перевіряти БД, повторне відкриття, DOCX/PDF/JPG та backup/restore. Ручне приймання r8 власником ще не зафіксовано.

## Відкрита частина Issue #511, наступна задача

**Повторне використання вже підготовлених пар з «Експлуатації» у наказі r8 навмисно не позначене виправленим.** Це окремий шлях даних і наступний вузький крок у Issue #511. Потрібно простежити джерело готових пар, їх вибір/перенесення у наказ, збереження, повторне відкриття та генерацію документа без нового перегрупування.

**10.21-r9 ще не починалася.** Наступна дія: відкрити START_HERE.md, звірити main/HANDOFF/open PR/branches without PR, потім продовжити тільки відкриту частину #511. Не повторювати r8; Stable не змінювати без прямої команди.
