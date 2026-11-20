# HANDOFF_CURRENT — Taxo

**20.11.2026 — відновлення після обриву, Stable promotion PENDING.**

Власник уточнив: саме **10.23-r1** зробити Stable/Latest; **10.23-r2 залишити тестовою**. Не відкотити код main, не пересувати теги.

- Поточний код main до службового PR: `559a816643499dba5234cc72f2fef8720eb42163` (10.23-r2). Усі 4 перевірки main SUCCESS.
- [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1): точний тег `84184bbbf6c26b681c04feaebee19910269bd25c`, 6 файлів до promotion. START #44600058957, Windows #44600058914, Win7 #44600058737, macOS #44600058736 — SUCCESS; Defender/integrity PASS. Windows/Win7 Setup зібрані, артефакти не прострочені.
- [10.23-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r2): 8 файлів, prerelease; точний source ac0bd0d5078ab4bd4c76abcaa0ca9b72e776e03e, CI SUCCESS, publisher #44619140603 SUCCESS. Редагування ролі/примітки учасника наказу та 33-й UI-маршрут.
- Фактична Stable до завершення promotion — 10.21-r2. Не оголошувати r1 stable до перевірки GitHub Releases/latest, exact tag, 8 assets, SHA256.
- Draft #543/#395 не чіпати. #553/#556 залишаються відкритими; ручне приймання та повне покриття не завершені.

**Наступна дія:** перевірити результат historical stable promotion PR/Actions, після SUCCESS синхронізувати README, PROJECT_STATE, HANDOFF, WORKLOG, RELEASE_INDEX, PRODUCT_STATUS та Issue #61. Не починати 10.23-r3 до документального закриття. Якщо promotion не пройде — зберегти 10.21-r2 як фактичну Stable і виправити причину без обходу перевірок.
