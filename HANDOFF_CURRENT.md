# HANDOFF_CURRENT — Taxo

**Live GitHub state — 18.11.2026.**

- **10.22-r7 повністю завершена, інтегрована й опублікована:** product PR #540 merged; final work head `b7daf5f3b69bddf9240805c7608118145fc6c2e9`; immutable exact product source `544da915100744f4fcf1e094f374d13c76c36c80`.
- Exact-source START #44404136276 **1540/1540**; Windows #44404136133, Win7 #44404136553, macOS Intel/ARM #44404136897 — SUCCESS; Windows/Win7 Defender/integrity PASS.
- Release-trigger PR #541 merged `7494e415a005a3c30c453069fabce7deefe2c457`; publisher #44406105602 SUCCESS.
- [v10.22-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r7): Test Portable prerelease, 6 assets; tag points exactly to the product source above.
- **Stable/Latest remains [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2)**.

## Що зроблено у r7

У загальному каталозі **«Документи»** заголовок **«Категорія»** тепер перемикає сортування А→Я / Я→А. Сортування застосовується до всього вже відфільтрованого списку до розбиття на сторінки. Записи **«Не визначено»** залишаються внизу в обох напрямках; «Скинути фільтри» повертає стандартний порядок за датою.

DocumentVault, файли й скани, паперовий підпис, backup/restore, схема БД, накази та пари водій↔ТЗ не змінювалися.

## Що не спрацювало і що виправлено

Кодова r7 і exact-source CI пройшли повністю. Уже в release-trigger PR #541 перший required Win7 check впав на кроці оновлення сигнатур Microsoft Defender через мережевий timeout `0x80072ee2`, не через Taxo і не через знайдену загрозу. Код не змінювали; чистий повторний запуск завершився SUCCESS, включно з Defender та integrity.

## Що далі

**10.22-r8 ще не починалася.** Спочатку `START_HERE.md` і fresh-звірка live GitHub з цим HANDOFF, включно з гілками без PR та CI. Далі один наступний вузький крок з Issue #289 або новий дефект ручного тестування. Stable не змінювати без прямої команди власника.
