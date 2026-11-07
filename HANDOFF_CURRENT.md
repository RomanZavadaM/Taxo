# HANDOFF_CURRENT — Taxo

**Оновлено:** 07.11.2026 — після інтеграції Feature Loss hardening 10.12-r9.

## База
- **Stable / Latest:** [v10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) — без змін.
- **Останній офіційно виданий candidate:** [v10.11-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r10), prerelease; exact source `b239bb0dda6a49878f5f06a0edd791710b62df9b`; 8 assets.
- **Поточний main / integrated candidate:** **10.12-r9**, commit `a445f01d1d1c00408ee3f064088de4ddc1637c86`.
- 10.12-r1…r9 **ще не публікувались як GitHub prerelease**.
- **Наступна кодова ревізія:** **10.12-r10**.
- Stable не змінювати без окремого рішення власника.

## Чому почалась лінія 10.12

Власник виявив, що прийнятий раніше **«Простий місячний графік…»** з вибором працівників, PDF/XLSX фактично зник з `Працівники → Планування`, хоча сам код і бізнес-тести залишались.

Ретроспективний Feature Loss Audit підтвердив системну проблему: у Taxo історично були випадки, коли функція залишалась реалізованою, але її UI-entry або control ставав невидимим через composition feature layers / layout.

Документи:
- `docs/maintenance/FEATURE_LOSS_AUDIT_2026-11-06.md`
- `docs/maintenance/FUNCTION_REGISTRY_DRAFT.md`
- UX tracking: Issue #164.

## 10.12-r1 — повернення вибіркового графіка

PR #202 merged → `893ce87ed7d333e4867982c879a12c294763e7df`.

- `Працівники → Планування → Простий місячний графік…` знову має постійний штатний вхід.
- Мультивибір працівників, PDF та Excel не були видалені; проблема була у крихкому runtime-injector.
- Legacy injector лишений лише як non-duplicating fallback.
- Windows / Win7 / macOS ARM64/Intel PR gate — SUCCESS.

## 10.12-r2 — function reachability gate

PR #204 merged → `33fa572b7e621c8adeea05165a017c29434bf0c9`.

- Додано executable registry: `src/taxo/function_registry.py`.
- Додано реальні Tk/Xvfb reachability smoke: mapped route + callback/binding для найбільш крихких входів.
- Gate покриває Personnel Data Center, simple-month fallback, military transport, STOIR.
- Фінальний PR head `da7ca95566372e612f27be65705e590e9cbd9b74`.
- Windows #42352276336 — SUCCESS.
- Windows 7 #42352276288 — SUCCESS, full CPython 3.8 regression.
- macOS ARM64/Intel #42352276292 — SUCCESS.
- Бізнес-логіка й DB schema не змінювались.

## 10.12-r3 — Personnel Data Center fail-safe

PR #205 merged → `28a84c9b44c7ac526acb09c6258e227d760cc762`.

Проблема: старий installer спочатку ховав окремі registry/Diia/document buttons, а лише потім намагався знайти `Новий працівник` і створити replacement `Дані / Дія / документи…`. При майбутньому UI-refactor це могло сховати цілий блок функцій.

Виправлено:
- `Дані / Дія / документи…` тепер постійна штатна action у Personnel UI;
- compatibility layer спочатку гарантує replacement route;
- legacy entries ховаються тільки після успішного replacement;
- якщо replacement/anchor відсутній — legacy entries залишаються доступними;
- runtime tests покривають permanent / fallback / missing-anchor сценарії.
- PR-head Windows #42352755797 — SUCCESS, **903 tests / OK**;
- Win7 #42352755837 — SUCCESS, full CPython 3.8;
- macOS ARM64/Intel #42352755821 — SUCCESS.


## 10.12-r4 — захист вкладених маршрутів

PR #207 merged → current main `816e386647575763074e9106b6f75ef431fadcb9`.

- Додано живу перевірку, що пункт **«Експлуатація»** реально видимий і відкривається.
- Додано живу перевірку вкладеної **«Відомість (додаток 1)»** у військово-транспортному обліку.
- Реєстр функцій тепер вимагає runtime-smoke і для цієї вкладеної відомості.
- PR-head: Windows #42354870979 — SUCCESS, **907 tests / OK**; Win7 #42354871043 — SUCCESS, full CPython 3.8; macOS ARM64/Intel #42354870938 — SUCCESS.
- Бізнес-логіка, БД і формування документів не змінювались.

## 10.12-r5 — історично ламкі layout-контроли

PR #209 merged → `444645d558f5147393d3f476fd618771ed3799e4`.

- Жива перевірка гарантує видимість прапорця перепланування персоналу на мінімальному підтримуваному розмірі вікна.
- У вузькому вікні перевіряються всі 9 дій шляхівок: жодна не зникає, усі переносяться на кілька рядків і натискаються.
- Windows #42355574911, Win7 #42355574884, macOS #42355574889 — SUCCESS.
- Бізнес-логіка, БД, PDF і нумерація документів не змінювались.

## 10.12-r6 — дії всередині центру даних працівників

PR #210 merged → current main `e1bdcd5b827b2da78093323ee7fcdc48e5ac5eb0`.

- Жива перевірка охоплює всі 8 основних дій усередині «Дані / Дія / документи…».
- Перевіряється, що кожна кнопка реально видима і відкриває правильну робочу дію.
- Windows #42356061719, Win7 #42356061533, macOS #42356061548 — SUCCESS.
- Бізнес-логіка, правила документів/Дії/військового обліку та БД не змінювались.

## 10.12-r7 — Центр документів

PR #214 merged → current main `232d7b54fd8aea61883acece2063741ea477bb0c`.

- Додано живу перевірку Центру документів усередині «Експлуатації».
- Перевіряються 4 основні дії: шляхові листи, контроль документів ТЗ, відомість ТЦК, реєстр працівників.
- Перевіряються 4 внутрішні переходи: накази, закріплення водіїв, відповідальні, каталог наказів.
- Повторне відкриття не створює дубль вкладки «Документи».
- Windows #42359978858 — SUCCESS, **917 tests / OK**.
- Win7 #42359978957 — SUCCESS.
- macOS ARM64/Intel #42359978856 — SUCCESS.
- Бізнес-логіка, БД і документи не змінювались.

## 10.12-r8 — головна навігація

PR #216 merged → current main `30d53a2d62b7622e5ed6601aa951676aaf9697c7`.

- Додано живу перевірку пунктів **«Тахограф»**, **«Звіти»**, **«Налаштування»**.
- Реєстр функцій тепер вимагає runtime-smoke для всіх трьох маршрутів.
- Під час першого варіанта тесту виявлено зависання Tk event-loop; тест перероблено на контрольоване компонування без зміни продуктового коду.
- Наступний варіант тесту виявив, що без одноразового завершення layout кнопка ще не mapped; це виправлено лише в test harness.
- Фінальний head `6b01f4068dd83a58f98b801186f363bce8601b20`: Windows #42362821426 — **920 tests / OK**; Win7 #42362821600 — SUCCESS; macOS ARM64/Intel #42362821506 — SUCCESS.
- Бізнес-логіка, БД, тахографічні розрахунки, формування звітів і налаштування не змінювались.
- Старий PR #211 закрито як superseded; його зміст перенесено чисто в r8 від актуального main.

## 10.12-r9 — вибір водіїв для звіту

PR #218 merged → current main `a445f01d1d1c00408ee3f064088de4ddc1637c86`.

- Додано живу перевірку маршруту **«Водії для звіту…»** у місячному графіку змінності.
- Перевіряється, що кнопка видима, відкриває **«Вибір водіїв для звіту»**, список водіїв формується, а дія **«Застосувати»** доступна.
- Реєстр функцій тепер вимагає runtime-smoke для `drivers.report_selection`.
- Перший test-harness шукав popup не на тому рівні дерева Tk і впав на macOS ARM64; виправлено лише тест, продуктова логіка не змінювалась.
- Фінальний PR head `08a2ef6d1c80d94c5fa6b124d1ef7986272a1196`: Windows #42394538014 — **923 tests / OK**; Win7 #42394537977 — SUCCESS; macOS ARM64/Intel #42394537997 — SUCCESS.
- План/факт, БД, планування водіїв та формування PDF/Excel не змінювались.
- Під час r9 фактично підтверджено CI-втрати: runs старого PR head не скасувались після нового commit і паралельно зайняли runners.

## Підтверджені висновки Feature Loss Audit

**Підтверджені втрати/регресії:**
- simple-month schedule UI-entry — знайдено й виправлено r1;
- історично vehicle core actions зникали через pack/grid conflict — виправлено ще у 10.8-r1/r2.

**Високий ризик / наступні кандидати на runtime gate:**
- STOIR navigation, military-transport route і nested `Відомість (додаток 1)` — уже покриті runtime gate у r2/r4;
- bulk personnel replanning checkbox, який уже історично перекривався layout;
- дев'ять waybill actions, які вже історично могли виходити за межі вузького вікна;
- інші dynamic navigation/feature-layer entries.

Прямого масового видалення функціонального коду після v10.10-r5 аудит не показав. Основний клас ризику — **live code becomes unreachable in composed UI**.

## Наступна безпечна дія

**Не починати 10.12-r10 у цій довгій сесії.**

Наступний окремий етап — **CI optimization / process-only, без зміни продуктової ревізії**:
1. почати чисто від актуального `main`;
2. використати PR #142 і #152 лише як історичну довідку, **не зливати їх як є**;
3. додати скасування superseded PR runs для Windows / Win7 / macOS;
4. консервативно не запускати важкі platform/START збірки для звичайних docs-only змін;
5. повні перевірки зберегти для коду, workflow, dependencies, packaging, security та release-sensitive змін;
6. окремо перевірити, що post-merge docs-only push не марнує runners, але release checkpoint не послаблений;
7. після нового актуального CI PR старі #142/#152 закрити як superseded.

Після завершення CI maintenance наступна **кодова** ревізія — **10.12-r10**: один вузький Feature Loss slice для **«План → факт»**. Не починати великий UX cleanup.

## Recovery

`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md` → `WORKLOG.md` / Issue #61 / #164 / #175.
