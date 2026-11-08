# HANDOFF_CURRENT — Taxo

**Оновлено:** 08.11.2026 — після reconciliation паралельної роботи, exact-product перевірок і Google Drive recovery-copy 10.13-r4.

## База
- **Stable / Latest:** [v10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10) — promoted 07.11.2026 з exact product source `6d0f32bc45323d4085bb165b2ec050dae7b378ee`; 8 assets; GitHub Latest.
- **Історичний prerelease:** [v10.11-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r10), exact source `b239bb0dda6a49878f5f06a0edd791710b62df9b`; **архівний, не активна лінія розробки**. Актуальна stable — 10.12-r10; активний код — 10.13-r4.
- **Поточний integrated product candidate:** **10.13-r4**, PR #244, product commit `67b4670fdb29a46d03f9d6462ae2bd19603a2a5c`.
- **CI integration checkpoint:** PR #220 merged → `894fdbb235b2b91c2bb334b8fadfb99566671fc9`; post-merge docs-only smoke PR #222 merged → `bc32daa1b63c20aa4398fa35262d32456b62088c`. Подальший docs-only recovery checkpoint може змінити repository HEAD без зміни продуктової ревізії.
- 10.12-r1…r9 лишаються integrated-only; **10.12-r10 опубліковано як stable/latest**; 10.13-r1/r2/r3/r4 лишаються integrated-only.
- **Попередня Google Drive recovery-copy — 10.13-r2:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r2_2026-11-07_START.zip`, 1 624 847 байт; Drive file `1f5z-jgnDwTEFSSexxoKA14G5mykUW1GV`; START #2321 artifact SHA256 `b8fccfebbb906ed86854ba47a21f77d6884de9232594e16238bdaff0245223f0`.
- **Попередня Google Drive recovery-copy — 10.13-r3:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r3_2026-11-07_START.zip`, 1 636 456 байт; Drive file `1F8R4-qUukZQr86iaBp2PWSuvGow43Gnn`.
- **Google Drive recovery-copy 10.13-r4:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r4_2026-11-07_START.zip`, 1 648 645 байт; Drive file `1_861lkkVbBzhxiBlDbhKexG2jLcE6WAN`; exact START artifact #13591576959 SHA256 `6fd45b64748df00506dcae1420d48db5959f847f1e884d3040b0f0eb6eea4555`.
- **Наступна кодова ревізія:** **10.13-r5**.
- Stable не змінювати без окремого рішення власника. Поточне рішення власника 07.11.2026 — stable = 10.12-r10.

## 10.13-r4 — наказ про закріплення з бази водіїв і транспорту

PR #244 merged → exact product commit `67b4670fdb29a46d03f9d6462ae2bd19603a2a5c`.

- Під час створення наказу про закріплення можна одразу вибрати **активний транспортний засіб** із реєстру ТЗ і **водія з фактичної бази водіїв**.
- Список водіїв не є загальним списком працівників: використовуються роль «Водій» та зв'язок з таблицею `drivers`; завершені/неактивні водії не пропонуються для нового закріплення.
- Перша пара **ТЗ + водій** створюється разом із чернеткою наказу; початок дії за замовчуванням — дата наказу.
- Якщо вибрано лише ТЗ або лише водія, створення блокується.
- Старий сценарій збережено: обидва поля можна лишити порожніми й створити чернетку, після чого додавати рядки у вкладці «Закріплення водіїв».
- При редагуванні історичної чернетки старі ТЗ/водії лишаються доступними, щоб не втрачати історію.
- DB schema, plan/fact, immutability чинних/підписаних наказів, stable/release/security не змінювались.
- Exact-product після merge: Windows #1305 — **953 tests / OK**; Win7 #291 — SUCCESS; macOS #1216 ARM64/Intel — SUCCESS; START #2325 — SUCCESS.
- Exact-source recovery-copy r4 на Google Drive підтверджена; файл і SHA256 наведені вище.
- Stable лишається **v10.12-r10**. r4 не опублікований.
- Наступна code revision — **10.13-r5**; перед новою кодовою роботою потрібне ручне приймання r4 власником.

## 10.13-r3 — окрема вкладка «Інструктажі та журнали»

- PR #239 merged → exact product commit `a7b13a920302fb1dbfb441bf6ba097953cc3f71b`. Stable не змінювалась.
- Створено доступний із «Експлуатації» новий розділ: БДР/охорона праці, квартал для орієнтації, дата, вид, тема, підстава позапланового, вибір активних працівників.
- Дія «Зберегти підготовчий список…» створює лише CSV для інженера з явним написом «НЕ Є ЖУРНАЛОМ». Не пише в робочу БД, не фіксує проведення, не моделює підпис, не перезаписує існуючий файл.
- PR-head gates: Windows #42414118500 — SUCCESS, Win7 #42414118532 — SUCCESS, macOS #42414118493 Intel/ARM — SUCCESS; нові live UI та ізольовані CSV-тести пройшли.
- **Exact-product post-merge:** Windows #42414412641 — SUCCESS, Win7 #42414412482 — SUCCESS, macOS #42414412631 Intel/ARM — SUCCESS, START #42414412635 — SUCCESS. ZIP містить 584 файли, версія й запуск перевірені; sha256 вище.
- **Резерв r3:** точна START копія на Drive підтверджена. Залишилось ручне приймання; далі — сховище затверджених програм і справжній квартальний план.
- Issue #237 і `docs/planning/INSTRUCTION_JOURNALS_FOUNDATION_2026-11-07.md` — єдина планова тема. Історична 10.11 не розробляється.

## Stable promotion 10.12-r10 — 07.11.2026

- Власник після ручного r10 acceptance дав пряму команду оновити stable до лінії 10.12.
- Оскільки 10.12-r10 був integrated-only, а main уже містив 10.13-r1, додано guarded exact-checkpoint promoter замість відкату main.
- PR #229 додав stable target і exact source; перший publisher run #42408835080 зупинився **до створення tag/release** через shell SIGPIPE у verification.
- PR #230 виправив лише pipefail handling без послаблення gate.
- Historical stable publisher #42409237532 — **SUCCESS**.
- Release [v10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10) → exact source `6d0f32bc45323d4085bb165b2ec050dae7b378ee`, prerelease=false, draft=false, GitHub Latest, 8 canonical assets.
- Вихідні r10 platform gates: Windows #1269, Win7 #262, macOS #1187 ARM64/Intel, START #2315 — SUCCESS; PR-head r10 Windows — **931 tests / OK**.
- Попередня stable `v10.10-r5` лишається rollback. 10.13-r1 не публікувався і не став stable.

## 10.13-r2 — зрозуміліша щоденна Експлуатація / СТОІР / накази

PR #232 merged → product commit `c6a2ad85b37019ab96fa32a0e597b625aea4815f`.

- Повторний UX-аудит підтвердив: r1 уже мав функціональний workflow, але частина щоденних дій залишалась неочевидною або показувала внутрішні технічні значення.
- «Стан автопарку» отримав явну дію **«Відкрити вибране ТЗ»**; подвійний клік збережено як швидкий шлях.
- У таблицях СТОІР `STO`, `REPAIR`, `waybill_end` та інші source codes замінені на зрозумілі українські підписи; дати/час показуються у звичному форматі.
- На робочому столі є прямий старт **«Оформити новий наказ…»**.
- Дії реєстру наказів переведені з одного довгого рядка у багаторядкову сітку; «Найчастіші дії» — у 2-колонкову сітку.
- Перший PR-head випадково замінив старий вхід **«Каталог типів наказів»** новим. Historical Feature Loss live-gate r7 зупинив CI. Старий маршрут повернуто, новий маршрут лишено поруч. Це підтвердило працездатність циклу «нічого не загубити».
- Бізнес-логіка, DB schema, plan/fact, факти ТО/ремонтів/одометра, незмінність наказів і release/security не змінювались.
- Фінальний PR-head `1b3d846a99dcb2c275562421fb5baabe61504f7e`: Windows #1287 — **941 tests / OK**; Win7 #278 — SUCCESS; macOS #1203 ARM64/Intel — SUCCESS.
- Exact-product post-merge: Windows #1288 — **941 tests / OK**; Win7 #279 — SUCCESS; macOS #1204 ARM64/Intel — SUCCESS; START #2321 — SUCCESS.
- Exact-source recovery-copy на Google Drive підтверджена; файл і SHA256 наведені вище.
- Stable лишається **v10.12-r10**. 10.13-r2 не публікувався.
- Наступна code revision — **10.13-r3**; перед новими змінами потрібне ручне приймання r2 власником.

## 10.13-r1 — «Експлуатація» / СТОІР як цілісний робочий сценарій

PR #227 merged → product commit `4ed9530b57a4e67fdca49c81da43602df074ebb0`.

- «Документи» в «Експлуатації» тепер працює як робочий стіл і має прямий вхід у **СТОІР — стан автопарку**; старі маршрути не видалені.
- СТОІР починається зі стану автопарку; подвійний клік по ТЗ веде до його огляду.
- Додано UI налаштування періодичності ТО конкретного ТЗ без переписування історії.
- Факт ТО/ремонту тепер приймає виконавця, документ/наряд і примітку.
- Заявка проходить зрозумілий цикл **нова → у роботу → закрити з результатом**; закриття без результату блокується.
- ОТК має прямий перехід до документів ТЗ; технічні статуси/пріоритети показуються людською українською.
- Накази починаються з **«Що потрібно оформити?»**; «Затвердити» замінено на **«Ввести в дію в Taxo»** з явним поясненням, що це не юридичне підписання.
- Чинні/підписані/скасовані накази захищені від звичайного редагування; є **«Історія…»**, незворотна позначка підписаного паперового оригіналу та скасування лише чернетки.
- Типові тексти наказів, plan/fact, робоча DB schema, історичні записи та release/build workflows не змінювались.
- PR-head: Windows #1274 — **936 tests / OK**; Win7 #265 — SUCCESS; macOS #1190 ARM64/Intel — SUCCESS.
- Exact-product post-merge: Windows #1275, Win7 #266, macOS #1191 ARM64/Intel, START #2316 — **SUCCESS**.
- Exact-source recovery-copy на Google Drive підтверджена; файл і SHA256 наведені вище.
- Ручне приймання власником цього UX-зрізу ще потрібне; наступний кодовий номер — **10.13-r2**.

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

## 10.12-r10 — «План → факт» reachability та інваріант даних

PR #224 merged → product commit `6d0f32bc45323d4085bb165b2ec050dae7b378ee`.

- Додано живу перевірку реального маршруту **«План → факт»** у щоденному табелі.
- Тест відкриває справжнє вікно табеля, переходить на щоденну вкладку, вибирає дві дати й натискає справжню кнопку.
- Вся зміна даних відбувається лише у тимчасовій ізольованій SQLite-БД; робоче сховище користувача не відкривається.
- Перевірено реальну дію: день без факту отримує план як факт.
- Одночасно перевірено інваріант: уже наявний підтверджений факт не змінюється; планові поля й примітки не переписуються побічно.
- Продуктову реалізацію `copy_missing_plan_to_fact` не переписували: r10 додає live regression gate навколо захисту, виправленого ще у 10.11-r3.
- Function registry тепер має `runtime_smoke=True` для **всіх 23 критичних маршрутів**.
- PR-head `8da128be181ea7b01a7d4927c4c5236a3966109a`: Windows #1268 — **931 tests / OK**; Win7 #261 — SUCCESS; macOS #1186 ARM64/Intel — SUCCESS.
- Post-merge exact product commit: Windows #1269 — SUCCESS; Win7 #262 — SUCCESS; macOS #1187 ARM64/Intel — SUCCESS; START #2315 — SUCCESS.
- Google Drive exact-source recovery-copy: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.12-r10_2026-11-07_START.zip`, 1 598 952 байти; source artifact SHA256 `395834c0c2247129d280fb08bff5cb7c27ac118cfc1d6ceae67092d413f0afa3`.
- Stable лишається `v10.10-r5`; останній published candidate — `v10.11-r10`; 10.12-r1…r10 integrated-only.

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

## CI maintenance — завершено 07.11.2026

- Старі draft PR #142 і #152 прочитані лише як історична довідка; **не зливались** і після перевірки replacement-рішення закриті як superseded.
- PR #220 перебудовано чисто від актуального `main` без зміни `VERSION.txt`, продуктової логіки чи `publish-current.yml`.
- Superseded PR runs тепер скасовуються для Windows / Win7 / macOS. Live-доказ: старі Windows #1262 і Win7 #258 завершились `cancelled`; macOS jobs попереднього head також були перервані після нового commit.
- Фінальний PR #220 head `0db456281f84f22d62e55b599b66abc35edc1be2`: Windows #1263 — SUCCESS; Win7 #259 — SUCCESS; macOS #1184 ARM64/Intel — SUCCESS.
- Required branch-protection check лишився **`build-windows`** і далі запускається на кожен PR.
- Docs-only smoke PR #221: тільки Windows #1264; documentation check — SUCCESS; Python/regression/START/PyInstaller/installer/artifacts — skipped; Win7/macOS не стартували.
- Workflow-sensitive merge #220: post-merge Windows #1265, Win7 #260, macOS #1185, START #2314 — усі SUCCESS; publisher не стартував.
- Post-merge docs-only PR #222: тільки lightweight Windows #1266 — SUCCESS. Після merge у `main` commit `bc32daa1b63c20aa4398fa35262d32456b62088c` мав **0 GitHub Actions runs**: важкі platform/START/publisher workflow не запускались.
- `VERSION.txt` лишився **10.12-r9**. `publish-current.yml` не змінено; exact-source release gates не послаблено.
- Деталі: `docs/maintenance/CI_MAINTENANCE_2026-11-07.md`.

## Наступна безпечна дія

Надати власнику готовий START 10.13-r3 для ручного приймання нового розділу. Після його перевірки — обрати один вузький наступний етап 10.13-r4: довідник затверджених програм і контрольний квартальний план, без юридичної імітації паперових підписів. Stable лишається 10.12-r10.

## Recovery

`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md` → `WORKLOG.md` / Issue #61 / #164 / #175.
