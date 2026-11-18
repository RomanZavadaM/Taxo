# HANDOFF_CURRENT — Taxo

**Live GitHub state — 18.11.2026.**

- **10.22-r3 повністю завершена:** product PR #528 merged, exact immutable source `bb3e7fb77e50dc0bd963e1a2a5c164296cfb1722`, final head `96f5ad3567d9314eac4a1a42529900a05f729a2a`.
- Exact-source START #44301305636 **1524/1524**; Windows #44301305635, Win7 #44301305627, macOS Intel/ARM #44301305732 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #529 merged `3dcb3f22c9c1ccd8123dba945f933a210de82f6d`; publisher #44302569986 SUCCESS.
- [v10.22-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r3): Test Portable prerelease, 6 assets, exact source `bb3e7fb77e50dc0bd963e1a2a5c164296cfb1722`.
- **Stable/Latest remains [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2)**.

## Що зроблено у r3

У загальному каталозі **«Документи»** додано кнопку **«Скинути фільтри»**. Одним натисканням вона очищає пошук, джерело, скани, період, тип, категорію, рік, місяць, працівника й ТЗ; повертає першу сторінку і сортування за датою (новіші першими). Відкладений пошук перед скиданням скасовується, щоб не запускати повторне зайве читання. Файли, скани, БД, backup/restore, документи та пари водій↔ТЗ не змінювалися.

## Пари водій↔ТЗ

Власник 18.11.2026 вручну перевірив 10.21-r9 і повідомив, що проблем не знайшов. Механізм пар прийнятий; якщо з'явиться новий дефект — зафіксувати його окремо.

## Що далі

**10.22-r4 ще не починалася.** Спершу звірити START_HERE.md → live main/HANDOFF → відкриті PR/гілки/CI. Далі взяти один вузький незалежний крок з Issue #289 або новий дефект ручного тестування. Stable не змінювати без прямої команди власника.
