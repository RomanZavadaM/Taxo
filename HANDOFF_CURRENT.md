# HANDOFF_CURRENT — Taxo

**Live GitHub state — 18.11.2026.**

- **10.22-r6 повністю завершена, інтегрована й опублікована:** product PR #537 merged; final work head `d764e56596dc30a0b4c717a0a6b0a5b56a7f39c9`; immutable exact product source `28d2b838dae51a8ed009dd4b14fe1a0afa561384`.
- Exact-source START #44386227495 **1535/1535**; Windows #44386227504, Win7 #44386227480, macOS Intel/ARM #44386227490 — SUCCESS; Windows/Win7 Defender/integrity PASS.
- Release-trigger PR #538 merged `c42d3554797ed3bfc133fd1337ab1288b8facc37`; publisher #44388264823 SUCCESS.
- [v10.22-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r6): Test Portable prerelease, 6 assets; tag points exactly to the product source above.
- **Stable/Latest remains [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2)**.

## Що зроблено у r6

У загальному каталозі **«Документи»** накази типу `seasonal_operation` тепер мають окремий напрям **«Сезонні заходи»** замість загального «Експлуатаційні». Категорія визначається тільки зі структурованого типу наказу; слова у темі чи тексті нічого автоматично не змінюють. Кадрова серія як і раніше має пріоритет.

DocumentVault, файли й скани, паперовий підпис, backup/restore, схема БД, накази та пари водій↔ТЗ не змінювалися.

## Що не спрацювало і що виправлено

Перший START у PR #537 знайшов один застарілий regression-набір: у його тестових даних не було сезонного наказу, тому список доступних категорій не міг містити новий напрям. Тестові дані виправлено; повторно **1535/1535** і всі платформи зелені. Логіку каталогу заради тесту не послаблювали.

## Що далі

**10.22-r7 ще не починалася.** Спочатку `START_HERE.md` і fresh-звірка live GitHub з цим HANDOFF, включно з гілками без PR та CI. Далі один наступний вузький крок з Issue #289 або новий дефект ручного тестування. Stable не змінювати без прямої команди власника.
