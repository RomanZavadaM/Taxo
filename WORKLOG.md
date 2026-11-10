## 10.11.2026 — 10.15-r4 опубліковано

- Exact product `ae0c673a42c5b633706efdffc1adfd5b1b70681d`: START [42807804380](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804380), Windows [42807804065](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804065), Win7 [42807804054](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804054), macOS [42807804153](https://github.com/RomanZavadaM/Taxo/actions/runs/42807804153) — SUCCESS.
- [v10.15-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r4) — prerelease, 8/8 assets, publisher [42808943357](https://github.com/RomanZavadaM/Taxo/actions/runs/42808943357) SUCCESS, tag = exact product; stable/latest v10.14-r4.
- Drive exact-source START artifact: `1QIyvVj4PPTKOjB3anHX4zX3IlxmhvA_X`, папка `02_CURRENT_MAIN`, 1 847 445 bytes; SHA256 до передавання `aa4449f6a3233a0e4dd7c0736acb73bf7fe04a14c5ab2ea67982a19777c6b4f2`. Після передавання перевірені назва, розмір і папка; повторне зчитування байтів не виконувалось.
- PR #305: оновлені сім README, інструкція, статус, release index, recovery; старі описи й стан збережені та звірені в приватному профілі `dev-strategy/profile/taxo/taxo-history/2026-11-10-before-10.15-r4/`.
- Наступна кодова ревізія 10.15-r5 після цього checkpoint: структурний етап наказів і інструктажів (#290); перенесення на цей момент не розпочиналося.

## 10.11.2026 — 10.15-r4 прийнято власником та інтегровано

- Власник повідомив, що тестував r4 і він, за його оцінкою, працює; доручив merge, релізний checkpoint, оновлення документації та перекладів.
- PR #304 merged: product `ae0c673a42c5b633706efdffc1adfd5b1b70681d`. PR-head `f199cdd6adef027788deffe3a9601daf8a87c2f3`: Windows [42807207434](https://github.com/RomanZavadaM/Taxo/actions/runs/42807207434), Win7 [42807207609](https://github.com/RomanZavadaM/Taxo/actions/runs/42807207609), macOS Intel/ARM [42807207436](https://github.com/RomanZavadaM/Taxo/actions/runs/42807207436) — SUCCESS.
- Exact-main CI та публікація мають бути звірені окремо; до наступної кодової ревізії потрібен завершений recovery checkpoint.
- До очищення описів копії дев'яти описових файлів і PROJECT_STATE записані та звірені у приватній гілці `dev-strategy/profile/taxo/taxo-history/2026-11-10-before-10.15-r4/`. Git та цей журнал залишають історію.
- Пріоритет після завершення checkpoint — реальна поетапна перебудова структури, починаючи з наказів та інструктажів; Issue #290.

## Перевірка документа ТЗ і відсутнього файла 10.11.2026

- PR #301 інтегровано: head `63d17d65d54a6fe187bb8cb1c6ca434958fa8bbd`, merge `fea9699ad638ad2b5f4a138f38488b771fb20c24`. Тест відновив пов'язаний із ТЗ 201 вигаданий PDF та реквізити; без вибору документів ТЗ файл не потрапив до ZIP.
- На вигаданих даних підтверджено ваду [#302](https://github.com/RomanZavadaM/Taxo/issues/302): коли документ працівника зник до копіювання, після відновлення запис і шлях залишились, файла немає, а контроль помилково показав копію та стан «Чинний». Ваду ще не виправлено.
- Exact head: Windows [42797582028](https://github.com/RomanZavadaM/Taxo/actions/runs/42797582028), Win7 [42797582005](https://github.com/RomanZavadaM/Taxo/actions/runs/42797582005), macOS Intel/ARM [42797582433](https://github.com/RomanZavadaM/Taxo/actions/runs/42797582433) — SUCCESS, тест у журналах ok, по 1057 тестів. Win7 — перевірка сумісності, не ручний запуск на Windows 7.
- Вікна створення і відновлення резерву та відкриття документів через програму ще не перевірені. Продукт, реліз і робочі дані не змінювалися.

## 10.11.2026 — відновлення прив'язаного PDF працівника

- PR #299: `tests/test_synthetic_workspace_restore.py` доповнено згенерованими вигаданими PDF та JPEG. PDF копіюється в `Data/EmployeeDocuments`, має запис документа, обов'язковість та контроль строку. У відновленій базі звіряються ID працівника, реквізити, вимоги і переносний шлях; PDF зчитується через pypdf і звіряється текст та байти. JPEG відкривається через Pillow.
- Exact PR head `a0df0a6b2855a24ce83987ae82d2b0caf0e4d735`: Windows [42794764832](https://github.com/RomanZavadaM/Taxo/actions/runs/42794764832), Win7 [42794764781](https://github.com/RomanZavadaM/Taxo/actions/runs/42794764781), macOS Intel/ARM [42794764605](https://github.com/RomanZavadaM/Taxo/actions/runs/42794764605) — SUCCESS; workflow на кожному виконує повний unittest discovery.
- Файл скану пов'язаний із записом за назвою; відкриття через інтерфейс і зв'язки документів ТЗ не перевірялись. Створення/відновлення копії — через функції, не через вікна. Тестові дані вигадані й тимчасові. Продуктова логіка, користувацькі дані та реліз не змінювались.

## 10.11.2026 — часткова карта персоналу, документів і графіка

- Досліджена база: `main 4e9e48b50ea464b6e3a7110c52e259d5df43df99`. Після перевірки: відкритих PR не виявлено; актуальний продукт 10.15-r3, stable v10.14-r4.
- Додано `docs/planning/FUNCTION_MAP_PERSONNEL_DOCUMENTS_SCHEDULE_2026-11-10.md`: частково простежено імпорт даних, картки, документи, вимоги, резервування вкладень і простий місячний графік; позначено наявні тести та невиконані перевірки.
- За статичним читанням контрольна ознака копії документа обчислюється за префіксом шляху без перевірки наявності файла в цій функції. Це ризик для практичного відтворення, не результат тесту і не твердження про всі екрани.
- Код і тести не запускалися; продукт, робочі дані та реліз не змінені. Далі — ізольований тест реалістичних вкладень та посилань і вікон backup/restore, включно з негативним випадком відсутнього файла.

## 10.11.2026 — ізольоване резервування / відновлення

- PR #296: карта `docs/planning/BACKUP_RESTORE_MAP_2026-11-10.md` і автоматичний тест `tests/test_synthetic_workspace_restore.py`. Вхідні дані вигадані, тимчасовий workspace і config задаються до імпорту. Продуктова логіка і схема не змінені.
- Тест створює реальним UI наказ з 12 парами, результати DOCX/PDF/JPG, окремі план і факт, документи інструктажу й стажування, основну і тахографічну БД та синтетичні файли вкладень. Після вибіркової повної копії і відновлення в порожнє сховище звіряє бази, пари, дані, індекс, DOCX/PDF, копії файлів і відмови. Зразки вкладень — контрольні байти, не справжні PDF/JPG; UI backup/restore і друк із відновленої БД ще не перевірені.
- Exact PR head `5284ec357f502993f302da39f00149c4a88a5e1d`: Windows [42790810896](https://github.com/RomanZavadaM/Taxo/actions/runs/42790810896), Win7 [42790811282](https://github.com/RomanZavadaM/Taxo/actions/runs/42790811282), macOS Intel/ARM [42790811050](https://github.com/RomanZavadaM/Taxo/actions/runs/42790811050) — SUCCESS; тест окремо знайдено в чотирьох журналах.
- Копія не містить необраних документів ТЗ, сканів або Output і навмисно виключає Backups/Logs. Продовжити карту персоналу, документів і графіків та підсилити тест відновлення відповідних посилань/інтерфейсу.

## 10.11.2026 — рішення власника та перша карта функцій

- База читання: `main f374b7b193466705a41bb3f60cb3d7a1ceff33c1`, продукт 10.15-r3; stable v10.14-r4. На початку роботи відкритих PR не виявлено.
- Власник погодив карту наявних сценаріїв з майбутнім розвитком і перевірку на ізольованому робочому сховищі. Перші напрями перенесення — накази та інструктажі, можливо окремими модулями. СТОІР окремо; акти ТО/робіт і запчастини/склад — майбутній розвиток. Каталог документів — спільний. Масовий перенос ядра та переписування міграцій на старті відкладено.
- Рішення зафіксовано в Issue #290: https://github.com/RomanZavadaM/Taxo/issues/290#issuecomment-6763545414 ; запис відновлення в Issue #61: https://github.com/RomanZavadaM/Taxo/issues/61#issuecomment-6763549967 .
- Складено першу частину карти `docs/planning/FUNCTION_MAP_ORDERS_INSTRUCTIONS_2026-11-10.md`: збереження, перегляд, друк, вибірковість резерву, зв'язки і наявні тести наказів/інструктажів; попередній індекс інших напрямів. Це **не повна карта Taxo**; код і тести під час складання не запускались. Продукт, база, версія, релізи не змінювались.
- Ризик для подальшої перевірки, не підтверджений дефект: вибір працівників інструктажу читається в момент збереження; перевірити втрату виділення. Окремо перевірити узгодженість файлів і початкового каталогу при збої.
- Наступна дія: доповнити карту/перевірки; створити ізольоване тестове сховище з вигаданими даними і перевірити вибраний повний backup/restore перед першим цілісним переносом наказового сценарію.

## 09.11.2026 — 10.15-r3 product merged, exact-main CI PASS, release checkpoint

- Owner rejected scattered CSV as a practical briefing archive, requested printable instruction text + signature sheet, and separate driver internship sheets.
- PR #292 merged into main: `eb71c64d3627ad3d02524b1735a1b53f155ec347`.
- New paperwork engine `paper_documents.py`, searchable Word list, full workspace path `Data/PaperDocuments`, backup regression and live feature routes.
- Driver internship UI based on driver/instructor/vehicle choices, printable field records for territory/route/control drive, paper-only signatures and admission decision.
- Updated README (Ukrainian), six translations, quick start, user manual, release index, product status, release notes.
- Exact PR-head Windows #1443, Windows 7 #417, macOS #1342 — SUCCESS.
- Exact product main Windows #1444, Windows 7 #418, macOS Intel+ARM #1343, START #2561 — **SUCCESS**. START source artifact #13706675051, 1 813 312 bytes.
- PR #293 merged → `d93ae63660abfeeeb8ee7298724288f75aea92dd`; existing publisher workflow #42690409737 SUCCESS → immutable [prerelease `v10.15-r3`](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r3) with 8/8 verified assets and SHA256; tag source exactly `eb71c64d3627ad3d02524b1735a1b53f155ec347`. Stable Latest remains v10.14-r4.
- Stable / Latest remains `v10.14-r4`; manual acceptance r3 pending.
- **Drive START recovery:** `Taxo_CURRENT_MAIN_v10.15-r3_2026-11-09_START.zip`, file `11T-KbkowXAVxKORUmDkl2VK6eq_-Txkt`, 1 813 312 bytes, SHA256 `6ec7ff84caf45822d9194905980d8f55faa16d92bfff99d36822ac1d5d8e20f1`; 640 ZIP entries, no nested ZIP, package check OK.

- Owner decision: independent read-only architecture audit required before module extraction for 2–3× future expansion, Issue #290; complete catalog with optional signed scans Issue #289.
- Next: finish release/backup verification, merge recovery checkpoint; no r4 code until checkpoint.

## 09.11.2026 — 10.14-r10 integrated: cold-start crash pack/grid

- Owner exact-main r9 START на Windows впав до робочого вікна з `_tkinter.TclError: cannot use geometry manager pack ... already has slaves managed by grid`.
- Traceback привів у `v1048_features.py` до кнопки «Реєстр “Шлях”».
- Підтверджено historical conflict: v1048 пакував registry actions у legacy vehicle toolbar, v1066 пізніше переводив core controls того самого parent на grid.
- Старий `test_v10_8_r1.py` знав про конфлікт, але перевіряв його наявність; regression змінено так, щоб конфлікт був заборонений.
- PR #283 merged → exact main `12d6ff9e49b9a9ac2753b29f63828531c66bd1c8`.
- Registry/TCC vehicle actions винесено в окрему панель «Реєстри та облік ТЗ».
- Додано справжній cold-start smoke в окремому процесі з ізольованим workspace; він відтворює startup order і не забруднює решту regression suite.
- Exact-main: START #2556, Windows #1413, Win7 #389, macOS #1314 — SUCCESS; 1039 tests OK; cold-start PASS.
- START artifact #13682040160, 1 760 098 B; SHA256 `a8304385abe5e120a5802872909eb2bd892adbbf3ef6a1bd678244929e21671b`.
- Drive: `Taxo_CURRENT_MAIN_v10.14-r10_2026-11-09_START.zip`, ID `13aUUhV1yGawzaqdrujn_emPqyK999cey`.
- Stable лишається v10.14-r4. Manual acceptance r10 pending. Next code revision: 10.15-r1.

## 09.11.2026 — 10.14-r5 integrated: appendix edit lock removed

- Recovery виконано за START_HERE/HANDOFF/private profile/live GitHub; stable v10.14-r4 підтверджено й не змінено.
- Експлуатаційна перевірка виявила один реальний залишковий дефект: додатки до наказів мали старе обмеження «лише чернетка».
- PR #273 merged → main `df7c9c6d001445fa2ea5d0b0cd12c20a04d0c5e6`.
- Додатки можна додавати/редагувати/видаляти незалежно від статусу наказу/паперового підпису; delete audit snapshot включає додатки.
- PR-head CI: Windows #1368, Win7 #344, macOS #1269, START #2418 — SUCCESS.
- Exact-main CI: Windows #1369, Win7 #345, macOS #1270, START #2419 — SUCCESS; 1023 tests OK.
- Exact-main START artifact #13668314757, 1 729 037 B; Drive backup `Taxo_CURRENT_MAIN_v10.14-r5_2026-11-09_START.zip`, ID `1EsQ5pdJUEP9Fge0_Hiw41qCvtaxCNF9q`.
- Issue #264 completed; старий audit #175 закрито як completed, щоб не дублювати виконану роботу.
- Manual operational acceptance r5 — pending; next code revision 10.14-r6.

## 09.11.2026 — stable 10.14-r4 опубліковано, підтверджено GitHub Latest

- Docs PR #270 merged, README українською + EN/DE/ES/FR/KO/JA, release index/notes, посібники і відновлення оновлено.
- Exact release source `214f714f4804cb284fdcbc5b5a26418cef40937a`, CI Windows #1364 / Win7 #341 / macOS #1266 / START #2404 SUCCESS.
- Protected marker PR #271 merged (skip old current publisher); historical promoter run #3 SUCCESS.
- Release https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4 ; 8/8 assets, SHA256, stable/latest; previous v10.12-r10 rollback.
- Drive stable folder містить macOS ARM/Intel і START; Windows backup artifact ZIP >100MB відхилено конектором. Повний комплект офіційно збережений у GitHub Releases.
- Наступна кодова ревізія 10.14-r5, не використовувати виданий r4 повторно.
## 09.11.2026 — схвалено стабільну 10.14-r4, синхронізація документації

Власник повідомив, що основні сценарії загалом працюють; дав пряму команду видати стабільну 10.14-r4 та оновити README українською і EN/DE/ES/FR/KO/JA, release index, release notes, посібники, product status, recovery docs. Перевірена кодова база 677458afa06893b4d221130db72de4045187e0c8 (PR #268), Windows #1357 / Win7 #337 / macOS #1262 / START #2402 PASS. Код і підтримувані бібліотеки не змінювали. Для immutable release ще треба stable marker workflow, 8 assets, SHA256, latest confirmation. Наступна кодова версія — 10.14-r5.
## 10.14-r4 — єдиний вигляд наказів Word / PDF / JPG — 09.11.2026

- **Інтегровано:** PR #268, точний product commit `677458afa06893b4d221130db72de4045187e0c8`. Stable/Latest лишається `v10.12-r10`, наступна кодова ревізія — `10.14-r5`.
- Виправлено розходження макета, яке показав власник на прикладі наказу №25. Замість простого тексту Word формує редаговані таблиці: дата/номер/місце, транспорт/номер/водій, підпис. Зміст і структуру основного наказу Word і два PDF-шляхи отримують зі спільного `order_layout.py` + `order_pdf_sections.py`. JPG візуально походить від PDF.
- Враховані **додатки та структуровані переліки**: Word отримує їх із бази, як PDF із додатками. Не вирізати з маршруту друку `v1073_features.py`.
- З вікна наказу «Перегляд DOCX» більше не показує оманливий простий текст: за наявності PDF цього сеансу відкривається друкований PDF; інакше файл відкривається у Word-сумісній програмі комп'ютера. Загальний спрощений viewer для інших документів Taxo не змінювали.
- **Без нових бібліотек і без змін ліцензій:** використовуються наявні python-docx, ReportLab, PDFium/Pillow. Не додано PyMuPDF.
- PR-head перевірки **PASS**: Windows #1356, Win7 #336, macOS #1261, START #2401, з тестами таблиць двох водіїв і тексту додатка. **Exact-main CI PASS:** Windows #1357, Win7 #337, macOS Intel/ARM #1262, START #2402 — усі SUCCESS.
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

## 10.13-r10 — видимий наказ і прямий друк — 08.11.2026

- Owner feedback після r9: помилки зникли, але готовий текст наказу та шлях до друку неочевидні.
- PR #258 merged → exact product `46ef1b995cfc42e8a3195d2f654ad0a9d5e07bb4`.
- Додано `order_preview_text()` та read-only **«Перегляд наказу»**: шапка, реквізити, тема, вступ, «НАКАЗУЮ», assignment rows, контроль, підписний блок.
- У реєстрі наказів є **«Переглянути / друк»**; double-click відкриває preview; у preview є **«Сформувати PDF / друк»**.
- Після створення наказу Taxo більше не ховає результат переходом на assignment tab: лишається на «Накази», виділяє створений запис і автоматично показує текст.
- Existing PDF generator не замінено; r10 робить його доступним із зрозумілого preview workflow.
- Новий regression перевіряє реальний текст наказу з кількома водіями та всі UI-входи.
- PR-head: Windows #1335 — **997 tests / OK**; Win7 #320 SUCCESS; macOS #1245 Intel/ARM SUCCESS.
- Exact-main: Windows #1336 — **997 tests / OK**; Win7 #321 SUCCESS; macOS #1246 Intel/ARM SUCCESS; START #2336 SUCCESS.
- Exact START: 1 699 549 bytes, SHA256 `9810df24b3a0ded29ec33ec8f804e18b29ef284853e47fe3763e22e994d2c0f3`.
- Google Drive recovery-copy: `Taxo_CURRENT_MAIN_v10.13-r10_2026-11-08_START.zip`, file `1F5-tTsEqlH6o8xdeSKdQcRBPbZ3k_iVs`; read-back PASS.
- Stable remains **v10.12-r10**. r10 integrated-only, owner manual-test candidate.
- Цикл 10.13 завершено по ревізіях; наступна code revision — **10.14-r1** після feedback.

## 10.13-r9 — виправлення після ручного тестування r8 — 08.11.2026

- Owner screenshots r8: raw SQLite duplicate error, crash `create_order_with_template(... order_series=...)`, нумерація непомітна у «Відповідальні», головне вікно не виходить на передній план.
- PR #256 merged → exact product `c0497c2679978f0936e1a36df3ad97c7244f8d12`.
- Legacy v1079 template wrapper тепер forwards `order_series`; створення наказу більше не падає на цьому параметрі.
- Duplicate assignment: single add/edit отримують human message; bulk add пропускає existing pairs і не валить нові.
- Реєстр наказів має пряму кнопку **«Нумерація наказів…»**; окремий видимий блок work/personnel next numbers пояснює продовження паперового журналу.
- Після повного старту root window одноразово deiconify/lift/topmost/focus і через 250 ms знімає topmost.
- Owner підтвердив fast-test policy: для функціонального приймання достатньо **START ZIP через START.bat**; Portable/installer — більші checkpoints/stable.
- PR-head: Windows #1332 — **993 tests / OK**; Win7 #318 — SUCCESS; macOS #1243 Intel/ARM — SUCCESS.
- Exact-main: Windows #1333 — **993 tests / OK**; Win7 #319 — SUCCESS; macOS #1244 Intel/ARM — SUCCESS; START #2335 — SUCCESS.
- Exact START: 1 691 957 bytes; SHA256 `83544cb6f0b5a1f34427051dfce11023f2861fd81fa0eb3d5051e95d2a3c201a`.
- Google Drive recovery-copy: `Taxo_CURRENT_MAIN_v10.13-r9_2026-11-08_START.zip`, file `1V1DNORZsku-LTl6UVqHlnfo5U5jFmJre`; read-back PASS.
- Stable remains **v10.12-r10**. r9 integrated-only, owner manual-test candidate. Next revision **10.13-r10** after feedback.

## 10.13-r8 — безпечне масове закріплення — 08.11.2026

- Після r7 self-audit виявлено: draft-helper допускав 1 водій→кілька ТЗ з одним validity window, але чинний approval invariant правильно блокує одночасне закріплення одного водія за різними ТЗ.
- PR #254 merged → exact product `78112c03db5406a2e4d9e4e4452226f6c9a82d0f`.
- r8 прибрав суперечливий режим ще до створення bulk pairs; UI теж більше його не показує як допустимий.
- Допустимі bulk modes: 1 ТЗ→кілька водіїв; equal N ТЗ↔N різних водіїв; одна пара.
- Behavioral regression проходить через реальний v10.9-r8 approval guard: допустимі схеми approve PASS; manual one-driver/many-vehicles conflict правильно rejected, order remains draft.
- Автонумерація r7 збережена без змін: work `1,2,3…`, personnel `1-К,2-К,3-К…`, configurable next number.
- PR-head: Windows #1328 — **987 tests / OK**; Win7 #314 — SUCCESS; macOS #1239 Intel/ARM — SUCCESS.
- Exact-main: Windows #1329 — **987 tests / OK**; Win7 #315 — SUCCESS; macOS #1240 Intel/ARM — SUCCESS; START #2333 — SUCCESS.
- Drive recovery-copy: `Taxo_CURRENT_MAIN_v10.13-r8_2026-11-08_START.zip`, 1 685 617 bytes, file `1rj63QCtxmw4laO1KOnoVlx2PJoNccb20`, SHA256 `19cc825561f367afaa84d75cbc621dbd4767aa8f7bf284bd1d60a1a5cc35b61f`.
- Windows Portable exact-main SHA256: `31f179abc8a6562a196d02168690d0f7888fec6c209592a1308129be650a7daa`.
- Stable remains **v10.12-r10**. r8 integrated-only and is the owner manual-test candidate. Next revision — **10.13-r9** only after feedback.

## 10.13-r7 — масові закріплення та автонумерація — 08.11.2026

- Owner feedback після r6: один наказ має охоплювати багато водіїв/ТЗ; накази потребують автонумерації, бажано окремо кадрові та робочі.
- PR #252 merged → exact product `4c90082aba0aa3f1c7f4636466ceaa08aa541ecf`.
- Додано bulk pairing у наказі про закріплення та «Додати багато…» у чернетці; single-pair сценарій збережено.
- Додано work/personnel numbering series, конфігурований next number, personnel suffix `-К`, legacy migration work-counter.
- Feature-loss gate двічі зловив старі UI contracts: legacy settings mocks без нових полів та точні labels r4; обидва виправлено без відмови від r7 функцій.
- PR-head: Windows #1320 — **981 tests / OK**; Win7 #306 — SUCCESS; macOS #1231 Intel/ARM — SUCCESS.
- Exact-main: Windows #1321 — **981 tests / OK**; Win7 #307 — SUCCESS; macOS #1232 Intel/ARM — SUCCESS; START #2331 — SUCCESS.
- Drive recovery-copy: `Taxo_CURRENT_MAIN_v10.13-r7_2026-11-08_START.zip`, 1 680 167 bytes, file `1lVmLFCqToh_9Bqhxrdd1e9Yuzz8Ol5r2`, SHA256 `09e0185d52dfbfd31c6745cf2afa31910be6a88645b18678eb95f683a8dbfea0`.
- Self-audit before owner delivery found semantic mismatch: helper permits 1 driver→many vehicles with same dates, but approval invariant correctly rejects one driver simultaneously on different vehicles. r7 is recovery-safe but **not the package to hand to owner**; next revision r8 must reject this mode at selection time and add approval regression.
- Stable remains **v10.12-r10**.

## 10.13-r6 — структуровані працівники й ТЗ у наказах — 08.11.2026

- Після r5 shared-selector foundation реалізовано другий етап Issue #246: **персистентні structured links** працівників/ТЗ до наказу з frozen snapshot реквізитів.
- PR #249 merged → exact product `a3f4e7e924f8d4c7389b28dc659c2f1e72e210da`.
- Additive schema: `operations_order_entities(order_id, entity_type, entity_id, role, snapshot_json, sequence_no, note, timestamps)`; існуючі накази/дані не переписуються.
- UI: окрема вкладка **«Учасники / ТЗ»**, mass-select, пошук за ПІБ/табельним №/ідентифікатором, держномером/VIN; роль і примітка для вибраної групи.
- Driver-specific order types використовують driver-only employee pool; vehicle-assignment order лишається на спеціалізованій моделі `vehicle_driver_assignments`.
- Frozen snapshot: зміна ПІБ/табельного №/RNOKPP або держномера/make-model/VIN у живій картці після додавання не переписує документний перелік.
- Privacy: RNOKPP доступний для ідентифікації/пошуку, але PDF автоматично друкує табельний №/Taxo ID, не повний RNOKPP; для ТЗ — VIN.
- Після введення наказу в дію структурований перелік immutable; inactive сутності не можна додати до нового наказу.
- Історія add/remove прив'язана до order_id, тому видалений зі чернетки рядок не зникає з історії наказу.
- PDF runtime layer `v1073_features.py` друкує окрему сторінку **«Структурований перелік працівників і транспортних засобів»** із frozen snapshot.
- r6 regression suite: +12 тестів; PR-head Windows #1312 — **972 tests / OK**; Win7 #298 — SUCCESS; macOS #1223 Intel/ARM — SUCCESS. Перший ARM job впав до checkout через зламаний manifest стандартного `actions/checkout`; конкретний failed job повторено без зміни коду — SUCCESS.
- Exact-main: Windows #1313 — **972 tests / OK**; Win7 #299 — SUCCESS; macOS #1224 Intel/ARM — SUCCESS; START #2329 — SUCCESS.
- Exact START artifact: 1 669 795 байт, SHA256 `6b362f065190b708f27c11cb1f8d08cd70fe57a9b2d5e72d0b2b247736392e36`.
- Google Drive recovery-copy: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r6_2026-11-08_START.zip`, Drive file `1MXbWM_ppcKBGhRRtPJtq8V1Y226_4YKK`; read-back підтверджений.
- Stable не змінювалась: **v10.12-r10**. r6 integrated-only. Наступна code revision — **10.13-r7** після ручного приймання.

## 10.13-r5 — спільний вибір працівників, водіїв і ТЗ — 08.11.2026

- Вимога власника: у багатьох наказах та інструктажах не переписувати людей/транспорт руками, а вибирати конкретні записи бази з однозначними реквізитами; зафіксовано Issue #246 і зв'язок з Issue #237.
- Від exact r4 checkpoint `f0521691...` створено r5; PR #247 merged → exact product `0b6e0b99dedcfcdbfe25df1460f483d197e623c9`.
- Додано спільний `entity_choices.py`; старі окремі employee/driver/vehicle selector-и в Operations переведено на один контракт.
- Працівник: stable Taxo ID, ПІБ, табельний №, посада, RNOKPP/registry ID для точного зіставлення. Повний RNOKPP не друкується автоматично; за відсутності табельного № UI показує лише маскований хвіст.
- Водії: driver-only фільтрація спільної employee-моделі; inactive не пропонуються для нового документа, historical режим їх не губить.
- ТЗ: stable Taxo ID, держномер, make/model, VIN, garage №; новий вибір показує VIN і підтримує пошук за ним.
- «Інструктажі та журнали» переведено на structured employee choice; підготовчий CSV містить ПІБ, табельний №, Код Taxo й надалі **не є журналом/підтвердженням проведення**.
- Choice records містять snapshot ідентифікаційних реквізитів як основу наступного кроку; персистентний historical snapshot для багатьох типів наказів ще не реалізований.
- Нові r5 regression checks: однакові ПІБ, табельний №/RNOKPP/registry ID, driver-only, VIN/plate, active/historical, CSV privacy, VERSION/START identity.
- PR-head: Windows #1308 — **960 tests / OK**; Win7 #294 — SUCCESS; macOS #1219 Intel/ARM — SUCCESS.
- Exact-main після merge: Windows #1309 — **960 tests / OK**; Win7 #295 — SUCCESS; macOS #1220 Intel/ARM — SUCCESS; START #2327 — SUCCESS.
- Exact START artifact: 1 656 837 байт, SHA256 `c4d3f8cdbfa1d6c911f74bddc6682f18dc71a55699896ffbc5142d14c1c37107`.
- Google Drive recovery-copy: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r5_2026-11-08_START.zip`, file `12xjT-MYyacorZVroEesvEicwR7Z17nPP`; read-back підтверджений.
- Stable не змінювалась: **v10.12-r10**. r5 integrated-only. Наступна code revision — **10.13-r6** після ручного приймання.

## 10.13-r4 — наказ про закріплення: водій і ТЗ з бази — 08.11.2026

- Після команди власника на вибір водіїв/транспорту виконано reconciliation: паралельна сесія вже інтегрувала PR #244; дублюючу кодову роботу не починали.
- Exact product commit: `67b4670fdb29a46d03f9d6462ae2bd19603a2a5c`; VERSION = 10.13-r4.
- `list_driver_choices()` відбирає фактичних водіїв через `employee_roles` і зв'язок `employees.driver_id → drivers`; механіки/диспетчери не потрапляють у новий список водіїв.
- У створенні наказу про закріплення є active ТЗ + active driver selectors і можливість одразу записати першу пару.
- Неповна пара блокується; порожня пара зберігає legacy draft workflow.
- Вкладка «Закріплення водіїв» також використовує driver-only choices для нових рядків; історичне редагування дозволяє старі записи.
- Exact-product checks: Windows #1305 — **953 tests / OK**; Win7 #291; macOS #1216 ARM64/Intel; START #2325 — SUCCESS.
- START artifact #13591576959, SHA256 `6fd45b64748df00506dcae1420d48db5959f847f1e884d3040b0f0eb6eea4555`.
- Drive recovery-copy: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r4_2026-11-07_START.zip`, file `1_861lkkVbBzhxiBlDbhKexG2jLcE6WAN`, 1 648 645 bytes, private readback PASS.
- Stable remains `v10.12-r10`; r4 integrated-only.
- Next code revision = **10.13-r5**, after owner manual acceptance.

## Exact-product closure 10.13-r3 — 07.11.2026

- PR #239 integration exact product SHA `a7b13a920302fb1dbfb441bf6ba097953cc3f71b`.
- Post-merge gates: Windows #42414412641 SUCCESS, Win7 #42414412482 SUCCESS, macOS #42414412631 ARM64/Intel SUCCESS, START #42414412635 SUCCESS.
- START artifact #13591181251, name `Taxo_v10_13_candidate_r3_START`, 584 files, 1 636 456 bytes, SHA256 `5ec905fa91289a369ccde51a2cc3bd6bbc3a5232371e0b0185274f8b1f3a66d2`.
- Drive recovery-copy підтверджено: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r3_2026-11-07_START.zip`, file `1F8R4-qUukZQr86iaBp2PWSuvGow43Gnn`.
- Stable `v10.12-r10` не змінено. 10.13-r3 integrated-only + START for manual owner acceptance, no separate release tag; next code revision 10.13-r4.

## 10.13-r3 — інструктажі БДР/ОП, перший паперовий підготовчий екран — 07.11.2026

- Звірено нормативні вимоги: БДР наказ №975 (види інструктажів, строки затверджує керівник, сезонні події), ОП НПАОП 0.00-4.12-05 (повторні інструктажі 3/6 міс залежно від робіт). Квартал не підміняє нормативний строк.
- Рішення власника: проведення й підпис на папері веде інженер; Taxo не займається підписанням.
- Планові документи: Issue #237, docs/planning/INSTRUCTION_JOURNALS_FOUNDATION_2026-11-07.md. PR #236 закрито через base drift; #238 — документаційна інтеграція після r3.
- PR #239: нова видима вкладка, валідований вибір БДР/ОП, виду, дати, теми, підстави, чинних працівників; допоміжний CSV без перезапису й фіктивних підписів. БД/схема/план-факт/stable не змінені.
- PR-head: Windows #42414118500 SUCCESS; Win7 #42414118532 SUCCESS; macOS #42414118493 (Intel/ARM) SUCCESS. Тести додано, старі маршрути наказів і СТОІР збережено.
- PR #239 merged → exact product SHA a7b13a920302fb1dbfb441bf6ba097953cc3f71b.
- Post-merge exact START/r3 recovery-copy ще окремо перевірити. Наступна кодова ревізія 10.13-r4.

## 10.13-r2 — Експлуатація / СТОІР presentation/usability — 07.11.2026

- Recovery виконано строго за START_HERE → HANDOFF_CURRENT → private profile/taxo → live GitHub → PROJECT_STATE; перед кодом перечитано методологію dev-strategy.
- Повторний UX-аудит r1: hidden double-click у «Стан автопарку», сирі STO/REPAIR/source_type/ISO dates, 7 order actions в один ряд, неочевидний старт нового наказу.
- PR #232; final PR head `1b3d846a99dcb2c275562421fb5baabe61504f7e`.
- Додано «Відкрити вибране ТЗ», human labels/dates, «Оформити новий наказ…», responsive action grids.
- Перший head `ea676a3...` замінив legacy «Каталог типів наказів»; historical live gate r7 правильно зупинив macOS CI. Product logic не ламалась. Старий маршрут відновлено, новий додано поруч.
- Фінальний PR-head: Windows #1287 — **941 tests / OK**; Win7 #278; macOS #1203 ARM64/Intel — SUCCESS.
- PR #232 merged → exact product commit `c6a2ad85b37019ab96fa32a0e597b625aea4815f`.
- Exact-product checks: Windows #1288 — **941 tests / OK**; Win7 #279; macOS #1204 ARM64/Intel; START #2321 — SUCCESS.
- START artifact ID `13589299601`, SHA256 `b8fccfebbb906ed86854ba47a21f77d6884de9232594e16238bdaff0245223f0`.
- Drive backup: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r2_2026-11-07_START.zip`; file `1f5z-jgnDwTEFSSexxoKA14G5mykUW1GV`; size 1 624 847 bytes; private readback PASS.
- Stable remains **v10.12-r10**; 10.13-r2 integrated-only.
- Next code revision: **10.13-r3**, only after owner manual acceptance of r2.

## Stable promotion — Taxo 10.12-r10 — 07.11.2026

- Owner command: оновити stable до 10.12; interpreted as completed line endpoint **10.12-r10**.
- Stable exact product source: `6d0f32bc45323d4085bb165b2ec050dae7b378ee`.
- Existing r10 gates reused: Windows #1269, Win7 #262, macOS #1187 ARM64/Intel, START #2315 — SUCCESS; PR-head Windows **931 tests / OK**; owner manual acceptance — без блокера.
- r10 had not previously been published, while main already contained 10.13-r1. To avoid moving main backward or releasing 10.13 by mistake, added guarded exact historical stable promoter.
- PR #229 merged with `[skip-publish]`: normal current publisher #18 correctly skipped; first historical promoter #42408835080 failed **before tag/release creation** on shell SIGPIPE/pipefail.
- PR #230 fixed only pipe handling; no release gate weakened.
- Historical stable promoter #42409237532 — **SUCCESS**.
- GitHub release `v10.12-r10`: prerelease=false, draft=false, **Latest**, exact tag target `6d0f32bc...`, 8 canonical assets.
- `.release/stable-current` = `10.12-r10`.
- Previous stable `v10.10-r5` remains rollback. Current main product 10.13-r1 remains integrated-only, not stable.
- Next code revision remains **10.13-r2**, after manual acceptance of 10.13-r1.

## 10.13-r1 — Експлуатація / СТОІР usability consolidation — 07.11.2026

- Recovery виконано за START_HERE → HANDOFF_CURRENT → private profile/taxo → live GitHub → PROJECT_STATE; Issue #61/#164/#175 звірені.
- Перед кодом повторно прочитано PRINCIPLES / METHODOLOGY / QUALITY_AND_RELEASES / CONTINUITY / AI_COLLABORATION / GOVERNANCE; застосовано новий mandatory Functional Loss Prevention rule.
- Підтверджено не косметичний, а структурний UX-розрив: Operations/STOIR були сусідніми системами; STOIR profile не мав UI; maintenance event не питав performer/notes; repair request закривався без result; orders UI не відповідав актуальній immutability-моделі.
- PR #227 створено від main `992de59bbb471f95740a46033873e4c38dc4d153`; фінальний PR head `f4ee7315eaef4237553055d480f0bdc7914e33d4`.
- СТОІР перетворено на workflow «стан автопарку → ТЗ → профіль ТО → факт ТО/ремонту → заявка → у роботу → закрити з результатом»; ОТК має прямий шлях до документів ТЗ.
- «Експлуатація → Документи» стала робочим столом із прямим STOIR-route; старі входи не видалені.
- Накази отримали старт «Що потрібно оформити?», чітке «Ввести в дію в Taxo» окремо від паперового підписання, history UI, early immutability guard і draft-only cancellation.
- Historical compatibility contract для групи «Операційні документи» збережено після окремої pre-CI звірки.
- PR-head gates: Windows #1274 — **936 tests / OK**; Win7 #265 — SUCCESS; macOS #1190 ARM64/Intel — SUCCESS.
- PR #227 merged → exact product commit `4ed9530b57a4e67fdca49c81da43602df074ebb0`.
- Exact-product gates: Windows #1275 — SUCCESS; Win7 #266 — SUCCESS; macOS #1191 ARM64/Intel — SUCCESS; START #2316 — SUCCESS.
- Exact-source START artifact #13588245649: 1 613 547 байт; SHA256 `11780cd318c419b52b8316e2c1fbb0c36d2b6877f738130250993dfac84eec38`.
- Google Drive recovery-copy: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r1_2026-11-07_START.zip`; Drive file `1XCfHkCdQUv8r0B0YyA3S2fCUsA126Z8F`.
- Stable лишається `v10.10-r5`; last published candidate — `v10.11-r10`; 10.13-r1 integrated-only.
- Наступний code revision — **10.13-r2**, але спочатку ручне приймання власником r1.

## 10.12-r10 — «План → факт» live reachability — 07.11.2026

- Recovery виконано строго: START_HERE → HANDOFF_CURRENT → private Taxo profile → live GitHub → PROJECT_STATE; Issue #61/#164/#175 звірені до змін.
- Preflight: main `4d1023c04a341379fa12549ede07292df977db27`, open PR = 0, `v10.12-r10`/r10 branch відсутні, stable `v10.10-r5`, published candidate `v10.11-r10`.
- PR #224 створено як один вузький Feature Loss slice від актуального main.
- Продуктову логіку «План → факт» не переписували; захист наявного факту лишається виправленням 10.11-r3.
- Додано live Tk regression на тимчасовій SQLite-БД: тест відкриває табель, щоденну вкладку, вибирає дві дати й натискає реальну кнопку «План → факт».
- Behavioral assertion: день без факту отримує план як факт; день із підтвердженим фактом лишається незмінним; planned_hours і notes не переписуються.
- Function registry позначає `timesheet.plan_to_fact` як runtime-smoke; після r10 усі 23 критичні routes мають runtime-smoke requirement.
- Фінальний PR head `8da128be181ea7b01a7d4927c4c5236a3966109a`: Windows #1268 — **931 tests / OK**; Win7 #261 — SUCCESS; macOS #1186 ARM64/Intel — SUCCESS.
- PR #224 merged → product main `6d0f32bc45323d4085bb165b2ec050dae7b378ee`.
- Post-merge exact-product checks: Windows #1269 — SUCCESS; Win7 #262 — SUCCESS; macOS #1187 ARM64/Intel — SUCCESS; START #2315 — SUCCESS.
- Google Drive recovery-copy підтверджена: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.12-r10_2026-11-07_START.zip`, 1 598 952 байти; джерело — exact-product START #2315 artifact, SHA256 `395834c0c2247129d280fb08bff5cb7c27ac118cfc1d6ceae67092d413f0afa3`.
- Stable лишається `v10.10-r5`; останній published candidate — `v10.11-r10`; 10.12-r1…r10 integrated-only.
- Feature Loss reachability cycle 10.12-r1…r10 завершено. Наступний номер code revision — **10.13-r1**; великий UX cleanup автоматично не починати.

## CI maintenance — process-only — 07.11.2026

- Recovery виконано строго: START_HERE → HANDOFF → private Taxo profile → live GitHub → PROJECT_STATE.
- Старі draft PR #142/#152 використані лише як історична довідка; replacement створено чисто від main `387b909bdabfa5df1a4a08d859f2993632a05db5`.
- PR #220 інтегровано як `894fdbb235b2b91c2bb334b8fadfb99566671fc9`; `VERSION.txt` лишився 10.12-r9, `publish-current.yml` не змінено.
- Superseded-run cancellation підтверджено live: старі Windows #1262 / Win7 #258 скасовані після нового PR head; macOS попереднього head також перервано.
- Фінальний PR #220 head `0db456281f84f22d62e55b599b66abc35edc1be2`: Windows #1263, Win7 #259, macOS #1184 ARM64/Intel — SUCCESS.
- Branch rules окремо звірено: `main` і далі вимагає exact status `build-windows`.
- Docs-only smoke #221: тільки Windows #1264 — SUCCESS; heavy regression/packaging steps skipped; Win7/macOS не стартували; PR закрито без merge.
- Workflow-sensitive post-merge #220: Windows #1265, Win7 #260, macOS #1185, START #2314 — SUCCESS; publisher не стартував.
- Post-merge docs-only PR #222: тільки lightweight Windows #1266 — SUCCESS. Після merge commit `bc32daa1b63c20aa4398fa35262d32456b62088c` отримав 0 Actions runs — platform/START/publisher не запускались.
- Після повної перевірки PR #142 і #152 закриті як superseded.
- Наступна кодова ревізія — **10.12-r10**: окремий live gate «План → факт» з обережною перевіркою зміни фактичних даних. Великий UX cleanup не починати.
## 10.12-r9 — «Водії для звіту…» reachability — 07.11.2026

- Recovery виконано за START_HERE → HANDOFF → private Taxo profile → live GitHub → PROJECT_STATE.
- Із двох залишкових маршрутів Feature Loss Audit першим обрано «Водії для звіту…»: це report-only маршрут без зміни plan/fact або БД. «План → факт» залишено окремим наступним кодовим slice.
- PR #218 створено чисто від main `49d19e47fd53d6709bf94f81b2602983c065301f`.
- Додано live Tk gate: кнопка «Водії для звіту…» видима, відкриває selector, список водіїв формується, дія «Застосувати» доступна.
- Function registry тепер вимагає runtime-smoke для `drivers.report_selection`.
- Перший test-harness на head `a5800066` помилково шукав popup лише серед прямих children root; macOS ARM64 правильно зафіксував 1 test failure. Продуктовий код не змінювався; harness виправлено рекурсивним пошуком.
- Фінальний head `08a2ef6d1c80d94c5fa6b124d1ef7986272a1196`: Windows #42394538014 — **923 tests / OK**; Win7 #42394537977 — SUCCESS; macOS ARM64/Intel #42394537997 — SUCCESS.
- PR #218 merged → main `a445f01d1d1c00408ee3f064088de4ddc1637c86`.
- Stable лишається `v10.10-r5`; останній published candidate — `v10.11-r10`; 10.12-r1…r9 integrated-only.
- Під час виправлення test-harness фактично підтверджено зайві Actions: runs попереднього PR head продовжили виконання після нового commit, одночасно стартували нові runs.
- CI maintenance не змішано з r9. Наступний process-only етап: чистий актуальний CI PR від нового main; PR #142/#152 використовувати лише як довідку і після replacement закрити як superseded.
- Наступна кодова ревізія після CI maintenance — **10.12-r10**, вузький live gate для «План → факт».

## 10.12-r8 — головна навігація — 07.11.2026

- Після recovery завершено docs-checkpoint r7: PR #215 merged; під час перевірки виправлено застарілі next-version markers.
- Старий PR #211 закрито як superseded, бо був створений як r7 від старої бази.
- PR #216 створено чисто від актуального main як 10.12-r8.
- Додано live UI gate для «Тахограф», «Звіти», «Налаштування» і runtime-smoke markers у function registry.
- Перший test harness зависав у Tk event-loop; другий варіант завершувався, але Windows показав unmapped control. Обидві проблеми були лише в тесті й виправлені без зміни продуктового коду.
- Фінальний PR head `6b01f4068dd83a58f98b801186f363bce8601b20`: Windows #42362821426 — **920 tests / OK**; Win7 #42362821600 — SUCCESS; macOS ARM64/Intel #42362821506 — SUCCESS.
- PR #216 merged → main `30d53a2d62b7622e5ed6601aa951676aaf9697c7`.
- Stable лишається `v10.10-r5`; останній published candidate — `v10.11-r10`; 10.12-r1…r8 integrated-only.
- Наступна кодова ревізія — **10.12-r9**. Наступний вузький Feature Loss slice: «Водії для звіту…» + «План → факт» (або один із них окремо, якщо обсяг виявиться більшим).

## 10.12-r7 — Центр документів — 07.11.2026

- PR #214 інтегровано в main: `232d7b54fd8aea61883acece2063741ea477bb0c`.
- Додано живу перевірку, що Центр документів реально з'являється у «Експлуатації».
- Перевіряються 4 основні зовнішні дії та 4 внутрішні переходи; повторне відкриття не дублює вкладку.
- Перший PR #213 був повністю зелений, але після docs-checkpoint base main змінився; згідно з repository rules зміни перебазовано на актуальний main у PR #214 і перевірено повторно.
- Windows #42359978858 — **917 tests / OK**; Win7 #42359978957 — SUCCESS; macOS ARM64/Intel #42359978856 — SUCCESS.
- Stable лишається `v10.10-r5`; останній виданий candidate — `v10.11-r10`.
- 10.12-r1…r7 інтегровані, але ще не публікувались як prerelease.
- Наступна ревізія — **10.12-r8**; продовження після recovery у новому чаті.

## 10.12-r5 → r6 — завершення історично ламких маршрутів — 07.11.2026

- **10.12-r5 / PR #209:** додано живу перевірку прапорця перепланування персоналу на мінімальному розмірі вікна та всіх 9 дій шляхівок у вузькому layout. Windows #42355574911, Win7 #42355574884, macOS #42355574889 — SUCCESS.
- **10.12-r6 / PR #210:** додано живу перевірку всіх 8 основних дій усередині «Дані / Дія / документи…». Windows #42356061719, Win7 #42356061533, macOS #42356061548 — SUCCESS.
- Current main: `e1bdcd5b827b2da78093323ee7fcdc48e5ac5eb0`.
- Stable лишається `v10.10-r5`; останній виданий candidate — `v10.11-r10`.
- 10.12-r1…r6 інтегровані, але ще не опубліковані як prerelease.
- Наступна ревізія — **10.12-r7**; мета — завершити runtime-перевірку решти критичних маршрутів реєстру.

# WORKLOG — Taxo

## 09.11.2026 — 10.15-r1: реальна БД показала втрату пар під час створення наказу

- Власник передав копію робочої `driver_worktime.sqlite3`; перевірка виконувалась лише локально на копії.
- SQLite integrity — OK. Наказ №27 містить 12 закріплень; наступний №28 створився без жодного закріплення. Після створення №28 assignment-create записів немає.
- Це відкинуло версію про втрату лише в Preview/DOCX/PDF: для №28 пари не дійшли до БД.
- Старий create-flow читав `Listbox.curselection()` у момент натискання «Створити». r1 замінив цей крихкий стан на видимі staged pairs.
- На копії реальної БД: 12×12 вибір → staged pairs → selection штучно очищено → «Створити» → усі 12 пар збережені й видимі у Preview.
- Постійний regression `test_v10_15_r1.py` повторює сценарій і перевіряє справжні DOCX/PDF/JPG та reopen.
- PR #286 → exact main `825a1994984aec6b47ce08224f2969735ee27d47`.
- Exact-main START #2559, Windows #1418, Win7 #394, macOS #1319 — SUCCESS; Windows 1041 tests / OK.
- START artifact #13695956407, 1 766 785 bytes, SHA256 `143cd4a662f4596e727d75a998944e4f6c3f1cd66d113756e64b48fc6bc1d054`.
- Drive recovery-copy: `Taxo_CURRENT_MAIN_v10.15-r1_2026-11-09_START.zip`, ID `1EwYuyv7nATjfmnDCQcpQVU9U-XRy9xZl`.
- Stable лишається v10.14-r4. Наступна кодова ревізія — 10.15-r2 після ручного приймання r1.

## 10.12-r4 — вкладені UI-маршрути — 07.11.2026

- Продовжено Feature Loss hardening без зміни бізнес-логіки.
- PR #207 додав реальну перевірку видимості/відкриття «Експлуатації» та вкладеної «Відомість (додаток 1)».
- Реєстр критичних функцій тепер вимагає живий UI-smoke для вкладеної військово-транспортної відомості.
- PR-head Windows #42354870979 — **907 tests / OK**; Win7 #42354871043 — full CPython 3.8 SUCCESS; macOS #42354870938 — ARM64/Intel SUCCESS.
- PR #207 merged → main `816e386647575763074e9106b6f75ef431fadcb9`.
- Наступна ревізія — **10.12-r5**; пріоритет — історично ламкі layout-контроли: прапорець перепланування та 9 дій шляхівок.

## 10.12-r1 → r3 — Feature Loss Audit і захист досяжності функцій — 07.11.2026

- Власник повідомив, що прийнятий раніше «Простий місячний графік…» з вибором працівників зник із Personnel UI. Аналіз підтвердив: код, мультивибір і PDF/XLSX лишались, але UI-entry додавався крихким runtime-injector.
- **10.12-r1 / PR #202:** дія перенесена у штатний `Працівники → Планування`; injector лишено лише fallback.
- Проведено ретроспективний Feature Loss Audit від stable `v10.10-r5` до current line. Підтверджено історичний аналогічний інцидент 10.8-r1 із vehicle core actions; знайдено історично ламкі controls/layouts і dynamic routes.
- PR #203 додав `FEATURE_LOSS_AUDIT_2026-11-06.md` та `FUNCTION_REGISTRY_DRAFT.md`.
- Виявлено, що до цієї роботи майже весь UI regression suite був source/static; реальний `winfo_ismapped()` + callback smoke фактично існував тільки для vehicle core toolbar.
- **10.12-r2 / PR #204:** додано executable `src/taxo/function_registry.py` і cross-platform Tk reachability smoke. Під час розробки test harness окремо адаптовано до macOS Label navigation та Windows Tk mapping lifecycle; product logic не змінювалась.
- Фінальний r2 gate: Windows #42352276336 SUCCESS; Win7 #42352276288 SUCCESS (full CPython 3.8); macOS #42352276292 SUCCESS.
- Аудит знайшов cascade-risk у Personnel Data Center: historical buttons ховались до перевірки, що replacement route вдалося створити.
- **10.12-r3 / PR #205:** `Дані / Дія / документи…` став постійним Personnel action; legacy buttons ховаються тільки після гарантії replacement; missing-anchor залишає старі routes доступними.
- r3 runtime regression покриває permanent / compatibility fallback / missing-anchor. PR-head Windows #42352755797 — **903 tests / OK**; Win7 #42352755837 SUCCESS; macOS #42352755821 SUCCESS.
- PR #205 merged; current main = `28a84c9b44c7ac526acb09c6258e227d760cc762`.
- Stable лишається `v10.10-r5`; останній **виданий** candidate лишається `v10.11-r10`. 10.12-r1/r2/r3 не публікувались.
- Наступна кодова ревізія — **10.12-r4**. Наступний slice не змішувати з великим UX cleanup; пріоритет — подальший runtime reachability gate за Issue #164.


## 10.11-r9 — immutable GitHub Action pins та офіційний prerelease — 06.11.2026

- Окремий workflow supply-chain hardening slice за Issue #175 finding #11; runtime/business logic, UX #164, build naming і CI optimization #142/#152 не змішувались.
- 06.11.2026 звірено current official major refs GitHub: `actions/checkout@v4 → 11d5960a326750d5838078e36cf38b85af677262`; `actions/setup-python@v5 → a26af69be951a213d495a4c3e4e4022e16d87065`; `actions/upload-artifact@v4 → ea165f8d65b6e75b540449e92b4886f43607fa02`.
- П'ять active workflows переведені з рухомих `@v4/@v5` на ці immutable commit SHA з human-readable коментарем major line. Historical workflows не переписувались.
- Додано `tests/test_v10_11_r9.py`: 40-char SHA requirement, exact allowlist, заборона moving major refs, збереження maintenance comments.
- r8 exact-current regression переведений на historical anchor, щоб не блокувати наступні ревізії.
- PR #195 head `371f63d3b8955cc697cf612f1bca3f4c23b64467`: Windows #42285971115, Win7 #42285971130, macOS #42285971196 — SUCCESS; CI фактично виконував pinned checkout по SHA.
- PR #195 merged; exact issued source / exact-main = `8f97218927b3ba6bc14aca465de4a196e2b19ba2`.
- Exact-main SUCCESS: START #42286505119 — **885 tests / OK**; Windows #42286505164; Windows 7 #42286505171 (full CPython 3.8 regression); macOS ARM64/Intel #42286505215.
- Автоматичний publisher після merge PR #195 безпечно зупинився на immutable r8 overwrite guard; release не змінено.
- Release-trigger PR #196 merged; trigger main `14d6a615f06ebb23254c46ef291c34f0f9fcc795`.
- Publisher #42287707654 — **SUCCESS**. Опубліковано immutable prerelease `v10.11-r9`; tag target = `8f97218927b3ba6bc14aca465de4a196e2b19ba2`; 8 assets, усі r9. Stable/Latest лишається `v10.10-r5`.
- Google Drive підтверджено: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r9_2026-11-06_START.zip`, 1 542 152 байт.
- Наступна кодова ревізія — **10.11-r10**. Перед новим кодом повторно звірити Issue #175 та UX Issue #164; не починати великий cleanup автоматично.

## 10.11-r8 — централізоване build/release naming та офіційний prerelease — 06.11.2026

- Окремий release-engineering slice за Issue #175 finding #10; runtime/business logic, UX #164, supply-chain action pinning і CI optimization #142/#152 не змішувались.
- `src/taxo/release_naming.py` розширено canonical helpers для `TAXO_VERSION`, `TAXO_CANDIDATE_STEM`, `TAXO_CHECKSUM_STEM`, що читаються з `VERSION.txt`.
- Active Windows, Win7 і macOS workflows більше не містять revision-specific r7 package names; Portable/Setup/checksum назви формуються з canonical tokens.
- `packaging/installer/Taxo.iss` більше не має hardcoded revision defaults: `MyAppVersion`, `SourceBundle`, `OutputBase` обов'язково передає workflow.
- promotion-to-stable у `publish-current.yml` формує required 8-asset list із marker/version, а не з hardcoded `v10.10-r5`.
- Перший r8 CI виявив test-only exact-version lock у r7 regression; переведено на historical anchor. Другий прогін виявив PowerShell interpolation `$env:TAXO_CANDIDATE_STEM_Windows_x64`; виправлено на braced env-variable syntax. Runtime не змінювався.
- Фінальний PR #192 head `0ba61c0f397af9f4dbc2ceefb02101c68b61aec5`: Windows #42282648349, Win7 #42282648375, macOS #42282648592 — SUCCESS. Artifact ZIP вручну перевірені: файли мають саме r8 names.
- PR #192 merged; exact issued source / exact-main = `f3e846c50e75bdc59560d10916cec90a7587cdac`.
- Exact-main SUCCESS: START #42283491422 — **881 tests / OK**; Windows #42283491587; Windows 7 #42283491399; macOS ARM64/Intel #42283491541.
- Автоматичний publisher на merge PR #192 безпечно зупинився на immutable r7 overwrite guard; release не змінено.
- Release-trigger PR #193 merged; trigger main `cbe1e06552dc94ae78519072b3a2e57fb1ec25e3`.
- Publisher #42284631762 — **SUCCESS**. Опубліковано immutable prerelease `v10.11-r8`; tag target = `f3e846c50e75bdc59560d10916cec90a7587cdac`; 8 assets, усі r8. Stable/Latest лишається `v10.10-r5`.
- Google Drive підтверджено: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r8_2026-11-06_START.zip`, 1 538 476 байт.
- Наступна кодова ревізія — **10.11-r9**. Наступний окремий finding Issue #175 — workflow supply-chain hardening.

## 10.11-r7 — повний Win7 regression gate та офіційний prerelease — 06.11.2026

- Окремий CI hardening-slice за Issue #175; UX #164, supply-chain hardening і CI optimization #142/#152 не змішувались.
- До r7 Win7 workflow запускав лише `test_v10_11_r5` і `test_v10_11_r6`. У r7 він запускає весь `python -m unittest discover -s tests -v` на реальному CPython 3.8.10 **до** PyInstaller packaging.
- Перший повний Win7 прогін виявив 129 помилок через відсутність legacy root-layout. Додано `python tests/stage_legacy_layout.py` перед suite — той самий механізм, який уже використовують Windows/macOS.
- Після staging залишилися лише test-only несумісності Python 3.8: три історичні тести використовували `str.removeprefix()`, а r6-тест помилково фіксував r6 як вічно поточну версію. Контракти виправлено без зміни runtime.
- Додано `tests/test_v10_11_r7.py`, який фіксує порядок: compile → legacy staging → full suite → packaging і забороняє повернення до вузького r5/r6-only gate.
- PR #188 фінальний head `284f0694971ddb5cff33ee91b5756362b18a6faa`: Windows #42272564664, Win7 #42272564632, macOS #42272564625 — SUCCESS; Win7 повний Python 3.8 suite — SUCCESS.
- PR #188 merged; exact issued source / exact-main = `3f3b28366ce7d453a70f5a2573eb676c0b503d2c`.
- Exact-main SUCCESS: START #42273303324 — **876 tests / OK**; Windows #42273303147; Windows 7 #42273303116 (full CPython 3.8.10 regression before packaging); macOS ARM64/Intel #42273303128.
- Release-trigger PR #189 merged; trigger main `0192e9c083c4a92ca6c5b9ec8b2df0609fce9dd9`.
- Publisher #42274663207 — **SUCCESS**. Опубліковано immutable prerelease `v10.11-r7`; tag target = `3f3b28366ce7d453a70f5a2573eb676c0b503d2c`; 8 assets, усі r7. Stable/Latest лишається `v10.10-r5`.
- Google Drive підтверджено: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r7_2026-11-06_START.zip`, 1 534 531 байт.
- Наступна кодова ревізія — **10.11-r8**. Наступний окремий finding Issue #175 — build/release hardcoding cleanup.

## 10.11-r6 — atomic output, restore/backup hardening та офіційний prerelease — 06.11.2026

- Окремий hardening-slice за Issue #175; UX #164 і CI optimization #142/#152 не змішувались.
- `src/taxo/output_files.py::write_output_file()`: writer працює через sibling temp із тим самим suffix; успіх завершується `os.replace()`; при помилці temp прибирається, попередній правильний output не пошкоджується.
- `src/taxo/backup_migration.py::restore_database_from_file()`: подвійна помилка restore + safety rollback більше не ковтається; composite failure містить обидві помилки і шлях до safety backup; rollback після копіювання перевіряється валідатором.
- Backup UI та ADMIN_GUIDE прямо показують, що `Data/EmployeeDocuments` входить завжди; базове ім'я змінено з `Taxo_backup_db_...` на `Taxo_backup_core_with_employee_documents_...`.
- Додано `tests/test_v10_11_r6.py`; оновлено історичний backup-disclosure regression, що перевіряв старе формулювання.
- Перший PR CI виявив два застарілі contract-тести (START ще r5 і старий текст «лише БД»); обидва виправлено до merge.
- PR #185 merged; exact issued source / exact-main = `558158a9777b18a05a224136fec4deeef55b5950`.
- Exact-main SUCCESS: START #42268068367 (**872 tests / OK**); Windows #42268068515; Windows 7 #42268068378; macOS ARM64/Intel #42268068403.
- Release-trigger PR #186 merged; trigger main `7a0eb9fa47bdea341854959376b473b214d00475`.
- Publisher #42269285656 — **SUCCESS**. Опубліковано immutable prerelease `v10.11-r6`; tag target = `558158a9777b18a05a224136fec4deeef55b5950`; 8 assets, усі r6. Stable/Latest лишається `v10.10-r5`.
- Google Drive підтверджено: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r6_2026-11-06_START.zip`, 1 531 200 байт.
- Наступна кодова ревізія — **10.11-r7**. Наступний рекомендований окремий slice з Issue #175 — Win7 загальний regression gate.

## 10.11-r5 — dependency security, Win7 mitigation та офіційний prerelease — 06.11.2026

- Окремий security/dependency slice за Issue #175; UX #164 і CI optimization #142/#152 не змішувались.
- Основна Windows/macOS лінія: Pillow `11.3.0 → 13.0.0`; pypdf `6.19.0 → 6.21.4`.
- Win7 / CPython 3.8.10 лишено на сумісних `Pillow 10.4.0` та `pypdf 5.9.0`. Для pypdf 5.9 Taxo додає runtime preflight page-tree budget перед flattening: entry budget 2 000 000, max nodes/depth та cycle guard.
- `attestation_render.py` більше не обходить захищений reader; PDF stamping теж використовує security preflight.
- Додано `tests/test_v10_11_r5.py`; Win7 workflow запускає цей security regression на CPython 3.8.10 до packaging.
- PR-head `76bd192359b30f3ae631c5a5fc2ff840dce059a1`: START #42229760772 — **867 tests / OK**; Windows #42229820841, Win7 #42229820773, macOS #42229820779 — SUCCESS. Win7 security-smoke — SUCCESS.
- PR #182 merged; exact issued source / exact-main = `f2614caf60380c4898c1d042bd6c8d402edc38da`.
- Exact-main SUCCESS: START #42230454712; Windows #42230454659; Windows 7 #42230454846 (incl. r5 security regression); macOS ARM64/Intel #42230454687.
- Release-trigger PR #183 merged; trigger main `fae431708a66664b238b37bf979aa84481c33898`.
- Publisher #42231569758 — **SUCCESS**. Опубліковано immutable prerelease `v10.11-r5`; tag target = `f2614caf60380c4898c1d042bd6c8d402edc38da`; 8 assets, усі r5.
- Google Drive підтверджено: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r5_2026-11-06_START.zip`, 1 525 891 байт.
- Наступна кодова ревізія — **10.11-r6**. Наступний рекомендований окремий slice з Issue #175 — output/restore/backup disclosure hardening.


## 10.11-r4 — захист історії тахографа та офіційний prerelease — 06.11.2026

- Продовження стабілізації за повним code-review Issue #175: окремим slice взято ризик каскадного видалення `control_protocols` через видалення вихідного `discs`.
- Робоча гілка `work/v10.11-r4-tachograph-history`; PR #179.
- У `src/taxo/tachograph.py` додано DB-level trigger `trg_tachograph_control_protocol_history`, який блокує видалення тахокарти, якщо для неї існує збережений контрольний протокол.
- UI-видалення використовує окрему перевірку та пояснює користувачу, чому історичний запис захищений. Чернеткова тахокарта без протоколу видаляється як раніше.
- Додано `tests/test_v10_11_r4.py`: helper guard, direct SQL DELETE guard, збереження snapshot, штатне видалення unprotected disc, наявність trigger після init. Повний PR-head START: **862 tests / OK**.
- PR-head `ac9e61626777487874f657731ba84d6744dac989`: START #42222773677, Windows #42222825203, Win7 #42222825057, macOS #42222825065 — SUCCESS.
- PR #179 merged; exact issued source / exact-main = `c4e701585d5ba5e06401002842f235ed3c363816`.
- Exact-main SUCCESS: START #42223328213; Windows #42223328267; Windows 7 #42223328554; macOS ARM64/Intel #42223328239.
- Release-trigger PR #180 merged; trigger main `51b17bc51986aa7cdf19092f538ad089e540e6c9`.
- Publisher #42224658087 — **SUCCESS**. Опубліковано immutable prerelease `v10.11-r4`; tag target = `c4e701585d5ba5e06401002842f235ed3c363816`; 8 assets, усі з r4-іменами. Stable `v10.10-r5` без змін.
- Google Drive підтверджено: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r4_2026-11-06_START.zip`, 1 519 882 байт. Зайвий повторний дубль видалено, у папці залишено одну підтверджену копію.
- Наступна кодова ревізія — **10.11-r5**. Наступний рекомендований окремий slice з Issue #175 — dependency/security; UX #164 і CI #142/#152 не змішувати.


## 10.11-r3 — захист plan/fact, атомарне перепланування та офіційний prerelease — 06.11.2026

- Повний read-only code-review зафіксовано в Issue #175. Найкритичніші знайдені дефекти: дія «План → факт» могла переписати існуючий факт; detailed personnel planner міг видалити старий план, не записати новий і закомітити стан.
- Робоча гілка `work/v10.11-r3-correctness`; PR #176. «План → факт» тепер працює лише для днів без факту, вимагає явного підтвердження й не переписує інші ручні поля.
- Детальна заміна `employee_shifts` переведена на SAVEPOINT: delete+insert атомарні; при DB/constraint error старий план відновлюється, batch rollback, користувач бачить помилку.
- Додано `tests/test_v10_11_r3.py`: 4 поведінкові regression tests. Перший CI виявив лише старий source-string contract; логіку не відкочували, сумісність збережено нейтральним коментарем.
- PR-head `e80fe0499c775b9e46625519847e7becfceadbd1`: START #42219058157 — 858 tests / OK; Windows #42219065224, Win7 #42219065321, macOS #42219065277 — SUCCESS.
- PR #176 squash-merged; exact issued source / exact-main = `a82a3dc6f7ce63a62d7318c7f423b17599360797`.
- Повторний exact-main CI: START #42219595152, Windows #42219595132, Windows 7 #42219595055, macOS ARM64/Intel #42219595074 — **SUCCESS**.
- Release-trigger PR #177 змінював лише checkpoint-коментар publisher. Required `build-windows` спочатку заблокував merge, після SUCCESS #42220118059 PR злитий без обходу ruleset; trigger main `0b2173ccc3f0942c2a364ddd95626f87e9ff2a2a`.
- Publisher #42220584720 — **SUCCESS**. Опубліковано immutable prerelease `v10.11-r3`; tag target = `a82a3dc6f7ce63a62d7318c7f423b17599360797`; 8 assets, усі з r3-іменами. Stable `v10.10-r5` без змін.
- Google Drive підтверджено: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r3_2026-11-06_START.zip`, 1 514 730 байт.
- Issue #175 залишається відкритим: наступні окремі slices — захист історії тахографічних протоколів, dependency/security, output/restore/backup hardening та інше. Наступна кодова ревізія — **10.11-r4**.


## 10.11-r2 — офіційний prerelease, build-name incident і завершення checkpoint — 05.11.2026

- Функціональний PR #169 злитий у main `defbc33245e6fc984eb1a280f7e9c1ab8f05ccbd`: змістовні імена простого графіка працівників; колонка «Роль» прибрана лише з PDF; XLSX/БД/plan-fact незмінні.
- Перший exact-main функціонального стану пройшов START/Windows/Win7/macOS, але publisher #42084574084 **відмовився створювати release**: build artifacts ще містили hardcoded `candidate_r1` у внутрішніх іменах файлів.
- Окремий build-only PR #171 виправив активні `packaging/installer/Taxo.iss`, Windows, Win7 і macOS workflows. Код функціоналу не змінювався.
- Після #171 exact issued source = `68d7459b28e4ae68d97b6dd43cc92ead695a80bb`.
- Exact-main SUCCESS: START #42085643768; Windows #42085643914; Windows 7 #42085644022; macOS ARM64/Intel #42085643987. Логи підтвердили `candidate_r2` та відсутність активних `candidate_r1`.
- Release-trigger PR #172 merged; publisher #42086984364 — **SUCCESS**.
- GitHub prerelease `v10.11-r2` опублікований з 8 assets; tag target = `68d7459b28e4ae68d97b6dd43cc92ead695a80bb`; stable `v10.10-r5` без змін.
- Google Drive: підтверджено `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r2_2026-11-05_START.zip`.
- Виданий r2 immutable. Наступна кодова ревізія — **10.11-r3**; подальший UX — Issue #164.

## 10.11-r2 — простий графік працівників: назва PDF і друк — 05.11.2026

- Старт від `main` `03df7bffeb1d46e3f51d9788f070292a0cec44df`; гілка `fix/v10.11-r2-personnel-report-20261105`.
- Реалізовано назву `Простий_графік_роботи_YYYY-MM_<вибірка>.pdf/.xlsx`; один працівник — прізвище/ім'я, група — прізвища + короткий стабільний код, повна вибірка — `усі-працівники`.
- Лише в PDF простого графіка прибрано колонку «Роль»; Excel її зберігає. Ролі в БД, кадрова картка, plan/fact, графік водіїв та історія не змінюються.
- Додано `tests/test_v10_11_r2.py`: 30/31 день, довгі ПІБ, одна/кілька/всі вибірки, різні групи, PDF landscape A4, збереження ролі в XLSX.
- Candidate identity синхронізовано на `10.11-r2`; stable `v10.10-r5` і prerelease `v10.11-r1` незмінні.
- Статус: **PUBLISHED PRERELEASE**; ручне приймання r2 триває, наступні зміни — 10.11-r3.

**Оновлено:** 06.11.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

## 10.11-r1 — immutable candidate prerelease та відгук власника — 05.11.2026

- PR #165 (handoff/state/worklog/guide), #166 (release notes/index) та #167 (штатний publish trigger) злиті в `main`; останній release trigger main `e1eea5e3e1b4714bb1c9d0c73cb895de6a591d49`.
- Exact verified source `89a93c0ddf95dfa120260f71ae98c8b772178a56`; CI START #42062350021, Windows #42062350458, Win7 #42062350396, macOS #42062350456 — SUCCESS.
- Workflow публікації #42063810115 — SUCCESS; GitHub prerelease [v10.11-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r1) з 8 artifacts і SHA256; тег незмінний. Stable залишається v10.10-r5.
- Зауваження власника щодо експортованого `Графік_працівників_2026_11.pdf` (неоднозначна назва) і зайвої колонки «Роль» у цьому друкованому PDF записано до Issue #164. **Виправлення лише в 10.11-r2**, не в уже виданому кандидатові r1.
- Робочих БД, employee-shifts, ролей, шляхівок, бланків і документів не змінювали.
- Наступна дія: завершити користувацьке тестування r1, наступним окремим кодовим кроком 10.11-r2 виправити назви вибіркового PDF та друковану колонку без змін plan/fact.

## 10.11-r1 — UX та імена файлів — 05.11.2026

- 5 скриншотів від власника показали перевантажений інтерфейс і хаос із назвами звітів, Issue #164.
- PR #163: 5 кнопок експорту місячного водійського графіка → один вибір документа та «Переглянути»/«Зберегти…», коротка інструкція.
- Стандарт назви: тип, YYYY-MM, коло осіб; один водій — прізвище та ім'я, група — перші два прізвища, кількість інших і короткий код набору.
- Додано `tests/test_v10_11_r1.py`; виправлено історичні тести версій і викликів друку для переходу 10.10-r10 → 10.11-r1.
- PR #163 merged: `0954018073f41df00a1c11291d92cf24d2d28456`. Pre-merge та exact-main Windows, Windows7, macOS ARM64/Intel, START — SUCCESS.
- Windows Portable та Setup завантажено власнику для користувацького приймання; SHA256 та цілісність ZIP перевірено.
- Google Drive current-main r1 START snapshot підтверджений у `02_CURRENT_MAIN`.
- Stable `v10.10-r5` без змін. Наступна ревізія `10.11-r2`; решта робіт Issue #164.

## 10.10-r9 — узгодження графіка водіїв — 05.11.2026

- Скріншоти власника виявили розбіжності між водійським табелем та новим графіком/PDF r8 (02.11, 14–16.11) та crash `adjusted() takes 5 positional arguments but 6 were given`.
- Створено робочу гілку `fix/r9-driver-schedule-consistency` та PR #160; виправлено визначення linked driver, читання worklog для клітинок водійського графіка і wrapper коригування відсутностей.
- Новий тест `tests/test_v10_10_r9.py`; версія та пакетування оновлені до r9.
- Початкові PR workflow впали лише через старий hardcoded r8 version guard; після узгодження workflow PR CI: Windows, Windows 7, macOS ARM64/Intel SUCCESS.
- PR #160 merged squash у main `66882a2164bea1a72a30ec1db74d36d1613d0c68`.
- Exact-main r9 SUCCESS: START #42041201788, Windows #42041201831, Windows 7 #42041202075, macOS #42041201978. Windows Portable/Installer отримано та звірено SHA256.
- Stable v10.10-r5 збережено. Жодної робочої БД чи сканів не читали й не переписували.
- Раніше записані подвійні employee_shifts не видаляємо автоматично; діагностика на копії — окрема робота.
- Next revision: 10.10-r10. CI optimization #152 не змішувати.

## 10.10-r8 — простий місячний графік — 05.11.2026

- PR r8 інтегровано в `main`; exact-main START, Windows, Windows 7, macOS ARM64 та Intel підтверджені успішно.
- Stable не змінено: користувацький stable залишається `v10.10-r5`.
- Наступна кодова ревізія після завершення r8 checkpoint — `10.10-r9`.

- Додано місячне планування для явно вибраних працівників.
- Простий план пишеться у чинний employee_shifts лише для безпечної однозначної неводійської ролі.
- Driver-only працівники не дублюються: їхній план читається з графіка водіїв.
- Факт/відсутності/конфлікти не перезаписуються.
- Employee-facing PDF/XLSX завжди будується з явного selected employee set; internal_notes не входять у такий export.
- Окремим тестом перевіряється, що в персональний Excel не потрапляють інші працівники.


## 10.10-r7 — документи працівників — 05.11.2026

- Вимоги до документів винесені на рівень працівник + тип документа.
- Обов'язковість і контроль строку незалежні.
- Архівування окремої копії не скасовує вимогу.
- Локальні файли документів копіюються у Data/EmployeeDocuments; існуючі зовнішні файли можна зібрати окремою безпечною операцією.
- EmployeeDocuments завжди входить до full workspace backup.
- Наступний slice: r8 простий місячний графік та відокремлені внутрішні/рольові/особисті представлення.


## 10.10-r6 — Працівники 2.0 / дані та реєстри — 05.11.2026

- Власник доручив привести до ладу роботу з даними працівників: Дія/державні відомості, масові операції, документи та простий графік.
- Перший окремий slice r6: єдиний центр даних + масове застосування останнього імпорту.
- Старі методи/сховища не видаляються; новий центр є оболонкою над чинною моделлю.
- Ідентифікаційні поля РНОКПП та registry-person-id виключені з масового перезапису.
- Перед масовою зміною викликається резервна копія основної БД.
- Далі після r6: r7 документи/обов'язковість/workspace backup; r8 простий місячний графік з role/personal views.


## R5 STABLE — 05.11.2026

- `v10.10-r5` опубліковано повним комплектом із 8 release assets.
- Власник раніше перевірив виправлення запуску на Apple Silicon Mac mini.
- Повний CI на PR і на main — SUCCESS для Windows, Windows 7, macOS ARM64/Intel та START.
- `v10.10-r4` superseded через підтверджену проблему запуску на macOS; tag/release не змінюється.
- `v10.10-r5` стає Stable / Latest.
- Наступна кодова ревізія: `10.10-r6`.
- Наступна робота: повернутися до CI optimization; PR #152 спершу звірити/перенести на актуальний r5 main.


## R5 MAIN CHECKPOINT — 05.11.2026

- PR #151 інтегровано в `main`; main SHA `44ff2854d85ef71cd2647f90568c73c2ba56c6f9`.
- Повний main CI: Windows, Windows 7, macOS ARM64 + Intel, START — SUCCESS.
- Випуск `v10.10-r5` формується тільки з цих перевірених main-артефактів.
- Наступна дія: publish r5 → stable/Latest → документація.


## MACOS STARTUP FIX → 10.10-r5 — 05.11.2026

- Stable `v10.10-r4` має підтверджену проблему запуску на macOS.
- PR #151 містить виправлення навігації «Працівники» для macOS.
- 04.11.2026 власник перевірив виправлену Apple Silicon збірку: запуск з Finder, головне вікно, підключення бази й розділ «Працівники» працюють.
- Попередня перевірка правки на Windows / Windows 7 / macOS — успішна.
- 05.11.2026 власник доручив перенести правку в основну версію.
- Видану r4 не перевикористовуємо: офіційна ревізія правки — **10.10-r5**.
- PR #152 з оптимізацією перевірок лишається окремою роботою.
- Далі: повна перевірка r5 → інтеграція #151 → випуск r5 → заміна r4 як stable/Latest.


**Stable release:** **Taxo 10.10-r5 / `v10.10-r5`** — виправлена macOS-версія; Windows 10/11, Windows 7, macOS Intel/ARM, START і SHA256 опубліковані
**Previous stable / rollback:** **v10.9-r10**; older rollback — `v10.3`
**Next code revision:** **10.10-r10**
**Recovery:** `HANDOFF_CURRENT.md` — короткий актуальний стан; Issue #61 — довга історія

Повний аудит: [`docs/maintenance/AUDIT_FULL_2026-10-05.md`](docs/maintenance/AUDIT_FULL_2026-10-05.md).

## CONTINUITY ADOPTION — 03.11.2026

- Прийнято dev-strategy v2 continuity для Taxo.
- Додано `HANDOFF_CURRENT.md` як першу recovery-точку після `START_HERE.md`.
- Створено private Taxo-profile у `RomanZavadaM/dev-strategy`, branch `profile/taxo`.
- Новий recovery-порядок: START → HANDOFF → private profile → live GitHub.
- WORKLOG лишається технічною хронологією і більше не повинен бути першим великим документом для нового чату.
- Після критичних змін HANDOFF оновлюється одразу.
- Наступний етап після інтеграції: незалежний review Taxo-профілю самим проєктом/іншим виконавцем із feedback у dev-strategy.

## SESSION CLOSE — 03.11.2026

- PR #149 `docs: record response to dev-strategy audit` перевірено і злитий у `main`.
- Merge SHA: `417b2ed5dd4e8d64f52cddb32ee8648194a2e8f2`.
- Windows, Windows 7 і macOS checks для PR #149 — success.
- Факт підтверджено: docs-only PR досі запускає всі три важкі platform builds.
- Рішення за аудитом записані в `docs/maintenance/DEV_STRATEGY_AUDIT_RESPONSE_2026-11-03.md`.
- Stable лишається `v10.10-r4`; код продукту і VERSION у цьому етапі не змінювались.
- Завтра: окремий CI-slice для docs-only, від актуального `main`, без автоматичного merge старого PR #142.

## DEV-STRATEGY AUDIT RESPONSE — 03.11.2026

Незалежний read-only аудит `dev-strategy` розглянуто.

Прийнято:
- split quick recovery / full preflight;
- виправлення меж read-only аналізу Taxo;
- окремий CI optimization slice для docs-only;
- окремий build/release security audit;
- окрема перевірка технічної незмінності releases;
- незалежний continuity recovery trial.

Не робити:
- не міняти stable лише заради методології;
- не застосовувати рекомендації автоматично;
- не змішувати CI/security/release hardening із функціональними змінами.

Деталі: `docs/maintenance/DEV_STRATEGY_AUDIT_RESPONSE_2026-11-03.md`.

## DOING

- **10.10-r4 завершено і прийнято як stable.** Виправлено версію у всіх вікнах, повернено Windows 7 Setup, усі платформні збірки успішні. PR #144 злитий; `v10.10-r4` опублікований; власник 03.11.2026 дав рішення випустити його як stable.
- Додано один універсальний механізм публікації замість окремого publish-файлу під кожну ревізію. Наступний кодовий крок — `10.10-r5`.

## ЦІЛІ НА МАЙБУТНЄ — недопрацювання станом на 05.10.2026

Порядок — орієнтовний; кожен пункт стартує лише за рішенням власника.

1. **Глибока перевірка бізнес-логіки stable 10.9-r10** — головне незроблене завдання 05.10. Лише читання коду, без змін і без локальних запусків: plan/fact, бланки підтвердження й фактичні межі, шляхівки та номери, табель і П-5, контроль праці/відпочинку, 60-денний реєстр, СТОІР, накази. Результат — перелік логічних помилок з місцями в коді.
2. **Експлуатаційне спостереження stable 10.10-r4.** Слідкувати за реальною роботою після переходу зі старої stable; окремо лишається ручна перевірка PDF на Windows 7 (PDFium у CI не перевіряється).
3. **Посібники користувача** (`docs/guides/*`, `DATA_MODEL_AND_STORAGE.md`) написані для 9.0–10.4 і не описують 10.5–10.9: СТОІР, накази й групи наказів, захист шляхівок і номерів, контроль праці/відпочинку 10.9, реєстр документів працівників, звірку з Дія, військовий облік, склад резервної копії, контроль сумісності схеми. Оновлювати після перевірки реального інтерфейсу (таблиця — `docs/README.md`, «Стан посібників»).
4. **Повне видалення працівника з бази** (рішення власника, варіант «б»; планувалось як 10.10-r4):
   - окрема явна дія; наявний механізм «Завершити роль водія» не змінюється;
   - попередження з переліком усього, що буде видалено (таблиці/документи з кількістю, включно з виданими шляхівками, наказами, бланками, тахографічними дисками, файлами), і явне підтвердження;
   - перед видаленням — копія основної й тахографічної БД в окрему теку `Backups/EmployeeDeletion/…` (поза ротацією 30 копій `backup_database`); файли не знищуються, а переносяться туди ж;
   - карта зв'язків (25+ таблиць, дві БД) і правила: шляхівки видаляються першими — тригери 10.9-r2 не обходяться; номери лишаються в `waybill_number_history`; спільні документи (накази з кількома особами, налаштування відповідальних) не видаляються — прибирається лише посилання; таблиці з `RESTRICT` (`vehicle_driver_assignments`, `military_statement_approvals`) — явна обробка; зв'язки без FK (`attestation_audit`, `operations_change_log`, `discs`/`control_protocols`) — явно;
   - одна транзакція: або все, або нічого.
5. **Виправлення з лінії 10.10 уже увійшли в stable 10.10-r4:** правильна версія, попередження «лише БД», відсутність PyMuPDF та повернений Win7 Setup.
6. **PyMuPDF:** stable 10.9-r10 і історичні releases v8.64…v10.9-r9 містять PyMuPDF (AGPL-3.0). Лінія 10.10 — без нього. Рішення щодо вже опублікованих пакетів — за власником (бажано з юристом).
7. **Правило СТОІР:** чи закриває/скидає ТО-2 цикл ТО-1 — рішення власника.
8. **Технічний борг (аудит A2/A3):** 55 шарів успадкування `App`, 184 підміни функцій `core`, `main.py` ~16.4 тис. рядків; 99 `except Exception: pass`; ~350 тестів перевіряють лише текст коду, а не поведінку. Поступово, доменами, з поведінковими тестами.
9. **CI:** версії й імена пакетів захардкоджені в workflow — кожна ревізія потребує ручної правки YAML; винести в `VERSION.txt`.
10. **Гілки:** 43 не злиті гілки з комітами поза `main` — переглянути з власником (злиті 164 вже видалено; список SHA в Issue #61).
11. **Публікація stable:** stable-пакети 10.9-r10 мають імена `candidate_r10` (оригінальні перевірені збірки). Для майбутніх stable — домовитись про схему імен до збирання кандидата.

## УРОКИ СЕСІЇ 05.10.2026

- **Stable = версія, яку власник перевірив на реальних даних**, з її оригінальними пакетами. Не робити нових ревізій «перед stable» і не перезбирати stable.
- **Нічого не запускати на машині власника без його згоди** — перевірка лише в CI (інцидент із робочою БД).
- Нові функції — лише після закриття поточної задачі власника; спершу уточнити, що саме мається на увазі.

## DECISIONS — власник, 05.10.2026

1. **Stable:** `v10.10-r4` — рішення власника 03.11.2026. Попередня stable / rollback — `v10.9-r10`; `v10.3` лишається давнішим rollback.
2. **Мовні пакети:** лише документація; інтерфейс програми — українською.
3. **Гілки:** видалити гілки, повністю злиті в `main`; теги й releases не чіпати.
4. **Повна резервна копія за замовчуванням:** лише БД, з явним попередженням.
5. **PyMuPDF** заборонений назавжди (`PROJECT_RULES.md` §17); 10.10-r1 — без нього.
6. **Повне видалення працівника:** варіант «б» — видаляти все з попередженням-переліком і підтвердженням; резервна копія перед видаленням.
7. **Локальні запуски:** без згоди власника тести/програму на його машині не запускати; перевірка — лише CI.

## BLOCKED

- Правило СТОІР ТО-2 → ТО-1 — відкрите рішення власника; Stable не блокує.
- Історичні releases v8.64–v10.9-r9 містять PyMuPDF — рішення власника (бажано з юристом); Stable не блокує.

## DONE — 03.11.2026

- **Stable `v10.10-r4`** — виправлена версія в усіх вікнах, Windows 7 Setup + Portable, Windows 10/11 Setup + Portable, macOS ARM/Intel, START, SHA256; прийнято власником як stable.
- **Універсальна публікація** — один активний механізм замість окремих publish-файлів для кожної ревізії.

## DONE — 05.10.2026

- **Stable `v10.9-r10`** (Latest) — оригінальні перевірені CI-збірки 02.10 (Windows x64 Setup/Portable, Windows 7 Portable, macOS arm64/x86_64, START, SHA-256); тег на `5e179eab`.
- **Документація під stable** — PR #140 → main `17bc2040`: README (uk + 6 мов), індекси, статус, release notes, PROJECT_STATE, WORKLOG; виняток §17; перегляд посібників.
- **Тестова лінія 10.10 (prerelease):** r1 без PyMuPDF (PR #136), r2 CI hardening + ізоляція тестів (PR #137), r3 правильна версія + попередження «лише БД» (PR #138); r1 і r3 власник перевірив на робочій машині («працює»).
- **Аудит 05.10.2026** — PR #135; правило §17 (ліцензії залежностей, заборона PyMuPDF).
- **Репозиторій:** 72 одноразові workflow → `docs/history/workflows/`; видалено 164 злиті гілки.
- PR #139 (stable 10.10 з перезбиранням) — закрито без інтеграції.

## INCIDENT 05.10.2026

Локальний прогін регресії на машині власника записав тестові записи в робочу БД (`main.py` читає робоче сховище з `%APPDATA%\Taxo\workspace.json` при імпорті). Власник виправляє БД сам. Наслідок: ізоляція тестів у 10.10-r2 і правило «лише CI».


## 10.11-r10 — UX звіту табеля персоналу — 06.11.2026

- PR #198 злитий у `main`: `15a04d0a383cc74a0ce8c1bd5e374d3948127a7a`.
- У «Табелі робочого часу всіх працівників» PDF/Excel зведено до одного вибору формату + «Зберегти…».
- Загальна назва файла: `Табель_робочого_часу_YYYY-MM_усі-працівники.*`.
- Plan/fact, БД і розрахунки не змінювалися.
- PR-head CI після виправлення: Windows #42289176738, Win7 #42289176886, macOS #42289176734 — SUCCESS; обидві macOS архітектури зелені; Win7 full regression PASS.
- Pre-release docs checkpoint додає release notes і стає exact source для повторної main-перевірки перед immutable prerelease.
- Stable залишається `v10.10-r5`.


## 10.11-r10 — офіційний immutable prerelease — 06.11.2026

- PR #198: вузький UX slice у загальному табелі персоналу; selector PDF/Excel + одна дія «Зберегти…»; однозначне ім'я файла.
- Після першого CI падіння виправлено три точні причини: START identity r10, два історичні UX-contract тести та помилково зачеплений filename окремого balance-звіту.
- Повторний PR-head CI: Windows #42289176738 — SUCCESS; Win7 #42289176886 — SUCCESS; macOS #42289176734 — SUCCESS (ARM64 + Intel); regression — 888 tests.
- PR #198 merged: `15a04d0a383cc74a0ce8c1bd5e374d3948127a7a`.
- PR #199 додав release notes + WORKLOG; exact issued source = `b239bb0dda6a49878f5f06a0edd791710b62df9b`.
- Release-trigger PR #200 merged; trigger main = `500a1ee559a02e39bb1b8e5874688749fd84aaa4`.
- Publisher exact-source guard вимагає successful START + Windows + Win7 + macOS саме для issued SHA до створення release; `v10.11-r10` створено і tag target перевірено як `b239bb0dda6a49878f5f06a0edd791710b62df9b`.
- Publisher формує канонічний комплект 8 assets; stable marker лишився `10.10-r5`.
- Google Drive r10 START recovery-copy ще не створена; остання підтверджена recovery-copy — r9.
- За правилом версій після r10 наступна кодова ревізія — **10.12-r1**.


## 09.11.2026 — 10.15-r2: типові накази та інструктажі БДР/ОП

- Власник попросив наповнити модуль наказів/інструктажів реальними редагованими заготовками, з окремим акцентом на автобуси та зимову експлуатацію.
- Додано 17 програм інструктажів БДР/ОП і 11 заготовок наказів.
- «Інструктажі та журнали»: вибір типової заготовки, редагування повного тексту програми, збереження теми/програми/підстави/працівників у підготовчому CSV.
- «Накази»: вибір кількох готових текстів; заготовка змінює тему/вступ/пункти тільки після явної кнопки «Вставити заготовку».
- Нормативна межа: Taxo не підміняє паперовий журнал, фактичні підписи чи затверджену підприємством програму; квартал — лише робочий календар.
- Перший macOS live regression знайшов реальний UI-дефект: кнопка збереження інструктажу виходила за доступну висоту малого вікна. Компонування виправлено до merge; повторні Windows/Win7/macOS тести пройшли.
- PR #288 merged; exact main `a5c09ffefde06074dd5339386e8d7fef75581211`.
- Exact-main: START #2560, Windows #1424, Win7 #399, macOS #1324 — SUCCESS; Windows 1049 tests / OK.
- START: artifact #13699543226, 1 788 528 bytes, SHA256 `8a03ca6b3e2be245559bbdb0e1333348ef6738e66c6f810d3c93ea39bfe784aa`; ZIP 634 entries, no nested ZIP.
- Google Drive: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.15-r2_2026-11-09_START.zip`, ID `1rmpW1SFVnzmvaMFWLfLBNrlEMnzWWgpB`.
- Stable лишається v10.14-r4. Manual acceptance r2 pending. Next code revision: 10.15-r3.

### Нові рішення власника для наступної розробки

- Створено Issue #289: єдиний каталог готових документів, сортування за датою/напрямом/типом та добровільне прикріплення сканів/фото паперових оригіналів. Скан не є обов'язковим і не означає автоматично «підписано».
- Створено Issue #290: припинити неконтрольоване зростання Python-монолітів. Поточний `main.py` ~848 КБ, `personnel_v91.py` ~194 КБ, `operations_orders_ui.py` ~84 КБ. Нові домени — окремими модулями; існуючі — дробити поступово, без big-bang rewrite.
- Issue #237 лишається відкритим: r2 дав тексти, але повний календар/строки/пропуски/історія програм — окремий наступний slice.
