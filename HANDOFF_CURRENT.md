# HANDOFF_CURRENT — Taxo

**Оновлено:** 09.11.2026 — інтегровано 10.14-r3, оформлено допоміжне середовище наказів без заборон за статусом.

## 10.14-r3 — накази без програмних заборон — 09.11.2026

- **Product integrated:** PR #266; `main` product SHA `eb4a45ffa6336ff25342816e615d720b3f33b861`. Stable/Latest — **v10.12-r10**, без змін; наступна кодова ревізія — **10.14-r4**.
- **Рішення власника:** Taxo — допоміжна програма для документів. Справжній контроль офіційних наказів — за паперовими примірниками. Статус чи позначка паперового підпису не можуть блокувати редагування/видалення. Канонічна вимога Issue #264.
- Реалізовано: редагування наказів незалежно від статусу/підпису; позначка про паперовий підпис вмикається/вимикається; скасований наказ можна знову ввести в дію; видалення наказу після підтвердження; до журналу записуються реквізити наказу та пов'язані записи; картки працівників/ТЗ і вже створені DOCX/PDF/JPG зберігаються.
- Операційна цілісність: при видаленні прибираються лише зв'язки самого наказу; пов'язані закріплення можуть вплинути на допоміжний облік. Користувач отримує попередження; рішення за ним.
- PR-head CI: Windows #1352, Win7 #333, macOS #1258, START #2380 — **SUCCESS**; START ZIP перевірено, 1 724 071 байт, SHA256 `ffd0594374bac45c11c88a68681b05231ba791a9a81706df10e1a25097a403a6`.
- **Exact-main CI PASS:** Windows #1353, Win7 #334, macOS Intel/ARM #1259, START #2381 — SUCCESS; START містить 610 файлів, 1 725 852 байти, SHA256 `caba27007ed4e3e21193d010623d2c683f792a4d3febe9c079a8473bd43a24c5`. Google Drive recovery-copy підтверджена: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.14-r3_2026-11-09_START.zip`, ID `1Qdb8WHiCTtkN7bKBF7pBaFxU8wctssya`, розмір 1 725 852 байти; URL https://drive.google.com/file/d/1Qdb8WHiCTtkN7bKBF7pBaFxU8wctssya/view .
- Ручне приймання власником — **PENDING**: перевірити виправлення чинного/підписаного/скасованого наказу, зняття відмітки паперового підпису, видалення, контроль файлів Word/PDF/JPG, відсутність впливу на картки людей/транспорту.
- **Одна наступна дія:** ручне приймання власником 10.14-r3 через `START.bat`: редагувати чинний/підписаний/скасований наказ, змінити позначку паперового підпису, видалити наказ з пов'язаними допоміжними записами, перевірити збереження карток людей/ТЗ та раніше створених DOCX/PDF/JPG. Після feedback планувати 10.14-r4. Не публікувати stable без окремого рішення.

## Попередні етапи (історія)\n\n## 10.14-r2 — накази: DOCX, PDF, JPG, 09.11.2026

- **Product merged:** PR #263, exact source `8ec6b2649f0f1a88da5851b4bc40486642165b69`. Stable/Latest лишається `v10.12-r10`. Next code revision: `10.14-r3`.
- Формати наказів: DOCX (редагований текст), PDF (друкований макет), JPG кожної сторінки (з PDFium), а також «Створити все». Перегляд у Taxo, відкриття зовнішньою програмою за вибором.
- Немає нових залежностей; ліцензійна перевірка у `docs/releases/RELEASE_NOTES_v10.14-r2.md`; PyMuPDF/AGPL не застосовується.
- PR-head Windows #1345, Win7 #327, macOS #1252, START #2358 — SUCCESS. Exact-main Windows #1346, Win7 #328, macOS #1253, START #2359 перевіряються; START SUCCESS.
- Owner ручний прийом ще **PENDING**. Не називати stable або опублікованим релізом.
- **Свіже рішення власника:** Taxo — допоміжне робоче середовище. Контроль офіційних документів — на паперових примірниках. **Не блокувати** редагування, зміну чи видалення наказів за ознакою статусу або підпису. Issue #264 замінено цим правилом; попередні заборони відкликані.
- **Одна наступна дія:** звірити exact-main CI, завершити контрольну документацію, далі у `10.14-r3` реалізувати вільне редагування/видалення наказів із простими підтвердженнями й цілісністю робочих даних. Резервна копія Drive для r2 ще не підтверджена.

## 10.14-r1 — безпечний друк наказів — 09.11.2026

**Фактично інтегровано:** PR #261, product `cc3ff5011298e2d287175ab39944012ba36a508d`; stable `v10.12-r10` **не змінювався**. Нова ревізія коду `10.14-r1` — integrated-only до окремого рішення про публікацію.

- При повторному друці наказу попередній файл PDF зберігається; створюється нова копія.
- Формування використовує наявний Taxo safe output із тимчасовим файлом, обробкою блокування/доступу та відмови.
- Після успіху відкривається штатний переглядач PDF Taxo, як у Бланках підтвердження діяльності; скасування/помилка не відкриває старий файл як новий.
- Логіку розділено на `src/taxo/order_pdf_workflow.py` і старі кнопки збережено; текст/макет PDF не переписували.
- PR-head: Windows #1340 SUCCESS; Win7 #323 SUCCESS; macOS #1248 SUCCESS; START #2345 SUCCESS, **1002 tests OK**.
- **Exact-main PASS:** Windows #1341, Win7 #324, macOS Intel/ARM #1249, START #2346; усі SUCCESS. START 1002 tests OK, ZIP перевірено.
- **Google Drive recovery-copy підтверджено:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.14-r1_2026-11-09_START.zip`, **1 708 502 байти**, Drive file `1BjwIIGIQVw8Ncekx0qojKQbA60mS5-RG`; SHA256 перевіреного GitHub START artifact `77fc9ab5aebe103dfb082e11ebc569d2d5d02a07c61ea2ec57c3e724c26bc65f`. Ручне приймання власником — **PENDING**.
- Наступна **кодова** ревізія `10.14-r2`; не починати без завершення r1 checkpoint/feedback.
- **Одна наступна дія:** ручне приймання 10.14-r1 через `START.bat`: створити наказ, надрукувати PDF, повторити формування, звірити дві окремі копії й переглянути PDF у Taxo. Після feedback вирішити наступне вузьке завдання для 10.14-r2. Stable не змінювати.
- Докладно: `docs/releases/RELEASE_NOTES_v10.14-r1.md`; рішення про друк: `docs/maintenance/RECOVERY_CHECKPOINT_2026-11-08_PRINT_WORKFLOW.md`.

## Попередня контрольна точка після обриву чату — 08.11.2026

Окремий повний запис: [RECOVERY_CHECKPOINT_2026-11-08_PRINT_WORKFLOW.md](docs/maintenance/RECOVERY_CHECKPOINT_2026-11-08_PRINT_WORKFLOW.md).

- Фактично integrated: **10.13-r10** (PR #258); stable **10.12-r10**. Windows 997 tests OK / Win7 / macOS Intel+ARM / START: SUCCESS. Open PR: 0 на час звірки. Owner manual acceptance: **PENDING**.
- **Нове рішення власника щодо друку:** не вигадувати окремий текстовий/друкарський сценарій наказів; взяти за зразок наявне **формування і друк Бланків підтвердження діяльності**, його форми та робочий шлях. Не роздувати один програмний файл — відокремлювати логічні фрагменти, не гублячи старі функції.
- Це рішення **зафіксовано, але ще не реалізовано в коді**. Наступна кодова ревізія — **10.14-r1**, не повторювати r10.
- **Одна наступна дія:** прочитати код поточного сценарію Бланків підтвердження діяльності, зіставити його з preview/PDF наказів r10 та зафіксувати конкретні відмінності **перед** реалізацією 10.14-r1. Жодного нового релізу або stable promotion цією документацією не робиться.

## База
- **Stable / Latest:** [v10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10) — promoted 07.11.2026 з exact product source `6d0f32bc45323d4085bb165b2ec050dae7b378ee`; 8 assets; GitHub Latest.
- **Історичний prerelease:** [v10.11-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r10), exact source `b239bb0dda6a49878f5f06a0edd791710b62df9b`; **архівний, не активна лінія розробки**. Актуальна stable — 10.12-r10; активний код — 10.13-r10.
- **Поточний integrated product candidate:** **10.13-r10**, PR #258, exact product commit `46ef1b995cfc42e8a3195d2f654ad0a9d5e07bb4`.
- **CI integration checkpoint:** PR #220 merged → `894fdbb235b2b91c2bb334b8fadfb99566671fc9`; post-merge docs-only smoke PR #222 merged → `bc32daa1b63c20aa4398fa35262d32456b62088c`. Подальший docs-only recovery checkpoint може змінити repository HEAD без зміни продуктової ревізії.
- 10.12-r1…r9 лишаються integrated-only; **10.12-r10 опубліковано як stable/latest**; 10.13-r1/r2/r3/r4/r5/r6/r7/r8/r9/r10 лишаються integrated-only.
- **Попередня Google Drive recovery-copy — 10.13-r2:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r2_2026-11-07_START.zip`, 1 624 847 байт; Drive file `1f5z-jgnDwTEFSSexxoKA14G5mykUW1GV`; START #2321 artifact SHA256 `b8fccfebbb906ed86854ba47a21f77d6884de9232594e16238bdaff0245223f0`.
- **Попередня Google Drive recovery-copy — 10.13-r3:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r3_2026-11-07_START.zip`, 1 636 456 байт; Drive file `1F8R4-qUukZQr86iaBp2PWSuvGow43Gnn`.
- **Google Drive recovery-copy 10.13-r4:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r4_2026-11-07_START.zip`, 1 648 645 байт; Drive file `1_861lkkVbBzhxiBlDbhKexG2jLcE6WAN`; exact START artifact #13591576959 SHA256 `6fd45b64748df00506dcae1420d48db5959f847f1e884d3040b0f0eb6eea4555`.
- **Google Drive recovery-copy 10.13-r5:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r5_2026-11-08_START.zip`, 1 656 837 байт; Drive file `12xjT-MYyacorZVroEesvEicwR7Z17nPP`; exact START #2327 artifact SHA256 `c4d3f8cdbfa1d6c911f74bddc6682f18dc71a55699896ffbc5142d14c1c37107`.
- **Google Drive recovery-copy 10.13-r6:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r6_2026-11-08_START.zip`, 1 669 795 байт; Drive file `1MXbWM_ppcKBGhRRtPJtq8V1Y226_4YKK`; exact START #2329 artifact SHA256 `6b362f065190b708f27c11cb1f8d08cd70fe57a9b2d5e72d0b2b247736392e36`.
- **Google Drive recovery-copy 10.13-r7:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r7_2026-11-08_START.zip`, 1 680 167 байт; Drive file `1lVmLFCqToh_9Bqhxrdd1e9Yuzz8Ol5r2`; exact START #2331 artifact SHA256 `09e0185d52dfbfd31c6745cf2afa31910be6a88645b18678eb95f683a8dbfea0`.
- **Google Drive recovery-copy 10.13-r8:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r8_2026-11-08_START.zip`, 1 685 617 байт; Drive file `1rj63QCtxmw4laO1KOnoVlx2PJoNccb20`; exact START #2333 artifact SHA256 `19cc825561f367afaa84d75cbc621dbd4767aa8f7bf284bd1d60a1a5cc35b61f`.
- **Google Drive recovery-copy 10.13-r9:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r9_2026-11-08_START.zip`, 1 691 957 байт; Drive file `1V1DNORZsku-LTl6UVqHlnfo5U5jFmJre`; exact START #2335 artifact SHA256 `83544cb6f0b5a1f34427051dfce11023f2861fd81fa0eb3d5051e95d2a3c201a`.
- **Google Drive recovery-copy 10.13-r10:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r10_2026-11-08_START.zip`, 1 699 549 байт; Drive file `1F5-tTsEqlH6o8xdeSKdQcRBPbZ3k_iVs`; exact START #2336 artifact SHA256 `9810df24b3a0ded29ec33ec8f804e18b29ef284853e47fe3763e22e994d2c0f3`.
- **Наступна кодова ревізія:** **10.14-r1** після ручного приймання r10.
- Stable не змінювати без окремого рішення власника. Поточне рішення власника 07.11.2026 — stable = 10.12-r10.

## 10.13-r10 — видимий текст наказу та прямий друк

PR #258 merged → exact product commit `46ef1b995cfc42e8a3195d2f654ad0a9d5e07bb4`.

- За owner feedback r9 закрито UX-проблему: створений наказ існував, але готовий текст і шлях до друку були неочевидні.
- Додано **«Перегляд наказу»** з фактичним змістом перед друком: шапка, дата/номер/місце, тема, вступ, **«НАКАЗУЮ»**, усі ТЗ/водії, контроль і підписний блок.
- У реєстрі є пряма дія **«Переглянути / друк»**; double-click по наказу відкриває той самий preview.
- У preview є **«Сформувати PDF / друк»**; чинний PDF generator лишається джерелом друкованого документа.
- Після створення наказу Taxo лишається на вкладці «Накази», виділяє новий запис і автоматично відкриває його текст замість прихованого переходу на «Закріплення водіїв».
- Regression перевіряє реальний preview наказу з кількома водіями, реквізити, «НАКАЗУЮ», контроль, підписний блок і всі UI-входи.
- PR-head: Windows #1335 — **997 tests / OK**; Win7 #320 — SUCCESS; macOS #1245 Intel/ARM — SUCCESS.
- **Exact-main:** Windows #1336 — **997 tests / OK**; Win7 #321 — SUCCESS; macOS #1246 Intel/ARM — SUCCESS; START #2336 — SUCCESS.
- Exact START recovery-copy r10 підтверджена на Google Drive: 1 699 549 байт, file `1F5-tTsEqlH6o8xdeSKdQcRBPbZ3k_iVs`, SHA256 `9810df24b3a0ded29ec33ec8f804e18b29ef284853e47fe3763e22e994d2c0f3`.
- Stable лишається **v10.12-r10**. r10 integrated-only і є поточним owner manual-test candidate.
- Цикл 10.13 закритий по ревізіях; наступна code revision після feedback — **10.14-r1**.

## 10.13-r9 — виправлення після ручного тестування r8

PR #256 merged → exact product commit `c0497c2679978f0936e1a36df3ad97c7244f8d12`.

- Виправлено падіння створення наказу: legacy template wrapper тепер передає `order_series` до актуального `create_order`.
- Дублікат закріплення більше не показує сирий SQLite `UNIQUE constraint failed`: одиночний дубль отримує людське повідомлення; bulk-add пропускає вже наявні пари й додає нові.
- Початкові/наступні номери наказів тепер мають прямий вхід **«Нумерація наказів…»** з реєстру наказів; у налаштуваннях є окремий видимий блок із work/personnel sequence.
- Після завантаження Taxo головне вікно одноразово піднімається вперед і бере фокус; режим always-on-top автоматично вимикається.
- Owner підтвердив: для швидкого функціонального приймання достатньо **START ZIP + START.bat**; Portable/installer лишаються більшими checkpoint/stable пакетами.
- PR-head: Windows #1332 — **993 tests / OK**; Win7 #318 — SUCCESS; macOS #1243 Intel/ARM — SUCCESS.
- **Exact-main:** Windows #1333 — **993 tests / OK**; Win7 #319 — SUCCESS; macOS #1244 Intel/ARM — SUCCESS; START #2335 — SUCCESS.
- Exact START recovery-copy r9 підтверджена на Google Drive: 1 691 957 байт, file `1V1DNORZsku-LTl6UVqHlnfo5U5jFmJre`, SHA256 `83544cb6f0b5a1f34427051dfce11023f2861fd81fa0eb3d5051e95d2a3c201a`.
- Stable лишається **v10.12-r10**. r9 integrated-only і є поточним owner manual-test candidate.
- Наступна code revision — **10.13-r10** тільки після зворотного зв'язку з r9.

## 10.13-r8 — безпечне масове закріплення

PR #254 merged → exact product commit `78112c03db5406a2e4d9e4e4452226f6c9a82d0f`.

- Закрито self-audit r7: масовий selector більше **не дозволяє «1 водій → кілька ТЗ»** з одним періодом, бо чинний approval invariant правильно забороняє одночасне закріплення одного водія за різними ТЗ.
- Дозволені робочі схеми: **1 ТЗ → кілька водіїв**, **N ТЗ ↔ N різних водіїв** за порядком вибору, або одна пара.
- Неоднозначна різна кількість ТЗ/водіїв і one-driver/many-vehicles блокуються ще до створення масових пар.
- UI більше не рекламує невалідний режим.
- Behavioral regression проходить через реальний «Ввести в дію»: 1 ТЗ + кілька водіїв — PASS; N різних пар — PASS; вручну створений конфлікт одного водія на кілька ТЗ — правильно блокується, наказ лишається чернеткою.
- Автонумерація r7 збережена: робоча серія `1,2,3…`, кадрова `1-К,2-К,3-К…`, next number конфігурується.
- PR-head: Windows #1328 — **987 tests / OK**; Win7 #314 — SUCCESS; macOS #1239 Intel/ARM — SUCCESS.
- **Exact-main:** Windows #1329 — **987 tests / OK**; Win7 #315 — SUCCESS; macOS #1240 Intel/ARM — SUCCESS; START #2333 — SUCCESS.
- Exact START recovery-copy r8 підтверджена на Google Drive; реквізити наведені вище.
- Stable лишається **v10.12-r10**. r8 integrated-only, не окремий release.
- **r8 — версія для ручного приймання власником.** Наступна code revision — **10.13-r9** тільки після зворотного зв'язку з цього тесту.

## 10.13-r7 — масові закріплення та автонумерація

PR #252 merged → exact product commit `4c90082aba0aa3f1c7f4636466ceaa08aa541ecf`.

- Наказ про закріплення отримав масовий вибір водіїв і ТЗ; у чернетці є окрема дія **«Додати багато…»**, старе додавання однієї пари збережене.
- Додано дві незалежні послідовності номерів: робочі/експлуатаційні `1,2,3…` та кадрові `1-К,2-К,3-К…`; наступні номери налаштовуються у «Відповідальні».
- Старі накази мігрують як робоча серія; робочий лічильник продовжується після найбільшого старого номера.
- PR-head: Windows #1320 — **981 tests / OK**; Win7 #306 — SUCCESS; macOS #1231 Intel/ARM — SUCCESS.
- **Exact-main:** Windows #1321 — **981 tests / OK**; Win7 #307 — SUCCESS; macOS #1232 Intel/ARM — SUCCESS; START #2331 — SUCCESS.
- Exact START recovery-copy r7 підтверджена на Google Drive; реквізити наведені вище.
- **Відоме до видачі:** r7 draft-helper дозволяє «1 водій → кілька ТЗ», але чинний захист введення наказу в дію правильно блокує одночасне закріплення одного водія за різними ТЗ. Тому r7 не віддавати власнику як фінальний тестовий пакет; наступна **10.13-r8** має прибрати цей суперечливий режим із UI/helper і додати regression на approval.
- Stable лишається **v10.12-r10**. r7 integrated-only.

## 10.13-r6 — структуровані працівники й ТЗ у наказах

PR #249 merged → exact product commit `a3f4e7e924f8d4c7389b28dc659c2f1e72e210da`.

- Для наказів (крім спеціалізованого наказу про закріплення) додано окрему вкладку **«Учасники / ТЗ»**.
- Можна масово вибрати кількох працівників або кілька ТЗ, шукати за ПІБ/табельним №/ідентифікатором або держномером/VIN і задати роль/призначення.
- Для водійських типів наказів employee-selector використовує саме driver-only базу.
- Кожний структурований зв'язок зберігає stable Taxo ID та **frozen snapshot** реквізитів. Подальша зміна ПІБ, табельного №, держномера, моделі чи VIN у живій картці не переписує історичний перелік наказу.
- Неактивні записи не можна додавати до нового наказу; після введення наказу в дію структурований перелік не редагується.
- Додавання/видалення учасника або ТЗ лишається в історії наказу навіть після видалення рядка з чернетки.
- PDF наказу з таким переліком отримує окрему сторінку **«Структурований перелік працівників і транспортних засобів»**; для працівника друкується табельний №/Taxo ID, для ТЗ — VIN; повний РНОКПП автоматично не друкується.
- Наказ про закріплення ТЗ за водіями зберігає спеціалізовану модель `vehicle_driver_assignments` і окрему вкладку.
- Schema change additive: нова `operations_order_entities`; існуючі накази/дані не переписуються. Plan/fact, юридичні підписи, stable/release/security не змінювались.
- PR-head: Windows #1312 — **972 tests / OK**; Win7 #298 — SUCCESS; macOS #1223 Intel/ARM — SUCCESS. Перший ARM runner впав до checkout через пошкоджений manifest `actions/checkout`; повтор того самого job без зміни коду — SUCCESS.
- **Exact-main після merge:** Windows #1313 — **972 tests / OK**; Win7 #299 — SUCCESS; macOS #1224 Intel/ARM — SUCCESS; START #2329 — SUCCESS.
- Exact START recovery-copy r6 підтверджена на Google Drive; файл, розмір і SHA256 наведені вище.
- Stable лишається **v10.12-r10**. r6 integrated-only, не окремий release.
- Наступна code revision — **10.13-r7** після ручного приймання r6.

## 10.13-r5 — спільний вибір працівників, водіїв і ТЗ

PR #247 merged → exact product commit `0b6e0b99dedcfcdbfe25df1460f483d197e623c9`.

- Створено **одне спільне джерело вибору** сутностей для наказів, інструктажів та наступних документів замість окремих несумісних списків.
- Працівник визначається стабільним ID Taxo; для людини показуються ПІБ, табельний № і посада. РНОКПП та реєстровий ID доступні для точного зіставлення/пошуку, але РНОКПП **не друкується автоматично** у підготовчий список.
- Водії є відфільтрованою підмножиною того самого списку; механіки/інші працівники не потрапляють у driver-only вибір.
- ТЗ визначається стабільним ID, держномером та VIN; у виборі показуються держномер + марка/модель + VIN.
- Нові документи пропонують активні сутності; історичний режим не втрачає деактивовані записи.
- «Інструктажі та журнали» тепер використовують структурований вибір працівників; підготовчий CSV містить ПІБ, табельний № і Код Taxo, але не повний РНОКПП.
- Choice-row вже містить snapshot ідентифікаційних реквізитів як основу для наступного етапу. **Збереження immutable snapshot у всіх типах наказів ще не реалізовано** — це окрема робота.
- DB schema, plan/fact, юридичне підписання/проведення інструктажів, stable/release/security у r5 не змінювались.
- PR-head: Windows #1308 — **960 tests / OK**; Win7 #294 — SUCCESS; macOS #1219 ARM64/Intel — SUCCESS.
- **Exact-main після merge:** Windows #1309 — **960 tests / OK**; Win7 #295 — SUCCESS; macOS #1220 ARM64/Intel — SUCCESS; START #2327 — SUCCESS.
- Exact START recovery-copy r5 підтверджена на Google Drive; файл, розмір і SHA256 наведені вище.
- Stable лишається **v10.12-r10**. r5 не опублікований як окремий release.
- Наступна code revision — **10.13-r6**; перед новою кодовою роботою бажане ручне приймання r5 власником.

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

## Попередня наступна дія (08.11, історія)

Ручно прийняти **10.13-r10 START** через `START.bat`: створити наказ про закріплення з кількома водіями, переконатися що одразу відкрився **«Перегляд наказу»**, звірити весь текст і сформувати PDF через **«Сформувати PDF / друк»**. Після feedback наступна code revision — **10.14-r1**. Stable лишається 10.12-r10.

## Recovery

`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md` → `WORKLOG.md` / Issue #61 / #164 / #175.
