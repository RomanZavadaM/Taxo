# HANDOFF_CURRENT — Taxo

**Live GitHub state — 18.11.2026.**

- **10.21-r10 повністю завершена:** product PR #519 merged; immutable exact source `3c6a4aedaf18399f3688d02bba3eb0cd30dd74ad`, final PR head `fdedb8bc013d1dcf51174c6a0b834f3780e39158`.
- Exact-source START #44270332491: **1501/1501**; Windows #44270332484, Win7 #44270332389, macOS Intel/ARM #44270332442 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #520 merged `f78e213b496117c400599568ff4133fd1f9b616c`; publisher #44271925495 SUCCESS.
- [v10.21-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r10): Test Portable prerelease, 6 files (Windows/Win7/macOS Intel/ARM Portable, START, SHA256), exact tag source `3c6a4aedaf18399f3688d02bba3eb0cd30dd74ad`.
- **Stable/Latest remains [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2)**.

## Що зроблено у r10

У спільному каталозі «Документи» додано окрему колонку і фільтр **«Категорія»**. Для наказів категорія визначається тільки зі структурованих полів, а не з тексту назви: **Кадрові**, **Експлуатаційні**, **Охорона праці**, **БДР**, **Пожежна безпека**. Старі Word/DocumentVault записи, де такого напряму в даних немає, показуються як **«Не визначено»** — Taxo нічого не вгадує. Фільтр працює разом із пошуком, джерелом, сканами, періодом і типом документа до розбиття на сторінки.

Файли документів, DocumentVault, скани, backup/restore, схема БД та бізнес-статуси не змінювались.

## Окремо про пари водій↔ТЗ

Механізм пар у r10 **не змінювався**. Залишається стан r9: пряме редагування/додавання/прибирання у поточному наказі та перенесення готових пар. Власник перевірить це вручну пізніше; новий дефект, якщо буде, фіксувати окремим кроком.

## Що далі

Лінія 10.21 завершила r10. Наступна дозволена кодова ревізія — **10.22-r1**. Перед нею: START_HERE.md → live main/HANDOFF → open PR/branches. Для каталогу ще відкриті окремі зрізи за роком/місяцем та за працівниками/ТЗ. Обрати один вузький крок; Stable не змінювати без прямої команди власника.
