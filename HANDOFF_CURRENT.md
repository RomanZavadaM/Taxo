# HANDOFF_CURRENT — Taxo

**Live GitHub state — 18.11.2026.**

- **10.22-r2 повністю завершена:** product PR #525 merged; immutable exact source `0aac6e80025cdcc5b54f2f393dbc256f40e42f2d`, final PR head `98ef9e391765de6578fc4a666d13820dba9abb9d`.
- Exact-source START #44291976150: **1520/1520**; Windows #44291976175, Win7 #44291976210, macOS Intel/ARM #44291976217 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #526 merged `c51f2016b12187d87ab4567d5649f5a1747bec40`; publisher #44293509376 SUCCESS.
- [v10.22-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r2): Test Portable prerelease, 6 files (Windows/Win7/macOS Intel/ARM Portable, START, SHA256), exact tag source `0aac6e80025cdcc5b54f2f393dbc256f40e42f2d`.
- **Stable/Latest remains [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2)**.

## Що зроблено у r2

У каталозі **«Документи»** додано точні read-only фільтри **за працівником і транспортним засобом**. Вони беруть дані не з випадкових слів у темі, а зі структурованих зв'язків наказу: для звичайних наказів — з `operations_order_entities` та його frozen snapshot, для наказів про закріплення — з фактичних `vehicle_driver_assignments`.

Однакові ПІБ не змішуються: фільтр працює за stable Taxo ID. У колонці **«Працівники / ТЗ»** і в текстовому пошуку видно структуровані зв'язки. Старі документи без таких зв'язків залишаються у звичайному каталозі та не отримують вигаданих прив'язок. Фільтри комбінуються з роком/місяцем, «Від / До», типом, категорією, джерелом, сканами й пошуком **до розбиття на сторінки**.

Файли документів, DocumentVault, скани, backup/restore, схема БД, бізнес-статуси та сам механізм пар водій↔ТЗ не змінювались.

## Пари водій↔ТЗ

Власник 18.11.2026 вручну перевірив 10.21-r9 і повідомив, що проблем не знайшов. Механізм пар вважається прийнятим; стару проблему закрито. Якщо пізніше з'явиться новий дефект — фіксувати його окремо.

## Що далі

**10.22-r3 ще не починалася.** Перед наступним кроком: START_HERE.md → live main/HANDOFF → open PR/branches. Продовжувати Issue #289 одним вузьким незалежним кроком або взяти новий дефект із ручного тестування, якщо власник його знайде. Stable не змінювати без прямої команди власника.
