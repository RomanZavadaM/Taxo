# HANDOFF_CURRENT — Taxo

**Оновлено:** 07.11.2026 — після Feature Loss Audit та інтеграції 10.12-r4.

## База
- **Stable / Latest:** [v10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) — без змін.
- **Останній офіційно виданий candidate:** [v10.11-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r10), prerelease; exact source `b239bb0dda6a49878f5f06a0edd791710b62df9b`; 8 assets.
- **Поточний main / integrated candidate:** **10.12-r4**, commit `816e386647575763074e9106b6f75ef431fadcb9`.
- 10.12-r1/r2/r3/r4 **ще не публікувались як GitHub prerelease**.
- **Наступна кодова ревізія:** **10.12-r5**.
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

Не починати великий UX cleanup.

Наступний номер — **10.12-r5**. Перед кодом:
1. прочитати цей HANDOFF;
2. звірити private Taxo profile;
3. звірити factual GitHub;
4. перечитати `FEATURE_LOSS_AUDIT_2026-11-06.md`, function registry, Issue #164;
5. вибрати один вузький reachability slice.

Пріоритет: перевірити два історично ламкі layout-сценарії: **прапорець перепланування персоналу** та **9 дій шляхівок на вузькому вікні**.

## Recovery

`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md` → `WORKLOG.md` / Issue #61 / #164 / #175.
