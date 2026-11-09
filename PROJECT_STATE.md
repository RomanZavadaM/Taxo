# PROJECT_STATE — Taxo

**Дата:** 09.11.2026  
**Repository:** `RomanZavadaM/Taxo`

## 10.14-r4 — єдиний вигляд наказів Word / PDF / JPG — 09.11.2026

- **Інтегровано:** PR #268, точний product commit `677458afa06893b4d221130db72de4045187e0c8`. Stable/Latest лишається `v10.12-r10`, наступна кодова ревізія — `10.14-r5`.
- Виправлено розходження макета, яке показав власник на прикладі наказу №25. Замість простого тексту Word формує редаговані таблиці: дата/номер/місце, транспорт/номер/водій, підпис. Зміст і структуру основного наказу Word і два PDF-шляхи отримують зі спільного `order_layout.py` + `order_pdf_sections.py`. JPG візуально походить від PDF.
- Враховані **додатки та структуровані переліки**: Word отримує їх із бази, як PDF із додатками. Не вирізати з маршруту друку `v1073_features.py`.
- З вікна наказу «Перегляд DOCX» більше не показує оманливий простий текст: за наявності PDF цього сеансу відкривається друкований PDF; інакше файл відкривається у Word-сумісній програмі комп'ютера. Загальний спрощений viewer для інших документів Taxo не змінювали.
- **Без нових бібліотек і без змін ліцензій:** використовуються наявні python-docx, ReportLab, PDFium/Pillow. Не додано PyMuPDF.
- PR-head перевірки **PASS**: Windows #1356, Win7 #336, macOS #1261, START #2401, з тестами таблиць двох водіїв і тексту додатка. Exact-main Windows #1357, Win7 #337, macOS #1262 — **ще перевіряються**, START #2402 — SUCCESS.
- **Exact-main START recovery ZIP перевірено**: `Taxo_CURRENT_MAIN_v10.14-r4_2026-11-09_START.zip`, 1 735 775 байтів, 614 файлів, SHA256 `24a55af49a53d581bd45c4472fbd6ea77391bcd98328cab65cb808d7b52215ef`; цілісність ZIP = OK; нові модулі присутні. **Google Drive backup CONFIRMED**: `02_CURRENT_MAIN`, ID `13cu1dNOBcVAS8zFO0Z1JnBUy212wu3dp`, https://drive.google.com/file/d/13cu1dNOBcVAS8zFO0Z1JnBUy212wu3dp/view .
- **Ручне приймання власником PENDING:** створити наказ із двома водіями, «Створити все», звірити справжні Word і PDF (таблиця, номер, місце, текст, підпис), JPG; повторити для наказу з додатками. Можливі невеликі відмінності переносу рядків/сторінок Word залежно від шрифтів.
- **Наступна безпечна дія:** підтвердити exact-main Windows/Win7/macOS PASS, завершити checkpoint-документацію, прийняти зворотний зв'язок власника. Новий код 10.14-r5 лише після цього. Не просувати stable автоматично.

**Незмінне правило власника:** Taxo — допоміжне середовище, паперові оригінали контролює людина; статус/підпис не блокують редагування чи видалення.

## 10.14-r3 — накази без програмних заборон — 09.11.2026

- **Product integrated:** PR #266; `main` product SHA `eb4a45ffa6336ff25342816e615d720b3f33b861`. Stable/Latest — **v10.12-r10**, без змін; наступна кодова ревізія — **10.14-r4**.
- **Рішення власника:** Taxo — допоміжна програма для документів. Справжній контроль офіційних наказів — за паперовими примірниками. Статус чи позначка паперового підпису не можуть блокувати редагування/видалення. Канонічна вимога Issue #264.
- Реалізовано: редагування наказів незалежно від статусу/підпису; позначка про паперовий підпис вмикається/вимикається; скасований наказ можна знову ввести в дію; видалення наказу після підтвердження; до журналу записуються реквізити наказу та пов'язані записи; картки працівників/ТЗ і вже створені DOCX/PDF/JPG зберігаються.
- Операційна цілісність: при видаленні прибираються лише зв'язки самого наказу; пов'язані закріплення можуть вплинути на допоміжний облік. Користувач отримує попередження; рішення за ним.
- PR-head CI: Windows #1352, Win7 #333, macOS #1258, START #2380 — **SUCCESS**; START ZIP перевірено, 1 724 071 байт, SHA256 `ffd0594374bac45c11c88a68681b05231ba791a9a81706df10e1a25097a403a6`.
- **Exact-main CI PASS:** Windows #1353, Win7 #334, macOS Intel/ARM #1259, START #2381 — SUCCESS; START містить 610 файлів, 1 725 852 байти, SHA256 `caba27007ed4e3e21193d010623d2c683f792a4d3febe9c079a8473bd43a24c5`. Google Drive recovery-copy підтверджена: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.14-r3_2026-11-09_START.zip`, ID `1Qdb8WHiCTtkN7bKBF7pBaFxU8wctssya`, розмір 1 725 852 байти; URL https://drive.google.com/file/d/1Qdb8WHiCTtkN7bKBF7pBaFxU8wctssya/view .
- Ручне приймання власником — **PENDING**: перевірити виправлення чинного/підписаного/скасованого наказу, зняття відмітки паперового підпису, видалення, контроль файлів Word/PDF/JPG, відсутність впливу на картки людей/транспорту.
- **Одна наступна дія:** ручне приймання власником 10.14-r3 через `START.bat`: редагувати чинний/підписаний/скасований наказ, змінити позначку паперового підпису, видалити наказ з пов'язаними допоміжними записами, перевірити збереження карток людей/ТЗ та раніше створених DOCX/PDF/JPG. Після feedback планувати 10.14-r4. Не публікувати stable без окремого рішення.

## 10.14-r2 — накази: DOCX, PDF, JPG, 09.11.2026

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

## Поточний підтверджений стан

- **Stable / Latest:** Taxo 10.12-r10 / `v10.12-r10` — promoted 07.11.2026; exact source `6d0f32bc45323d4085bb165b2ec050dae7b378ee`; 8 assets; GitHub Latest.
- **Previous stable / safe rollback:** Taxo 10.10-r5 / `v10.10-r5`.
- **Older rollback:** Taxo 10.9-r10 / `v10.9-r10`.
- **Older rollback:** Taxo 10.3 / `v10.3`; historical tag target `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
- **Historical prerelease (archive only):** `v10.11-r10`, exact source `b239bb0dda6a49878f5f06a0edd791710b62df9b`. Ніяких поточних робіт із 10.11: stable — 10.12-r10, integrated development — 10.13-r10; історичний тег зберігається.
- **Previous integrated product candidate:** Taxo **10.13-r10**, exact product commit `46ef1b995cfc42e8a3195d2f654ad0a9d5e07bb4`, PR #258. Stable лишається 10.12-r10; 10.13-r1…r10 integrated-only і не stable.
- **CI maintenance checkpoint:** PR #220 merged → `894fdbb235b2b91c2bb334b8fadfb99566671fc9`; docs-only post-merge smoke PR #222 merged → `bc32daa1b63c20aa4398fa35262d32456b62088c`. Product version unchanged.
- **Next code revision:** **10.14-r2** після ручного приймання r10. Для r10 exact-main Windows/Win7/macOS/START і Google Drive recovery-copy — PASS.
- **Continuity:** `HANDOFF_CURRENT.md` — обов'язковий recovery-знімок; private process profile — `RomanZavadaM/dev-strategy` / `profile/taxo` / `TAXO_PROFILE.md`.
- **Previous Google Drive backup:** exact-source START recovery-copy для 10.13-r2 підтверджена: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r2_2026-11-07_START.zip`, 1 624 847 байт; Drive file `1f5z-jgnDwTEFSSexxoKA14G5mykUW1GV`; source artifact START #2321, SHA256 `b8fccfebbb906ed86854ba47a21f77d6884de9232594e16238bdaff0245223f0`.
- **Previous Drive recovery-copy:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r3_2026-11-07_START.zip`, 1 636 456 байт; file `1F8R4-qUukZQr86iaBp2PWSuvGow43Gnn`.
- **Previous Drive recovery-copy:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r4_2026-11-07_START.zip`, 1 648 645 байт; file `1_861lkkVbBzhxiBlDbhKexG2jLcE6WAN`; START artifact SHA256 `6fd45b64748df00506dcae1420d48db5959f847f1e884d3040b0f0eb6eea4555`.
- **Previous Drive recovery-copy:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r5_2026-11-08_START.zip`, 1 656 837 байт; file `12xjT-MYyacorZVroEesvEicwR7Z17nPP`; exact START #2327 artifact SHA256 `c4d3f8cdbfa1d6c911f74bddc6682f18dc71a55699896ffbc5142d14c1c37107`.
- **Previous Drive recovery-copy:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r6_2026-11-08_START.zip`, 1 669 795 байт; file `1MXbWM_ppcKBGhRRtPJtq8V1Y226_4YKK`; exact START #2329 artifact SHA256 `6b362f065190b708f27c11cb1f8d08cd70fe57a9b2d5e72d0b2b247736392e36`.
- **Previous Drive recovery-copy:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r7_2026-11-08_START.zip`, 1 680 167 байт; file `1lVmLFCqToh_9Bqhxrdd1e9Yuzz8Ol5r2`; exact START #2331 artifact SHA256 `09e0185d52dfbfd31c6745cf2afa31910be6a88645b18678eb95f683a8dbfea0`.
- **Previous Drive recovery-copy:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r8_2026-11-08_START.zip`, 1 685 617 байт; file `1rj63QCtxmw4laO1KOnoVlx2PJoNccb20`; exact START #2333 artifact SHA256 `19cc825561f367afaa84d75cbc621dbd4767aa8f7bf284bd1d60a1a5cc35b61f`.
- **Previous Drive recovery-copy:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r9_2026-11-08_START.zip`, 1 691 957 байт; file `1V1DNORZsku-LTl6UVqHlnfo5U5jFmJre`; exact START #2335 artifact SHA256 `83544cb6f0b5a1f34427051dfce11023f2861fd81fa0eb3d5051e95d2a3c201a`.
- **Current Drive recovery-copy:** `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r10_2026-11-08_START.zip`, 1 699 549 байт; file `1F5-tTsEqlH6o8xdeSKdQcRBPbZ3k_iVs`; exact START #2336 artifact SHA256 `9810df24b3a0ded29ec33ec8f804e18b29ef284853e47fe3763e22e994d2c0f3`.
- **Live ledger:** Issue #61 — історія, не перша сторінка recovery.

## Інтегрована розробка 10.13-r10 — видимий наказ і прямий друк

- PR #258 merged → exact product `46ef1b995cfc42e8a3195d2f654ad0a9d5e07bb4`.
- Owner feedback r9: наказ створюється, але текст і друк неочевидні.
- Додано read-only **«Перегляд наказу»** з фактичним змістом документа перед PDF; assignment preview містить усі ТЗ/водіїв, реквізити, «НАКАЗУЮ», контроль і підпис.
- Orders register має **«Переглянути / друк»** та double-click preview; preview має **«Сформувати PDF / друк»**.
- Після створення наказу UI залишається на «Накази», виділяє новий запис і автоматично відкриває preview.
- PR-head Windows #1335 — **997 tests / OK**; Win7 #320 SUCCESS; macOS #1245 Intel/ARM SUCCESS.
- Exact-main Windows #1336 — **997 tests / OK**; Win7 #321 SUCCESS; macOS #1246 Intel/ARM SUCCESS; START #2336 SUCCESS.
- Drive recovery-copy r10: 1 699 549 bytes, file `1F5-tTsEqlH6o8xdeSKdQcRBPbZ3k_iVs`, SHA256 `9810df24b3a0ded29ec33ec8f804e18b29ef284853e47fe3763e22e994d2c0f3`.
- Stable **10.12-r10** unchanged. r10 — owner manual-test candidate.
- 10.13 revision cycle exhausted; next code revision is **10.14-r1** after feedback.

## Інтегрована розробка 10.13-r9 — owner-test fixes

- PR #256 merged → exact product `c0497c2679978f0936e1a36df3ad97c7244f8d12`.
- Закрито owner-reported crash `order_series` у legacy order template wrapper.
- Duplicate assignment UX: single duplicate → людське повідомлення; bulk-add → existing pairs skipped, new pairs preserved; edit-to-duplicate blocked.
- У реєстрі наказів додано прямий **«Нумерація наказів…»**; стартові/наступні work/personnel номери більше не заховані лише у «Відповідальні».
- Головне вікно після повного старту одноразово виходить на передній план і бере focus; permanent topmost не лишається.
- Fast functional acceptance package = **START ZIP + START.bat** за рішенням owner.
- PR-head: Windows #1332 — **993 tests / OK**; Win7 #318 — SUCCESS; macOS #1243 Intel/ARM — SUCCESS.
- Exact-main: Windows #1333 — **993 tests / OK**; Win7 #319 — SUCCESS; macOS #1244 Intel/ARM — SUCCESS; START #2335 — SUCCESS.
- Drive recovery-copy r9: 1 691 957 bytes, file `1V1DNORZsku-LTl6UVqHlnfo5U5jFmJre`, SHA256 `83544cb6f0b5a1f34427051dfce11023f2861fd81fa0eb3d5051e95d2a3c201a`.
- Stable **10.12-r10** unchanged. r9 — owner manual-test candidate. Next revision **10.13-r10** after feedback.

## Інтегрована розробка 10.13-r8 — safety alignment bulk assignment

- PR #254 merged → exact product `78112c03db5406a2e4d9e4e4452226f6c9a82d0f`.
- r7 self-audit закрито: one-driver→many-vehicles більше не формується bulk helper/UI при одному validity window.
- Підтримуються 1 vehicle→many drivers і equal-size N vehicles↔N distinct drivers.
- Behavioral tests використовують реальний approval guard: допустимі масові накази вводяться в дію; manual conflicting one-driver/many-vehicles rows блокуються й наказ лишається draft.
- Автонумерація r7 лишається без змін: work `1,2,3…`, personnel `1-К,2-К,3-К…`, configurable next number.
- PR-head: Windows #1328 — **987 tests / OK**; Win7 #314 — SUCCESS; macOS #1239 Intel/ARM — SUCCESS.
- Exact-main: Windows #1329 — **987 tests / OK**; Win7 #315 — SUCCESS; macOS #1240 Intel/ARM — SUCCESS; START #2333 — SUCCESS.
- Drive recovery-copy r8: 1 685 617 bytes, file `1rj63QCtxmw4laO1KOnoVlx2PJoNccb20`, SHA256 `19cc825561f367afaa84d75cbc621dbd4767aa8f7bf284bd1d60a1a5cc35b61f`.
- Stable **10.12-r10** unchanged. r8 — owner manual-test candidate. Next revision **10.13-r9** only after feedback.

## Інтегрована розробка 10.13-r7 — масові закріплення й автонумерація

- PR #252 merged → exact product `4c90082aba0aa3f1c7f4636466ceaa08aa541ecf`.
- Assignment order: bulk select; 1 ТЗ→кілька водіїв, equal-size N↔N pairing; «Додати багато…» у draft; single-pair workflow збережено.
- Дві numbering series: work `1,2,3…`, personnel `1-К,2-К,3-К…`; next values конфігуруються, legacy work counter продовжується з наявної історії.
- PR-head: Windows #1320 — **981 tests / OK**; Win7 #306 — SUCCESS; macOS #1231 Intel/ARM — SUCCESS.
- Exact-main: Windows #1321 — **981 tests / OK**; Win7 #307 — SUCCESS; macOS #1232 Intel/ARM — SUCCESS; START #2331 — SUCCESS.
- Drive: 1 680 167 bytes, file `1lVmLFCqToh_9Bqhxrdd1e9Yuzz8Ol5r2`, SHA256 `09e0185d52dfbfd31c6745cf2afa31910be6a88645b18678eb95f683a8dbfea0`.
- Known follow-up before user delivery: r7 helper still allows 1 driver→many vehicles in draft while approval guard rejects simultaneous multi-vehicle assignment. Next revision **10.13-r8** must reject it earlier and add approval regression.
- Stable **10.12-r10** unchanged.

## Інтегрована розробка 10.13-r6 — структуровані працівники й ТЗ у наказах

- PR #249 merged → exact product `a3f4e7e924f8d4c7389b28dc659c2f1e72e210da`.
- Для звичайних наказів додано additive `operations_order_entities` та вкладку **«Учасники / ТЗ»** з масовим вибором працівників/ТЗ.
- Пошук підтримує ПІБ, табельний №/ідентифікатор, держномер і VIN; водійські типи наказів використовують driver-only pool.
- Кожен зв'язок має stable Taxo ID, роль у наказі, note і frozen snapshot реквізитів; зміна живої картки не переписує історичний перелік.
- Неактивні сутності не додаються до нового наказу; після введення наказу в дію перелік immutable.
- Add/remove події зберігаються в історії самого наказу навіть після видалення рядка з чернетки.
- PDF додає структурований перелік; employee identifier = табельний №/Taxo ID, vehicle identifier = VIN; RNOKPP автоматично не друкується.
- Наказ про закріплення ТЗ/водіїв лишається на спеціалізованій моделі.
- PR-head: Windows #1312 — **972 tests / OK**; Win7 #298 — SUCCESS; macOS #1223 Intel/ARM — SUCCESS після повтору infra-failed ARM job без зміни коду.
- Exact-main: Windows #1313 — **972 tests / OK**; Win7 #299 — SUCCESS; macOS #1224 Intel/ARM — SUCCESS; START #2329 — SUCCESS.
- Drive recovery-copy r6 підтверджена: 1 669 795 байт, file `1MXbWM_ppcKBGhRRtPJtq8V1Y226_4YKK`, SHA256 `6b362f065190b708f27c11cb1f8d08cd70fe57a9b2d5e72d0b2b247736392e36`.
- Stable **10.12-r10** незмінна; r6 не опублікований. Наступний code revision — **10.13-r7** після ручного приймання.

## Інтегрована розробка 10.13-r5 — спільні identity-aware selectors

- PR #247 merged → exact product `0b6e0b99dedcfcdbfe25df1460f483d197e623c9`.
- Працівники, водії та ТЗ для «Експлуатації» тепер походять зі спільного selector-контракту зі стабільним ID і реквізитами однозначної ідентифікації.
- Працівник: ПІБ, табельний №, посада; РНОКПП/registry ID доступні для точного зіставлення, але не виводяться автоматично у паперовий підготовчий список.
- Водій: driver-only фільтр спільної employee-моделі; механіки та інші ролі не змішуються з водіями.
- ТЗ: держномер + марка/модель + VIN; active для нового документа, historical для збереження старих зв'язків.
- «Інструктажі та журнали» використовують той самий структурований список працівників; CSV містить ПІБ, табельний № та Код Taxo.
- Shared choice містить snapshot реквізитів як технічну основу; персистентні immutable snapshots у всіх типах наказів — **ще наступний етап**, не заявляти як готове.
- PR-head: Windows #1308 — **960 tests / OK**; Win7 #294 — SUCCESS; macOS #1219 Intel/ARM — SUCCESS.
- Exact-main: Windows #1309 — **960 tests / OK**; Win7 #295 — SUCCESS; macOS #1220 Intel/ARM — SUCCESS; START #2327 — SUCCESS.
- Drive recovery-copy r5 підтверджена: 1 656 837 байт, file `12xjT-MYyacorZVroEesvEicwR7Z17nPP`, SHA256 `c4d3f8cdbfa1d6c911f74bddc6682f18dc71a55699896ffbc5142d14c1c37107`.
- Stable **10.12-r10** незмінна; r5 не опублікований. Наступний code revision — **10.13-r6** після ручного приймання.

## Інтегрована розробка 10.13-r4 — вибір водія й ТЗ у наказі про закріплення

- PR #244 merged → exact product `67b4670fdb29a46d03f9d6462ae2bd19603a2a5c`.
- Новий наказ про закріплення може одразу містити першу пару «активне ТЗ + чинний водій».
- Водії беруться з фактичної driver-моделі Taxo, а не із загального списку активних працівників.
- Частково заповнена пара блокується; порожня пара дозволяє старий draft-first workflow.
- Подальше додавання закріплень пропонує активні ТЗ/водіїв; історичне редагування не втрачає старих записів.
- Exact-product: Windows #1305 — **953 tests / OK**; Win7 #291 — SUCCESS; macOS #1216 ARM64/Intel — SUCCESS; START #2325 — SUCCESS.
- Drive recovery-copy r4 підтверджена. Stable **10.12-r10** незмінна.
- Наступний code revision — **10.13-r5** після ручного приймання.

## Інтегрована розробка 10.13-r3 — паперова підготовка інструктажів

- PR #239 merged → exact product `a7b13a920302fb1dbfb441bf6ba097953cc3f71b`.
- Окрема вкладка у «Експлуатації»; БДР/ОП, вид/дата/тема/підстава, активні працівники, квартал як організаційний орієнтир.
- Допоміжний CSV-список із видимою позначкою «НЕ Є ЖУРНАЛОМ», без підписів, статусу проведення, перезапису файлів і DB/schema змін.
- PR-head Windows #42414118500, Win7 #42414118532, macOS #42414118493 (Intel/ARM) — SUCCESS; live regression та ізольовані тести.
- Exact-product post-merge: Windows #42414412641, Win7 #42414412482, macOS #42414412631 Intel/ARM, START #42414412635 — **SUCCESS**. 584 files, exact SHA256 above. Drive recovery-copy r3 підтверджена.
- Наступний code revision 10.13-r4; stable 10.12-r10 незмінна. Manual acceptance ще потрібне.

## Stable promotion 10.12-r10

- Owner decision: stable → **10.12-r10**.
- Release: `v10.12-r10`, exact source `6d0f32bc45323d4085bb165b2ec050dae7b378ee`.
- Historical stable promoter run #42409237532 — SUCCESS; GitHub `/releases/latest` підтверджує `v10.12-r10`.
- 8 canonical assets: Windows Setup/Portable, Win7 Setup/Portable, macOS ARM64/Intel, START, SHA256SUMS.
- Stable release використав уже перевірені exact-r10 packages; 10.13-r1 у release не потрапив.
- Rollback stable: `v10.10-r5`.

## Поточний product main 10.13-r2 — presentation/usability consolidation

- **PR #232 → product commit `c6a2ad85b37019ab96fa32a0e597b625aea4815f`.**
- Явна кнопка «Відкрити вибране ТЗ» прибрала залежність від прихованого double-click; старий double-click збережено.
- Технічні коди СТОІР/одометра та ISO timestamps у робочих таблицях замінені людськими українськими підписами/датами.
- На робочому столі додано «Оформити новий наказ…»; дії наказів перебудовані у багаторядкові сітки для мінімальної ширини.
- Перший PR-head видалив старий «Каталог типів наказів»; Feature Loss gate `test_v10_12_r7` зловив регресію. Фінальний r2 зберігає і старий маршрут, і новий рекомендований маршрут.
- Plan/fact, DB schema, факти ТО/ремонтів/одометра, immutability наказів, нормативні тексти й release/security не змінено.
- PR-head: Windows #1287 — **941 tests / OK**; Win7 #278 — SUCCESS; macOS #1203 ARM64/Intel — SUCCESS.
- Exact-product: Windows #1288 — **941 tests / OK**; Win7 #279 — SUCCESS; macOS #1204 ARM64/Intel — SUCCESS; START #2321 — SUCCESS.
- Drive recovery-copy підтверджена.
- Stable = **10.12-r10**; r2 не опублікований; наступний code revision = **10.13-r3**.

## Попередній product main 10.13-r1 — Експлуатація / СТОІР usability consolidation

- **PR #227 → product commit `4ed9530b57a4e67fdca49c81da43602df074ebb0`.**
- Перед змінами повторно прочитано чинну dev-strategy, включно з mandatory Functional Loss Prevention rule; робота виконана як цілісний operational workflow, а не як окрема кнопка.
- «Експлуатація → Документи» стала робочим столом із прямим входом до СТОІР; старі маршрути збережені.
- СТОІР: стан автопарку перший; вибір ТЗ; UI профілю ТО; факт ТО/ремонту з виконавцем/приміткою; заявка «нова → у роботу → закрити з результатом»; прямий перехід ОТК → документи ТЗ; локалізовані статуси/пріоритети.
- Накази: старт «Що потрібно оформити?»; «Ввести в дію в Taxo» окремо від паперового підписання; early immutability guard; історія; однозначна незворотна позначка підписаного оригіналу; UI-скасування лише чернетки.
- Plan/fact, DB schema, нормативні типові тексти наказів, історичні факти та release/build workflows не змінено.
- PR-head: Windows #1274 — **936 tests / OK**; Win7 #265 — SUCCESS; macOS #1190 ARM64/Intel — SUCCESS.
- Exact-product post-merge: Windows #1275 — SUCCESS; Win7 #266 — SUCCESS; macOS #1191 ARM64/Intel — SUCCESS; START #2316 — SUCCESS.
- Google Drive exact-source recovery-copy підтверджена.
- Ручне приймання власником — наступний UX gate; наступний code revision — **10.13-r2**.

## Попередній product cycle 10.12-r10 — Feature Loss hardening

- **10.12-r1 / PR #202:** повернуто постійний вхід `Працівники → Планування → Простий місячний графік…`; код мультивибору працівників і PDF/XLSX був живий, але старий runtime-injector був ненадійним.
- **Feature Loss Audit / PR #203:** зафіксовано підтверджені історичні UI-entry regressions, крихкі runtime routes і чернетку реєстру функцій.
- **10.12-r2 / PR #204:** додано executable `function_registry.py` та cross-platform Tk/Xvfb reachability smoke; Windows #42352276336, Win7 #42352276288, macOS #42352276292 — SUCCESS.
- **10.12-r3 / PR #205:** Personnel Data Center став постійним штатним route; historical registry/Diia/document entries ховаються лише після гарантії replacement. Missing-anchor сценарій тепер fail-safe. PR-head Windows #42352755797 — **903 tests / OK**; Win7 #42352755837; macOS #42352755821 — SUCCESS.
- **10.12-r4 / PR #207:** живий UI-gate для `Експлуатація` та вкладеної `Відомість (додаток 1)`; Windows 907 tests / OK, Win7/macOS SUCCESS.
- **10.12-r5 / PR #209:** runtime-перевірка історично ламкого прапорця перепланування та всіх 9 дій шляхівок; Windows/Win7/macOS SUCCESS.
- **10.12-r6 / PR #210:** runtime-перевірка всіх 8 основних дій центру «Дані / Дія / документи…»; Windows/Win7/macOS SUCCESS.
- **10.12-r7 / PR #214:** live UI-gate для Центру документів і всіх 8 ключових дій/переходів; Windows **917 tests / OK**, Win7/macOS SUCCESS.
- **10.12-r8 / PR #216:** live UI-gate для «Тахограф», «Звіти», «Налаштування»; Windows **920 tests / OK**, Win7/macOS SUCCESS. Перший test-harness був виправлений після зависання/не-mapped контролу; продуктова логіка не змінювалась.
- **10.12-r9 / PR #218:** live UI-gate для «Водії для звіту…»; реальний selector відкривається, список водіїв і «Застосувати» доступні. Фінальний head `08a2ef6d`; Windows **923 tests / OK**, Win7/macOS SUCCESS. План/факт, БД і звітна логіка не змінювались.
- **10.12-r10 / PR #224:** live behavioral gate для «План → факт» на тимчасовій SQLite-БД: справжня кнопка реально копіює план лише у відсутній факт, а наявний підтверджений факт, планові поля та примітки лишаються недоторканими. Product commit `6d0f32bc45323d4085bb165b2ec050dae7b378ee`; PR-head Windows **931 tests / OK**, Win7/macOS SUCCESS; post-merge Windows #1269, Win7 #262, macOS #1187, START #2315 — SUCCESS. Product logic/schema не змінювались.
- **Feature Loss reachability cycle r1…r10:** executable registry тепер має runtime-smoke requirement для **23/23** критичних маршрутів. Подальші UX-зміни вести окремими вузькими slices через Issue #164, не як продовження цього audit-cycle.
- CI-дефект, підтверджений під час r9, закрито окремим process-only PR #220: superseded Windows/Win7/macOS PR runs скасовуються; ordinary docs-only PR лишає lightweight required Windows check; ordinary docs-only main push не запускає platform/START. PR #142/#152 закриті як superseded.
- Основний виявлений клас ризику: feature code може залишитися живим, але стати недоступним після UI feature-layer composition. Reachability-cycle r1…r10 закрито; подальший UX/backlog — Issue #164 окремими вузькими slices.

## Попередня інтегрована лінія 10.10-r6 → 10.11-r10

- **r6:** єдиний центр «Дані / Дія / документи» та масове поновлення державних даних для вибраних працівників.
- **r7:** вимоги до документів на рівні конкретного працівника; незалежний контроль строку; копії документів у workspace; employee documents завжди входять у повний backup.
- **r8:** простий місячний графік для вибраних працівників; шаблони Пн–Пт, 2/2, 3/3, щодня та вибрані дні; факт/відсутність/конфлікти не перезаписуються.
- **r9:** вибрані водії відображають основний worklog замість загальної кадрової норми; посада водія не створює дубль у планувальнику; виправлено аварію коригування відсутностей. Тести r9 додано. PR #160 merged; exact-main START, Windows, Windows 7, macOS ARM64/Intel — SUCCESS.
- **r10:** українське «част.»; вибір водіїв у деталізованому водійському PDF/Excel, PR #162 merged.
- **10.11-r1:** спрощення до вибору документа та двох дій; читабельні імена файлів; PR #163 merged. Exact-main START/Windows/Win7/macOS SUCCESS. Issue #164 — подальша системна UX робота.
- **10.11-r2:** PR #169 — інформативні назви простого графіка працівників і вилучення «Роль» лише з PDF; PR #171 — виправлення залишкових r1-імен у активному packaging; exact-main `68d7459b` START/Windows/Win7/macOS SUCCESS; prerelease `v10.11-r2` опублікований workflow #42086984364. Stable залишається r5.
- **10.11-r3:** повний code-review Issue #175 виявив два критичні дефекти цілісності даних; PR #176 закрив їх: «План → факт» більше не перезаписує існуючий факт, а детальне перепланування стало атомарним. Exact issued source `a82a3dc6`; START #42219595152, Windows #42219595132, Win7 #42219595055, macOS #42219595074 — SUCCESS; publisher #42220584720 опублікував immutable prerelease `v10.11-r3` з 8 assets. Google Drive START backup підтверджений. Наступна ревізія — 10.11-r4.
- **10.11-r4:** PR #179 — DB-level захист `control_protocols` від каскадного видалення через `discs`, UI guard і behavioral SQLite regression. Exact issued source `c4e70158`; START #42223328213, Windows #42223328267, Win7 #42223328554, macOS #42223328239 — SUCCESS; publisher #42224658087 опублікував immutable prerelease `v10.11-r4` з 8 assets. Google Drive START backup підтверджений. Наступна ревізія — 10.11-r5.
- **10.11-r5:** PR #182 — основна лінія Pillow 13.0.0 / pypdf 6.21.4; Win7 лишається на Python 3.8-сумісних Pillow 10.4.0 / pypdf 5.9.0 з Taxo page-tree security preflight і окремим Win7 security-smoke. Exact issued source `f2614caf`; START #42230454712, Windows #42230454659, Win7 #42230454846, macOS #42230454687 — SUCCESS; publisher #42231569758 опублікував immutable prerelease `v10.11-r5` з 8 assets. Google Drive START backup підтверджений.
- **10.11-r6:** PR #185 — atomic output через sibling temp + `os.replace`, composite restore failure reporting із шляхом до safety backup, явний disclosure `Data/EmployeeDocuments` у backup UI/name/docs. Exact issued source `558158a9777b18a05a224136fec4deeef55b5950`; START #42268068367 — **872 tests / OK**; Windows #42268068515, Win7 #42268068378, macOS #42268068403 — SUCCESS. Release-trigger PR #186; publisher #42269285656 — SUCCESS; immutable prerelease `v10.11-r6` має 8 assets. Google Drive START backup підтверджений.
- **10.11-r7:** PR #188 — Win7 workflow тепер перед packaging відновлює legacy layout для історичних regression-тестів і запускає **повний** `python -m unittest discover -s tests -v` на CPython 3.8.10. Під час переходу виправлено лише test-contract сумісність Python 3.8 (`removeprefix`, історичний r6 version anchor), runtime-логіку не змінено. Exact issued source `3f3b28366ce7d453a70f5a2573eb676c0b503d2c`; START #42273303324 — **876 tests / OK**; Windows #42273303147, Win7 #42273303116, macOS #42273303128 — SUCCESS. Release-trigger PR #189; publisher #42274663207 — SUCCESS; immutable prerelease `v10.11-r7` має 8 assets. Google Drive START backup підтверджений. Наступна ревізія — 10.11-r8.
- **10.11-r8:** PR #192 — `VERSION.txt` + `src/taxo/release_naming.py` стали єдиним джерелом package naming для Windows/Win7/macOS; Inno Setup більше не має revision defaults; stable promotion формує required assets з marker/version замість hardcoded r5. Exact issued source `f3e846c50e75bdc59560d10916cec90a7587cdac`; START #42283491422 — **881 tests / OK**; Windows #42283491587, Win7 #42283491399, macOS #42283491541 — SUCCESS. Release-trigger PR #193; publisher #42284631762 — SUCCESS; immutable prerelease `v10.11-r8` має 8 assets. Google Drive START backup підтверджений. Наступна ревізія — 10.11-r9.
- **10.11-r9:** PR #195 — усі official GitHub Actions у п'яти active workflows pinned до immutable commit SHA; current major refs звірені 06.11.2026, historical workflows не переписувались. Exact issued source `8f97218927b3ba6bc14aca465de4a196e2b19ba2`; START #42286505119 — **885 tests / OK**; Windows #42286505164, Win7 #42286505171, macOS #42286505215 — SUCCESS. Release-trigger PR #196; publisher #42287707654 — SUCCESS; immutable prerelease `v10.11-r9` має 8 assets. Google Drive START backup підтверджений. Наступна ревізія — 10.11-r10.
- **10.11-r10:** PR #198 — у загальному табелі персоналу PDF/Excel зведені до одного selector + «Зберегти…», ім'я файла уніфіковано як `Табель_робочого_часу_YYYY-MM_усі-працівники.*`; plan/fact і БД не змінені. Pre-release PR #199 додав release notes. Exact issued source `b239bb0dda6a49878f5f06a0edd791710b62df9b`; publisher exact-source gate знайшов SUCCESS для START/Windows/Win7/macOS; tag `v10.11-r10` перевірено на exact source. Stable лишається r5. Наступна ревізія — 10.12-r1.
- **Публікація:** docs PR #165/#166 та release trigger PR #167 merged; publish workflow #42063810115 SUCCESS. 10.11-r1 = immutable prerelease, не stable.
- **Зауваження власника до r1 закриті в r2:** неоднозначне ім'я `Графік_працівників_2026_11.pdf` замінено на змістовну схему, зайву колонку «Роль» прибрано лише з PDF. Подальший UX — Issue #164; власник тестує r2.
- Водійський план не дублюється у загальному плануванні персоналу.
- Персональний PDF/Excel містить тільки вибраних працівників і не показує службові проблеми інших ролей.
- Перед інтеграцією r8 повні перевірки Windows, Windows 7, macOS ARM64/Intel та START пройшли успішно.
- Повторна перевірка точного інтегрованого main r8: START, Windows, Windows 7, macOS ARM64 та Intel — SUCCESS.
- Stable / Latest залишається **v10.10-r5** до окремого рішення власника.

## Що додано в 10.10-r1

- PyMuPDF (AGPL-3.0) повністю прибрано з коду, тестів, requirements, specs і пакетів (`PROJECT_RULES.md` §17);
- новий `src/taxo/pdf_engine.py`: pypdfium2 (рендер), reportlab + pypdf (штамп);
- Бланк підтвердження PDF/JPG і дата у звіті №340 — попіксельно ідентичні попередній реалізації;
- вбудований перегляд/друк PDF — pypdfium2, з fallback на системну програму;
- license gate: `tests/test_v10_10_r1.py` + `scripts/check_bundle_licenses.py` у всіх збірках;
- без міграцій робочих БД і змін даних користувача.

## Поточна stable 10.10-r5

- виправлено показ версії у всіх вікнах і діалогах;
- повернено Windows 7 Setup поруч із Portable;
- опубліковано повний комплект Windows, Windows 7, macOS Intel/ARM, START і SHA256;
- універсальний механізм публікації замінив окремі publish-файли під кожну ревізію;
- виправлено macOS startup crash у навігації «Працівники»; виправлення перевірено власником на Apple Silicon.

## Що додано в 10.9-r10

- runtime/support Python modules перенесені з кореня в `src/taxo/`;
- executable entry points лишені в корені, сумісність flat imports збережена bootstrap-механізмом;
- runtime templates перенесені в `assets/`;
- активні PyInstaller/Inno Setup файли перенесені в `packaging/`, історичні spec — в `packaging/history/`;
- `START.bat`, Windows, Windows 7 і macOS packaging paths адаптовані до нової структури;
- `VERSION.txt` і `main.APP_VERSION` синхронізовані на `10.9-r10`;
- зміна не вводить міграції робочих БД, backup/workspace, сканів чи документів користувача.

## Інтегрована лінія 10.9-r2 → 10.9-r9

- **r2:** незворотна історія виданих шляхівок і номерів; retention не може видалити пов'язаний факт.
- **r3:** чинність обов'язкових документів ТЗ на весь плановий період рейсу.
- **r4:** посилений контроль робочого часу/відпочинку, gaps/overlaps, 3+9, weekly-rest spacing і двотижневий контроль.
- **r5:** 60-денний реєстр не вигадує відпочинок із невідомих хвилин; непідтверджений тахограф має нижчий пріоритет.
- **r6:** баланс персоналу/П-5, employment-aware historical selection, цикли 2/2 та 3/3.
- **r7:** СТОІР — хронологія одометра, fallback `work_date`, прогноз від останнього факту та spike guard.
- **r8:** незмінність затверджених/підписаних наказів, безпечне оновлення відповідального, захист driver→vehicle assignments.
- **r9:** SQLite schema compatibility baseline через `PRAGMA user_version` і future-schema guard.

## Репозиторій після structural cleanup

- поточний код береться тільки з `main`;
- `src/taxo/` — runtime/support modules;
- `assets/` — runtime templates/assets;
- `packaging/` — active build/installer definitions;
- historical work/candidate refs, tags і releases не є джерелом актуального коду;
- historical tags/releases залишаються immutable для audit/rollback.

## Чинні інваріанти

- plan і fact зберігаються окремо;
- факт не підміняється планом без явного підтвердження там, де це дозволено;
- Бланки підтвердження діяльності є фактичними документами;
- невідомий/ручний час не перетворюється автоматично на роботу чи відпочинок;
- роль водія має датовані періоди;
- видана шляхівка та історично використаний номер захищені від тихого фізичного знищення/повторного використання;
- робочі БД, SQLite, скани, кеші та персональні документи не входять у repository/release;
- видані tags/releases immutable;
- поточна stable — `10.12-r10`; rollback checkpoint — `10.10-r5`; поточний integrated main candidate — `10.14-r1`; наступна кодова ревізія — `10.14-r2`; stable змінюється лише окремим рішенням власника;
- у програму й пакети входять лише залежності з permissive-ліцензіями; PyMuPDF заборонений назавжди;
- regression-тести запускаються лише в CI або в ізольованому середовищі, ніколи — на машині з реальним робочим сховищем.

## Право та власність

Taxo — proprietary software.  
Правовласник: **Roman Zavada (Роман Завада), фізична особа**.  
**Copyright © 2026 Roman Zavada. All rights reserved.**

Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Джерело істини при новій сесії

`START_HERE.md` → `HANDOFF_CURRENT.md` → private `dev-strategy/profile/taxo/TAXO_PROFILE.md` → live GitHub → `PROJECT_STATE.md`; `WORKLOG.md` та Issue #61 — для деталей/історії.

При суперечності документації з live GitHub перемагає фактичний GitHub state.
