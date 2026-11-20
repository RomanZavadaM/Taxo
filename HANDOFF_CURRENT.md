# HANDOFF_CURRENT — Taxo

**20.11.2026 — Stable promotion підтверджено.**

**Stable/Latest:** [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1), 20.11.2026, 8 файлів. Exact source `84184bbbf6c26b681c04feaebee19910269bd25c`; START #44600058957, Windows #44600058914, Win7 #44600058737, macOS #44600058736 — SUCCESS; Defender/integrity PASS. Promotion PR #565 merged `e307b1a05a1ee8b6ef277a3a02fa3b72576bac32`; historical publisher #44704009390 SUCCESS. Попередня stable [10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2).

**Поточний тестовий випуск:** [10.23-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r2), 19.11.2026, 8 файлів, prerelease. Exact source `ac0bd0d5078ab4bd4c76abcaa0ca9b72e776e03e`; START #44617883252, Windows #44617883284, Win7 #44617883325, macOS #44617883395 — SUCCESS; publisher #44619140603 SUCCESS після виправлення пошуку exact-source CI (#564). Код main залишається r2. Одноразовий full marker прибрано.

Власник явно вказав: r1 stable, r2 test. Опубліковані теги не пересувалися. README, шість перекладів, посібники й індекс релізів синхронізовано цим документальним checkpoint; після merge звірити GitHub.

## Незавершена робота 10.23-r3

Активна гілка `feature/10.23-r3-documents-workspace` від main `c4dd760e4e01c85cb3528898023abab7d8721718`. Власник затвердив один комплексний пакет документів і наказів, не реліз на кожну кнопку. Реалізація: #562 регульований розділювач форми бланків і таблиці історії; #553 накопичуваний вибір учасників, видимість теми/активного наказу; #556 компактні панелі каталогу й захист від втрати функцій. Проміжні зміни не публікувати, перевірки ще не виконані. Далі — завершити компактне компонування каталогу, додати живий тест розділювача та підготувати єдиний кандидат. Не чіпати stable r1, test r2, draft #543/#395.
