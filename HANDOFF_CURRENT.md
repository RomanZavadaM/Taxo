# HANDOFF_CURRENT — Taxo

**Live GitHub state — 18.11.2026.**

- **10.22-r4 повністю завершена:** product PR #531 merged, exact immutable source `b01437828551fe309c2dfcba81572a9a9d51e628`, final head `0f537c7ffe57c0628de4619eb8f2c19567beb02f`.
- Exact-source START #44320801103 **1527/1527**; Windows #44320801102, Win7 #44320801191, macOS Intel/ARM #44320801139 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #532 merged `7d443e25f8ec754f71a3749c6e46163d8aca8728`; publisher #44322860950 SUCCESS.
- [v10.22-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r4): Test Portable prerelease, 6 assets, exact source `b01437828551fe309c2dfcba81572a9a9d51e628`.
- **Stable/Latest remains [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2)**.

## Що зроблено у r4

У загальному каталозі **«Документи»** команда **«Відкрити вибране»** для запису DocumentVault тепер реально відкриває документ. Перед переглядом Taxo повторно перевіряє індекс, розмір і SHA-256 незмінного об'єкта. Сам файл у `Data/DocumentVault` зовнішній програмі не передається: створюється окрема тимчасова DOCX-копія тільки для читання. Пошкоджений або підмінений об'єкт не відкривається.

БД, формат DocumentVault, скани, backup/restore, бізнес-статуси, КЕП/e-signature, накази та пари водій↔ТЗ не змінювалися.

## Пари водій↔ТЗ

Власник 18.11.2026 вручну перевірив 10.21-r9 і повідомив, що проблем не знайшов. Механізм пар прийнятий; якщо з'явиться новий дефект — зафіксувати його окремо.

## Що далі

**10.22-r5 ще не починалася.** Спершу звірити START_HERE.md → live main/HANDOFF → відкриті PR/гілки/CI. Далі взяти один вузький незалежний крок з Issue #289 або новий дефект ручного тестування. Stable не змінювати без прямої команди власника.
