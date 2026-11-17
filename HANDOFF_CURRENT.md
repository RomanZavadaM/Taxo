# HANDOFF_CURRENT — Taxo

**Live GitHub state — 17.11.2026.**

- **10.21-r7 fully completed:** product PR #509 merged; immutable product source `b3185f5f558d96880cc8c2614529d0fb2d0de660`, final PR head `dcbc81b363c4de737a20bcbf7d9869c0e61a8ef3`.
- Exact-source START #44159339508: **1469/1469**; Windows #44159339500, Win7 #44159340068, macOS Intel/ARM #44159339556 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #510 merged `4f9eafa9729f15b25dd1bf26385e87e3fe1aa520`; publisher #44161402744 SUCCESS.
- [v10.21-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r7): Test prerelease, 6 files (Windows/Win7/macOS Intel/ARM Portable, START, SHA256). Tag points exactly to product source `b3185f5f558d96880cc8c2614529d0fb2d0de660`.
- **Stable/Latest remains [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2)**, 8 files.

## Що зроблено

У вікно «Шляхівки» додано штатну кнопку **«Дата…»**: використовує той самий календар, що й графіки, вибір іншої дати відразу оновлює шляхівки. Закриття без вибору нічого не змінює. Ручне введення/Enter/«Перейти» та День-/Сьогодні/День+ із r6 збережено. Без змін БД, пробігу, видачі шляхівок, backup/restore, security чи залежностей. Ручне приймання власником нової кнопки ще не зафіксовано.

## Критичний дефект, наступна задача

Власник надав два скриншоти: (1) обрані водії/ТЗ у наказах неправильно групуються в пари; (2) **готові пари з «Експлуатації» теж не вдається забрати**. Зафіксовано в [Issue #511](https://github.com/RomanZavadaM/Taxo/issues/511), також у Issue #61. Початковий аналіз показав автоматичне `zip` індексних списків в `operations_orders.build_assignment_pairs`, виклики з `order_editor_assignments_ui.py` і `order_assignments_ui.py`; це гіпотеза для відтворення, а не підтверджена повна причина. Потрібно явно добирати й перевіряти конкретні пари, включно з перенесенням підготовлених пар з «Експлуатації», без тихого перегрупування.

**10.21-r8 ще не починалася.** Наступна дія: відкрити START_HERE.md, звірити main/HANDOFF/open PR/branches without PR, потім працювати над #511 як окремою r8. Не повторювати r7; Stable не змінювати без прямої команди.
