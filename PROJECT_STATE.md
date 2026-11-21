# PROJECT_STATE — Taxo

**Підтверджено GitHub 20.11.2026 після stable promotion 10.23-r4.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact product source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, GitHub Latest, prerelease=false.

**Попередня Stable:** [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1). Новішого тестового випуску немає. r3 був інтегрований у main, але окремий v10.23-r3 свідомо не публікувався.

## Stable 10.23-r4

- Каталог документів: пошук, фільтри, сортування, дерево «За видами / За датами / Мої папки», вкладені власні папки, сховище, скани та паперовий підпис.
- Бланки: регульована вертикальна робоча область між формою та історією.
- Каталог: регульована ширина дерева та компактні дії для меншої ширини.
- Накази: явні пари водій–ТЗ, редагування пар, ролі/примітки учасника, накопичення вибору при пошуку, тема активного наказу, перехід до закріплень.
- Перегляд наказу: адаптивні DOCX/PDF/JPG дії, стабільна нижня сітка, доступність при 760×560.
- Захист функцій: **37 strict runtime routes** з mapped / onscreen / usable / activation.

## Перевірка

Exact stable source `a919ced6bc8665ced70ebb4d897808e4e2618667`:
- START #44803423646 — SUCCESS;
- Windows #44803423874 — SUCCESS, Defender/integrity PASS;
- Windows 7 #44803423649 — SUCCESS, Defender/integrity PASS;
- macOS Intel/ARM #44803423740 — SUCCESS;
- Test publisher #44804999191 — SUCCESS;
- owner manual acceptance 20.11.2026;
- Stable promotion #44811800328 — SUCCESS.

Release v10.23-r4 перевірено: tag target = exact source, 8 assets, draft=false, prerelease=false, `releases/latest` = v10.23-r4.

## Активна розробка

**10.23-r5 уже в роботі:** PR #576, head `3a084fa47784d9d7765f733a84e9f8951b0d4a03`. Пакет закриває ризик малого viewport «Документи → Каталог»: компактні дерево/таблиця, повноширинна панель дій власних папок, адаптивні фільтри та strict live route `documents.catalog_small_viewport`. Якщо буде merged, реєстр зросте з 37 до 38 strict live routes.

Exact-head CI r5 завершено: START, Windows, Win7, macOS Intel/ARM — SUCCESS. PR #576 ще відкрита, не merged і не опублікована. Після інтеграції діє стандартне правило Test prerelease; Stable/Latest лишається 10.23-r4 без окремого рішення власника. #553/#556/#562 лишаються відкритими; draft #543/#395 не змінювати.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
