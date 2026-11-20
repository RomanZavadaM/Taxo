# HANDOFF_CURRENT — Taxo

**20.11.2026 — 10.23-r3 інтегровано, реліз свідомо пропущено.**

**Stable/Latest:** [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1), exact source `84184bbbf6c26b681c04feaebee19910269bd25c`, 8 файлів. Stable не змінювати без прямого рішення власника.

**Останній опублікований Test:** [10.23-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r2), exact source `ac0bd0d5078ab4bd4c76abcaa0ca9b72e776e03e`, 8 файлів, prerelease.

**Поточний main:** `12a675a8f16c1f22190281339f62824aaad6a11d`, версія коду **10.23-r3**. Product head `149254b25da390892dcb09b8e2138fb0e88004cc`; PR #567 merged. У r3 одним пакетом: регульована область бланків/історії (#562), регульоване дерево каталогу та компактні дії (#556), накопичуваний вибір учасників/ТЗ, тема активного наказу й перехід до закріплень (#553); 36 strict runtime routes. Exact-head CI: Windows #44777829188, Win7 #44777829261, macOS #44777829358, START #44777829338 — SUCCESS.

Власник 20.11.2026 прямо вирішив **цю збірку пропустити й рухатися далі**. Тому v10.23-r3 не публікувати. Браузерне попередження для Windows-артефакту було окремо перевірене: exact archive і розпакований вміст пройшли Microsoft Defender та ClamAV у run #44789160753; SHA256 збіглися, шкідливу сигнатуру не виявлено. Діагностичний PR #568 закрито без merge.

## Наступна дія

Документаційний резерв Google Drive завершено й перевірено читанням: `05_CURRENT_DOCS_2026-11-20_main-r3` містить START_HERE, PROJECT_RULES, HANDOFF_CURRENT, PROJECT_STATE, TAXO_PROFILE і DEVELOPMENT_LOG; старий великий recovery-файл залишено як історичний архів. Код і збірки на Drive не дублюються.

Почати **10.23-r4** як один змістовний пакет наступних пов'язаних UI-виправлень із #556, не генеруючи окрему збірку на кожну дрібницю. #562, #553 і #556 не закривати без ручного приймання; draft #543/#395 не чіпати.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.
