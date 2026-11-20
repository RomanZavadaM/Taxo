# Taxo 10.23-r1 — збереження функцій під контролем

**Stable/Latest — рішення власника 20.11.2026.**

- 32 суворі UI-маршрути (раніше 29); реальні тести каталогу, його дерева й папок.
- Контроль втрати кнопок, вкладок, пунктів меню, 22 дій документів/наказів і 10 команд наказів із їхніми обробниками.
- Тести SQLite: збереження учасників/ТЗ наказу після повторного відкриття, незмінні реквізити, дублікати, історія та вивід у текст наказу.
- Роз'єднано фонове читання каталогу й об'єкти Tk-вікна для сумісності зі старим Python/Windows 7.

**Залишається:** повний контроль всіх функцій Taxo та ручне приймання UX наказів Issue #553. Issue #556 також відкрито.

Exact-source Windows, Windows 7, macOS Intel/ARM, START й security успішно завершені.


**Stable/Latest:** [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1), 20.11.2026, 8 файлів. Exact source `84184bbbf6c26b681c04feaebee19910269bd25c`; START #44600058957, Windows #44600058914, Win7 #44600058737, macOS #44600058736 — SUCCESS; Defender/integrity PASS. Promotion PR #565 merged `e307b1a05a1ee8b6ef277a3a02fa3b72576bac32`; historical publisher #44704009390 SUCCESS. Попередня stable [10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2).

**Поточний тестовий випуск:** [10.23-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r2), 19.11.2026, 8 файлів, prerelease. Exact source `ac0bd0d5078ab4bd4c76abcaa0ca9b72e776e03e`; START #44617883252, Windows #44617883284, Win7 #44617883325, macOS #44617883395 — SUCCESS; publisher #44619140603 SUCCESS після виправлення пошуку exact-source CI (#564). Код main залишається r2. Одноразовий full marker прибрано.
