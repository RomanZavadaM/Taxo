## 20.11.2026 — уточнення резервування

- Власник визначив Google Drive резервом документації, логів і порядку роботи, не копіями коду/збірок. GitHub залишається джерелом коду та релізів. Усі попередні архіви зберігаються до окремого рішення.
- Документаційна перевірка виявила втрату буквального історичного якоря Taxo 10.3 / `v10.3`; відновлено без послаблення тесту.

## 20.11.2026 — 10.23-r1 Stable/Latest; 10.23-r2 Test

**Stable/Latest:** [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1), 20.11.2026, 8 файлів. Exact source `84184bbbf6c26b681c04feaebee19910269bd25c`; START #44600058957, Windows #44600058914, Win7 #44600058737, macOS #44600058736 — SUCCESS; Defender/integrity PASS. Promotion PR #565 merged `e307b1a05a1ee8b6ef277a3a02fa3b72576bac32`; historical publisher #44704009390 SUCCESS. Попередня stable [10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2).

**Поточний тестовий випуск:** [10.23-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r2), 19.11.2026, 8 файлів, prerelease. Exact source `ac0bd0d5078ab4bd4c76abcaa0ca9b72e776e03e`; START #44617883252, Windows #44617883284, Win7 #44617883325, macOS #44617883395 — SUCCESS; publisher #44619140603 SUCCESS після виправлення пошуку exact-source CI (#564). Код main залишається r2. Одноразовий full marker прибрано.

- Власник уточнив r1, не r2. Перевірки #565 пройдено; звичайний publisher пропущено, історичний завершився SUCCESS. Stable має 8 файлів, exact tag не змінено. README та переклади, посібники, стан і релізний індекс синхронізовано окремим docs checkpoint. #553/#556 відкриті, #562 — наступний вузький крок 10.23-r3. Резерв Google Drive потребує окремого підтвердження.

## 19.11.2026 — 10.23-r1: розширення захисту функцій Taxo

- PR #557 merged: 32 суворі UI-маршрути, автоматичне виявлення втрати команд/вкладок; перевірки наказів і каталогу.
- PR #558 merged: ідентичність тестової версії 10.23-r1. Immutable source `84184bbbf6c26b681c04feaebee19910269bd25c`.
- Exact-source START #44600058957, Windows #44600058914, Win7 #44600058737, macOS #44600058736 — SUCCESS; Defender/integrity PASS.
- PR #559 publisher trigger, #44601093398 SUCCESS. Test prerelease v10.23-r1, 6 assets. Stable v10.21-r2 untouched.
- Рамки: захист усього Taxo ще неповний; наступний крок 10.23-r2 — редагування ролі/примітки збереженого учасника наказу, Issue #553. Issue #556 — подальший аудит UI.

## 19.11.2026 — 10.22-r10: керування папками та виправлення PDF-додатка наказу

- За підтвердженим r9 розпочато 10.22-r10. Product PR #550: переміщення вкладених логічних папок, архівування/відновлення з усіма нащадками, перевірки циклів і заборона запису в архівні папки. «Додати документ у цю папку…» відкриває повний каталог навіть із порожньої папки; вибір папки не скидається після додавання. Повний backup/restore зберігає структуру та membership.
- За скріншотами власника уточнено два різні дефекти. Нерозумілий шлях «Експлуатація → Учасники / ТЗ» збережено окремо в Issue #553 (ще потребує end-to-end/manual acceptance). У PDF-додатку до наказу №30 ролі/ПІБ перекривали сусідні колонки: PR #551 замінив сирі рядки на Paragraph-клітинки, додав перенос і тести; пробний PDF візуально перевірений.
- Product PR #550 merged `4cfb2637683a6a2d74374919f6255ec957526411`; PDF PR #551 merged. Exact immutable product source **`56917daed4756dc4725cc58c43fcb900ce256f2c`**.
- Exact-source CI: START #44535065602, Windows #44535065617, Win7 #44535065603, macOS #44535065691 — SUCCESS, Defender/integrity PASS.
- Застарілий publisher PR #552 закрито без merge після зміни точного коду. Reconciled trigger PR #554 merged `bb01b7537e3309b2c45841731b361b789b1dc01c`; publisher #44536931544 SUCCESS.
- [v10.22-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r10) — Test Portable, 6 assets (4 portable + START + SHA256); tag на точний продукт `56917dae…`. Stable/Latest **10.21-r2** без змін.
- Наступна кодова версія: **10.23-r1**; один вузький крок із Issue #553, окремо від майбутньої вхідної/вихідної кореспонденції PR #543.

## 19.11.2026 — 10.22-r9: власні логічні папки готових документів

- Після recovery r8 звірено START/HANDOFF/PROJECT_STATE, live GitHub, PR #543/#395, гілки та CI. Один Win7 run на main мав лише мережевий timeout оновлення Microsoft Defender; повтор пройшов SUCCESS без змін коду.
- Реалізовано **«Мої папки»** у каталозі «Документи»: власні та вкладені папки, перейменування, розміщення одного документа в одній або кількох папках. Файли документів фізично не переносяться, не перейменовуються і не копіюються.
- Структура папок і membership зберігаються окремо у `Data/DocumentLibrary/collections.json` з атомарним записом, перевіркою циклів, батьків, дублікатів назв/прив'язок і fail-closed читанням пошкодженого індексу. Залишок незавершеного temp-файла після обриву не блокує бібліотеку.
- Під час огляду виправлено важливий крайній випадок: prepared-документ не губиться з власної папки після реєстрації точної редакції у DocumentVault — логічний ключ лишається прив'язаним до стабільного походження документа.
- Додано regression для create/rename/nested/move core, кількох папок, фільтрації до pagination, повного backup/restore, пошкодженого індексу, interrupted-write residue і DocumentVault identity. Full START suite: **1556 tests**.
- Product PR #547 merged; final PR head `f1f01699f284d57b8db98bcef9473e3780276b0c`; immutable exact source `d38f6a2609775295dbd4885ebee58c9e587b9c2e`.
- Exact-source START #44517481797, Windows #44517481864, Win7 #44517482057, macOS Intel/ARM #44517481994 — SUCCESS; Defender/integrity PASS.
- Release-trigger PR #548 merged `5e5633214084535f1d594fc26ceea0e8c155befc`; publisher #44519029232 SUCCESS. [v10.22-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r9) — Test Portable prerelease, рівно 6 assets, tag на exact product source.
- Stable/Latest **v10.21-r2** без змін. **10.22-r10 не починалася.** Наступний вузький крок — переміщення/перепідпорядкування та безпечне архівування власних папок; кореспонденція окремою наступною роботою.

## 19.11.2026 — 10.22-r8: дерево бібліотеки готових документів

- Власник визначив наступну структуру: бібліотека шаблонів окремо від готових документів; віртуальні дерева за видом/датою, згодом власні редаговані папки. Додатково доручено ділову переписку: журнали вхідних/вихідних листів, номери, кореспонденти, відповіді, строки й файли. План у draft PR #543 (не реалізація кореспонденції).
- З основи main `c37cf6c304a17ef23068c9f281bc204225bfd315` взято один вузький кодовий крок з Issue #289: «Документи» → «За видами / За датами», роки/місяці, «Без дати» і «Усі документи». Кількість береться з повного snapshot, вузол фільтрує до сторінок, існуючі пошук/фільтри/сортування зберігаються. Чиста read-only логіка у `document_library_tree.py`, окремі регресійні тести. Не чіпали DocumentVault, SQLite, скани, підписи, backup/restore чи пари водій↔ТЗ.
- Product PR #544 merged; final head `054061fb85bf85e975f976ce82ab3ddc5a00472c`; exact product source `c3274b85d8e5f9fd7de0cb9172da63b2d392daa8`.
- Exact-source START #44506037689, Windows #44506037500, Win7 #44506037901, macOS Intel/ARM #44506037619 — SUCCESS, Defender/integrity PASS. PR-head checks також SUCCESS.
- Release-trigger PR #545 з незмінним marker Stable `10.21-r2`, merged `525083510f5ea43a4abd447f979ae3304071b96e`; publisher #44507263991 SUCCESS.
- [v10.22-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r8) — Test Portable prerelease, tag на точний product source, рівно 6 файлів (4 Portable, START, SHA256). Stable/Latest [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2) без змін.
- **10.22-r9 ще не почалася.** Наступна безпечна вузька дія: користувацькі логічні папки з контрольованим збереженням і перевіреним backup/restore; реєстр кореспонденції окремими подальшими ревізіями. Після recovery merge звірити main/PR/CI.

## 18.11.2026 — 10.22-r7: сортування каталогу за категорією

- Після fresh recovery взято один вузький пункт Issue #289: заголовок «Категорія» у спільному каталозі «Документи» тепер сортує А→Я / Я→А.
- Сортування застосовується до всього вже відфільтрованого списку до pagination. «Не визначено» залишається внизу в обох напрямках; «Скинути фільтри» повертає стандартний порядок за датою.
- Product PR #540 merged; final head `b7daf5f3b69bddf9240805c7608118145fc6c2e9`; immutable exact source `544da915100744f4fcf1e094f374d13c76c36c80`.
- Exact-source START #44404136276 **1540/1540**; Windows #44404136133, Win7 #44404136553, macOS Intel/ARM #44404136897 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #541: перший required Win7 check впав лише через timeout оновлення Defender `0x80072ee2`; повторний запуск SUCCESS без змін коду.
- Release-trigger PR #541 merged `7494e415a005a3c30c453069fabce7deefe2c457`; publisher #44406105602 SUCCESS. [v10.22-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r7) Test Portable — 6 assets; tag points exactly to product source.
- DocumentVault, скани, паперовий підпис, backup/restore, схема БД, пари водій↔ТЗ і Stable не змінювалися.
- Stable/Latest **v10.21-r2** unchanged. **10.22-r8 not started.**

## 18.11.2026 — 10.22-r6: окремий напрям «Сезонні заходи»

- Після fresh recovery взято один вузький пункт Issue #289: накази `seasonal_operation` у спільному каталозі «Документи» тепер мають окрему категорію «Сезонні заходи».
- Класифікація лише зі структурованого `order_type`; вільний текст не аналізується. Кадрова серія має пріоритет.
- Перший START у PR #537 знайшов один застарілий regression fixture без сезонного рядка. Виправлено тільки тестові дані; production-логіку не послаблювали.
- Product PR #537 merged; final head `d764e56596dc30a0b4c717a0a6b0a5b56a7f39c9`; immutable exact source `28d2b838dae51a8ed009dd4b14fe1a0afa561384`.
- Exact-source START #44386227495 **1535/1535**; Windows #44386227504, Win7 #44386227480, macOS Intel/ARM #44386227490 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #538 merged `c42d3554797ed3bfc133fd1337ab1288b8facc37`; publisher #44388264823 SUCCESS. [v10.22-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r6) Test Portable — 6 assets; tag points exactly to product source.
- DocumentVault, скани, паперовий підпис, backup/restore, схема БД, пари водій↔ТЗ і Stable не змінювалися.
- Stable/Latest **v10.21-r2** unchanged. **10.22-r7 not started.**

## 18.11.2026 — 10.22-r5: ручна позначка підписаного паперового документа

- Після прямого зауваження власника додано окрему колонку «Папір / підпис» та дію «Паперовий підпис…» з явною датою підписання. Відмітку можна скасувати без стирання історії.
- Паперовий підпис, скани та immutable DOCX — різні дані. Наявність скана не означає підпис; електронний підпис, юридична перевірка чи зміна бізнес-статусу не реалізуються.
- Append-only журнал `Data/DocumentVault/paper_original_events.json` у workspace, що автоматично входить до full backup/restore. Fail-closed перевірка некоректної дати, стороннього документа, пошкодженого журналу; суворий whitelist DocumentVault змінено лише для цього валідованого файла.
- Початковий START на гілці знайшов конфлікт whitelist і дві помилки тестування; виправлено до merge, повторний PR CI успішний.
- 4 нові regression-перевірки. Product PR #534 merged; final head `c7f79db2384ec359dc9cd5e62902f58c0a3fcdd9`; immutable exact source `576f93acd7d070a6786cfcd3c28af1d5f29d98c0`.
- Exact-source START #44375223718 **1531/1531**; Windows #44375224479, Win7 #44375223666, macOS Intel/ARM #44375223669 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #535 merged `ef8f63bdf5771d2a365509d5786bbf9ab6a115e8`; publisher #44376388134 SUCCESS. [v10.22-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r5) Test Portable — 6 assets; tag points exactly to product source.
- Stable/Latest **v10.21-r2** unchanged. **10.22-r6 not started.**

## 18.11.2026 — 10.22-r4: відкриття документа зі сховища

- У спільному каталозі «Документи» «Відкрити вибране» для DocumentVault тепер відкриває сам документ через окрему тимчасову DOCX-копію тільки для читання.
- Перед створенням копії повторно перевіряються індекс, розмір і SHA-256; immutable-файл у `Data/DocumentVault` зовнішній програмі не передається. Пошкоджений/підмінений об'єкт блокується.
- Додано 3 regression-перевірки: точні байти й розміщення поза vault/read-only, відмова при tamper, підключення дії в каталозі.
- Product PR #531 merged; final head `0f537c7ffe57c0628de4619eb8f2c19567beb02f`; immutable exact source `b01437828551fe309c2dfcba81572a9a9d51e628`.
- Exact-source START #44320801103 **1527/1527**; Windows #44320801102, Win7 #44320801191, macOS Intel/ARM #44320801139 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #532 merged `7d443e25f8ec754f71a3749c6e46163d8aca8728`; publisher #44322860950 SUCCESS. [v10.22-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r4) Test Portable — 6 assets, tag points exactly to product source.
- Stable/Latest **v10.21-r2** unchanged. **10.22-r5 not started.**

## 18.11.2026 — 10.22-r3: швидке скидання фільтрів каталогу

- Вікно «Документи»: кнопка «Скинути фільтри» очищає всі обмеження (джерело, скани, пошук, дати, тип, категорію, рік/місяць, працівника/ТЗ) і повертає список з новішими документами першими. Скидає сторінку та скасовує відкладений пошук, щоб не читати каталог повторно.
- Не змінювались файли, сховище, скани, БД, backup/restore, security/dependencies, пари водій↔ТЗ чи правила наказів.
- Product PR #528 merged, final head `96f5ad3567d9314eac4a1a42529900a05f729a2a`, immutable source `bb3e7fb77e50dc0bd963e1a2a5c164296cfb1722`. Exact-source START #44301305636 **1524/1524**; Windows #44301305635, Win7 #44301305627, macOS #44301305732 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #529 merged `3dcb3f22c9c1ccd8123dba945f933a210de82f6d`; publisher #44302569986 SUCCESS. [v10.22-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r3) Test Portable — 6 assets.
- Stable/Latest **v10.21-r2** unchanged. **10.22-r4 not started.**

## 18.11.2026 — 10.22-r2: точний зріз документів за працівником і ТЗ

- Після повного recovery 10.22-r1 взято наступний незалежний крок Issue #289 у спільному каталозі «Документи».
- Додано read-only фільтри за конкретним працівником і транспортним засобом. Джерело — тільки структуровані зв'язки: `operations_order_entities` з frozen snapshot для звичайних наказів та `vehicle_driver_assignments` для наказів про закріплення.
- Однакові ПІБ розрізняються за stable Taxo ID; вільний текст теми не використовується для автоматичного приписування документа людині чи ТЗ. Старі документи без структурованого зв'язку не переписуються.
- Колонка «Працівники / ТЗ» і пошук показують структуровані реквізити; нові фільтри комбінуються з роком/місяцем, «Від / До», типом, категорією, джерелом, сканами й пошуком до pagination.
- Product PR #525 merged; final PR head `98ef9e391765de6578fc4a666d13820dba9abb9d`; immutable exact source `0aac6e80025cdcc5b54f2f393dbc256f40e42f2d`.
- Exact-source START #44291976150 **1520/1520**; Windows #44291976175, Win7 #44291976210, macOS Intel/ARM #44291976217 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #526 merged `c51f2016b12187d87ab4567d5649f5a1747bec40`; publisher #44293509376 SUCCESS. [v10.22-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r2) — Test Portable, 6 assets, exact tag source above.
- Stable/Latest **v10.21-r2** unchanged. **10.22-r3 not started.**

## 18.11.2026 — 10.22-r1: швидка навігація каталогу за роком і місяцем

- Після завершення лінії 10.21 взято один незалежний крок у каталозі «Документи»: швидкі read-only фільтри «Рік» / «Місяць».
- Роки й місяці формуються тільки з коректних дат, реально присутніх у каталозі. При зміні року місяць скидається; місяць може працювати і без року по всіх роках. Старі записи з порожньою/некоректною датою не зникають у звичайному режимі.
- Нові фільтри комбінуються з пошуком, джерелом, сканами, «Від / До», типом і категорією до pagination. Файли, DocumentVault, скани, backup/restore, схема БД та механізм пар не змінювались.
- Product PR #522 merged; final PR head `fa4142f674e975ce76f17647bb478ea7c53fba9f`; immutable exact source `4d108acc1eac69c120244c19d32c89e112f6afcd`.
- Exact-source START #44280221670 **1511/1511**; Windows #44280221497, Win7 #44280221443, macOS Intel/ARM #44280221618 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #523 merged `061ebf398f69591703ee996582a1ce7219b17da6`; publisher #44284701235 SUCCESS. [v10.22-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.22-r1) — Test Portable, 6 assets, exact tag source above.
- Stable/Latest **v10.21-r2** unchanged. **10.22-r2 not started.**

## 18.11.2026 — 10.21-r10: категорії у спільному каталозі «Документи»

- Після повного recovery r9 механізм пар залишено без змін на майбутнє ручне тестування власника. Для незалежного наступного кроку взято каталог «Документи».
- Додано структуровані категорії: **Кадрові**, **Експлуатаційні**, **Охорона праці**, **БДР**, **Пожежна безпека**, а для старих записів без структурованого напряму — **Не визначено**.
- Для наказів категорія походить тільки з `order_series` + `order_type`; вільний текст теми не використовується для автоматичної класифікації. Кадрова серія має пріоритет.
- У UI додано окрему колонку й read-only фільтр «Категорія». Він комбінується з пошуком, джерелом, сканами, періодом і типом до pagination.
- Додано regression, включно з temp-SQLite перевіркою, що слова «Охорона праці»/«БДР» у довільній темі самі не змінюють категорію. Аудит: `docs/maintenance/AUDIT_DOCUMENT_CATEGORY_FILTER_10_21_R10.md`.
- Product PR #519 merged; final PR head `fdedb8bc013d1dcf51174c6a0b834f3780e39158`; immutable exact source `3c6a4aedaf18399f3688d02bba3eb0cd30dd74ad`.
- Exact-source START #44270332491 **1501/1501**; Windows #44270332484, Win7 #44270332389, macOS Intel/ARM #44270332442 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #520 merged `f78e213b496117c400599568ff4133fd1f9b616c`; publisher #44271925495 SUCCESS. [v10.21-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r10) — Test Portable, 6 assets, tag points exactly to product source above.
- Stable/Latest **v10.21-r2** unchanged. Лінія 10.21 завершила r10; наступна кодова ревізія — **10.22-r1**.

## 18.11.2026 — ручне приймання 10.21-r9

- Власник вручну перевірив механізм пар у 10.21-r9 і повідомив: «Вроді перевірив, нічого не знайшов».
- Ручне приймання зафіксовано як PASS; Issue #511 закрито. Новий дефект, якщо з’явиться надалі, не відкриває стару проблему автоматично — його фіксувати окремо.

## 17.11.2026 — 10.21-r9: редагування й перенесення пар у власному наказі

- Власник вручну перевірив r8 і повідомив: пари не редагуються, механізм нелогічний, «наказ → редагування → збереження» перекидає до загального вікна з купою пар без результату. Негативний результат записано в Issue #511, r8 не вважається вручну прийнятою.
- Перевірка коду підтвердила два примусових переходи: `_open_existing_assignment_manager()` знищував редактор і перемикав вкладку, а `order_editor_ui.save()` переводив збережений порожній наказ у загальний список. Обидва прибрано.
- У наявному наказі: вибір рядка + «Редагувати вибрану пару…»/подвійний клік, «Додати пару…», «Прибрати вибрану пару». Список конкретного наказу оновлюється одразу, немає автоматичного переходу між вкладками. «Зберегти пару» — окрема явна операція, яка не записує незбережений текст наказу.
- Новий наказ: «Замінити вибрану пару», «Взяти готові пари з наказів…». Імпорт читає точні зв'язки з попередніх наказів «Експлуатації», дозволяє шукати, виключає скасовані джерела та повтори, не змінює джерела.
- Додано regression для переставленого порядку списків, дубліката, неоднозначного вибору, скасування, CRUD, повторного відкриття і UI переходу у тому самому наказі. Старі власницькі сценарії з 12 парами, DOCX/PDF/JPG та backup/restore збережені.
- Проміжні тести знайшли помилкові припущення щодо транзакцій у тестах та старі точні перевірки номера r8; виправлені саме тести без відключення перевірок. Фінальний product PR #516 merged: head `0c32fc975c281ae976a5f25bba9cf38c199ea050`, immutable exact source `77b80c77f9fd084208d32847c62a5d16c4640262`.
- Exact-source START #44180404692 **1491/1491**; Windows #44180404613, Win7 #44180404568, macOS Intel/ARM #44180404629 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #517 merged `95d3405c25c7ad7bcc5aa6a2e29991bd74753a8a`; publisher #44181523720 SUCCESS. [v10.21-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r9) Test Portable: 6 assets, exact tag source above. Stable/Latest **v10.21-r2** unchanged.
- Issue #511 залишено відкритим для ручного приймання r9. **10.21-r10 ще не починалася.**

## 17.11.2026 — 10.21-r8: явні пари водій↔ТЗ у наказах

- Fresh recovery found live GitHub ahead of the user-provided checkpoint: 10.21-r7 was already product/release/recovery complete on main `874dbc8bb3ce5a92f31653deffa02412e9f5963a`; no pre-existing r8/#511 work branch was found.
- Root cause of the first Issue #511 screenshot confirmed in code: equal-sized independent vehicle/driver selections were paired by positional `zip`. r8 removes that silent behavior.
- New-order editor now stages explicit concrete pairs into a visible table: exactly one vehicle + one/more drivers per action, repeat for another vehicle. Unstaged selections block save. Existing-order bulk add follows the same safe rule; older stored orders are not rewritten.
- The owner regression with 12 pairs was converted from implicit 12+12 list zipping to explicit pair staging while retaining DB, reopen, DOCX/PDF/JPG and backup/restore checks.
- Intermediate CI exposed only stale regression/version guards that still expected the former implicit behavior or literal r7 identity; these were corrected before merge. Final product PR #513 merged; final PR head `55056ffccb9eb4c5de523e4d3109f2304cba0620`; immutable exact product source `c9dc9799c22565b56c737216983dd900265c29bd`.
- Exact-source START #44167952855 **1475/1475**; Windows #44167952924, Win7 #44167952849, macOS Intel/ARM #44167952840 SUCCESS; Defender/integrity PASS.
- Release-trigger PR #514 merged `293ddccfcf88433e7a331d79372e4fe1c71239b4`; publisher #44169744409 SUCCESS. [v10.21-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r8) is an immutable Test Portable prerelease with 6 assets and exact tag source `c9dc9799c22565b56c737216983dd900265c29bd`. Stable/Latest remains v10.21-r2.
- The second owner-reported problem — taking prepared pairs from «Експлуатація» — is intentionally **not** marked fixed by r8 and remains the next narrow part of Issue #511. **10.21-r9 not started.**

## 17.11.2026 — 10.21-r7: календар «Дата…» у шляхівках

- Started after r6 recovery closed, from main `e086dbde708f8564c966793d70ed0976aabd01ac`; no existing r7 branch. Used existing `calendar_button` and `show_calendar_picker` from the main schedule, without new dependencies.
- Selecting a new date refreshes only waybill-window day; cancel or same day does not cause refresh; r6 navigation remains. Separate regression tests added; no DB/waybill data or security changes.
- Product PR #509 merged, final PR head `dcbc81b363c4de737a20bcbf7d9869c0e61a8ef3`; immutable exact source `b3185f5f558d96880cc8c2614529d0fb2d0de660`.
- Exact-source START #44159339508 **1469/1469**; Windows #44159339500, Win7 #44159340068, macOS Intel/ARM #44159339556 SUCCESS; Defender/integrity PASS.
- Trigger PR #510 merged `4f9eafa9729f15b25dd1bf26385e87e3fe1aa520`; publisher #44161402744 SUCCESS. [v10.21-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r7) Test prerelease, 6 assets, exact source verified. Stable/Latest v10.21-r2 unchanged.
- New high-priority owner defect, two screenshots: wrong pairs when choosing drivers and vehicles, plus inability to select prepared pairs from «Експлуатація». Separate [Issue #511](https://github.com/RomanZavadaM/Taxo/issues/511) created; no r8 work started. Manual owner UI acceptance r7 not yet recorded.

## 17.11.2026 — 10.21-r6: власна навігація по даті у «Шляхівках»

- Після recovery live GitHub випереджав HANDOFF: 10.21-r5 вже була product/release завершена, але recovery PR #505 ще був open. #505 перевірено як docs-only і merged `e6658d1d1f1c374ff9e074d6ca95a1b924f50205`; лише після цього почато r6.
- Зауваження власника зі скриншота: у вікні «Шляхівки» незручно послідовно вводити кілометраж із паперових шляхівок, бо немає власного переходу по даті.
- Вузький UX slice: редаговане `ДД.ММ.РРРР`, Enter/«Перейти», «День -», «Сьогодні», «День +». Змінюється тільки день відкритого waybill-window; головний графік і дані не переписуються.
- Реалізація винесена в `src/taxo/waybill_date_navigation.py` і підключена через feature registry. БД/schema, odometer rules, issuance/voiding, plan/fact, backup/restore, security та dependencies без змін.
- Проміжний START `44148899029`: 1464 tests, 1 failure — layer imported, але descriptor не був внесений у registry через невдале текстове вставлення. Виправлено до merge; це не продуктова помилка логіки дати.
- Product PR #506 merged. Final PR head `e94c39080e2d2ab0e3db25bc7639edd50483c70f`; exact immutable source `ef444e7753ee0f112baf8729ca6cceefea738652`.
- Exact-source: START `44150116439` **1464/1464**; Windows `44150116540`; Win7 `44150116763`; macOS Intel/ARM `44150116499` SUCCESS; Defender/integrity PASS.
- Release-trigger PR #507 merged `f89351973061538407e64e5c9746a0aec358bca9`; publisher `44151934906` SUCCESS. [v10.21-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r6) — Test prerelease, exact tag source `ef444e7753ee…`, 6 assets = 4 Portable + START + SHA256.
- Stable/Latest **v10.21-r2** unchanged. Ручна UI-перевірка власником нового поля дати ще не зафіксована. **10.21-r7 не розпочата**.

## 17.11.2026 — 10.21-r5: сортування каталогу за «№»

- Fresh verification: main `fd0e97f9af7cb54bf5112188cd1004e414d829fe`, 415 refs, r5 не було, старий docs-only PR #395. Попередній main CI успішний.
- Один вузький Issue #289 крок: у «Документи» клік «№» перемикає natural numeric сортування ▲/▼ (2 перед 10; 2-А перед 10-А); порожні номери наприкінці. Фільтри перед сортуванням, сортування до пагінації, перемикання на першу сторінку. Сортування за датою r4 збережено.
- Перший проміжний START помітив неправильне regex-екранування числових частин у новій реалізації; виправлено до merge, старі проміжні runs не враховуються.
- Product PR #503 merged; final PR head `639d4461b2119dd7caebd37f8fb18e3ded5a890e`, exact release source `d3f01d1cefd11ac5cab15054dfab85d962c0a84c`.
- Exact-source CI: START `44141706069` **1459/1459**, Windows `44141706165`, Win7 `44141706293`, macOS Intel/ARM `44141706021` SUCCESS; Defender/integrity PASS.
- Release-trigger PR #504 merged `1515b1b52fe0a9e9d38d49bed7fd4f06f0de674f`; publisher `44143863239` SUCCESS. [v10.21-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r5) Test prerelease, immutable exact tag `d3f01d1c…`, 6 assets = 4 Portable + START + SHA256.
- Stable/Latest **v10.21-r2** unchanged, 8 assets. Сховище, файли, скани, backup/restore, бізнес-статуси, schema і КЕП не змінювалися. **10.21-r6 не розпочата**.

## 17.11.2026 — 10.21-r4: сортування дати в каталозі «Документи»

- Fresh GitHub verification: `main` `96c3fd4516addc0e95a93f3df024f8e97a62f3ac`, 412 refs (включно з гілками без PR), жодної r4 гілки; старий docs-only PR #395 не є продуктовою роботою.
- Один bounded slice Issue #289: натискання на заголовок «Дата» перемикає новіші ▼ / старіші ▲ на всьому відфільтрованому списку **до пагінації**. Некоректні й порожні дати в кінці; однакові дати зберігають вихідний порядок джерела.
- Новий regression `tests/test_v10_21_r4_document_date_sort.py`, оновлення version guards. Перший START: 1454 тестів, 1 failure лише через неправильне очікування порядку рівних дат у новому тесті; виправлено сам тест, продукт без змін.
- Product PR #500 merged; final PR head `4540da0b17b85348195701f108adeaf33f5ad3f7`, immutable release source `abc0d8848752b70d50f8d2d55983ed83159f24a7`.
- Exact-source CI: START `44125366421` **1454/1454**; Windows `44125366461`, Win7 `44125366427`, macOS Intel/ARM `44125366431` SUCCESS; Defender/integrity PASS.
- Release-trigger PR #501 merged як `d575f1b51caaf8f659dd2c2dc5f24b73271138af`, stable marker value `10.21-r2` не змінено. Publisher `44127599704` attempt 1 failure: remote artifact HTTP 503 egress during Mac Intel download; prerelease/tag ще не було. Rerun only publisher attempt 2 SUCCESS.
- [v10.21-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r4) опубліковано Test prerelease: exact tag source `abc0d8848752b70d50f8d2d55983ed83159f24a7`, 6 assets — 4 Portable + START + SHA256. Stable/GitHub Latest **v10.21-r2** незмінний (8 assets).
- Документна модель, файли, скани, backup/restore, бізнес-статуси, КЕП та залежності не змінювалися. **10.21-r5 ще не розпочата**; наступний вузький крок тільки після fresh verification.

## 17.11.2026 — Promotion 10.21-r2 → Stable/Latest

- Пряма команда власника: зробити саме 10.21-r2 стабільною. PR #499 merged `cdaaafe6078d55bbc7a2b3f5d605fc840d2d1cb6`; історичний promoter `44116866634` SUCCESS.
- Stable/Latest `v10.21-r2` — 8 assets: 2 Windows installers, 4 portable, START, SHA256; immutable source `b104f94ace0ae355df79c914b3be6f39417bd6e9` з exact-source 1442/1442 і Defender/integrity PASS.
- `v10.21-r3` залишається test prerelease 6 assets, code source `f8a30882c473568293b3123e1f23feca22e54334`. Main не повернуто на r2; product code r3 лишився інтегрованим.
- Звичайний publish-current на службовому merge #499 відхилив дублювання вже існуючого release, спеціальний stable promoter завершився успішно.

## 17.11.2026 — 10.21-r3: фільтр документів за типом

- Fresh verification почався з main `2145f025c82471b4917e5fafa20f2a821e7b169e`; перевірено 408 refs, включно з гілками без PR. 10.21-r2 вже була завершена/recovery-закрита; готової r3 гілки/PR не було.
- Один bounded slice Issue #289: у загальному каталозі «Документи» додано read-only фільтр «Тип». Значення формуються з уже наявного структурованого поля `kind`; без вгадування категорій і без міграції.
- Точний тип застосовується до повного snapshot до пагінації й комбінується з пошуком, джерелом, сканами та періодом «Від / До». Категорії БДР/ОП/кадрові та employee/vehicle navigation лишились поза r3.
- Перший START на проміжному head: 1448 тестів, 1 failure лише у новому тесті через жорстке очікування Unicode-порядку українських назв. Виправлено тест на перевірку складу значень; продукт не змінювався.
- Product PR #496 merged; final product head `7ad2df8ba4dd08d754cb1f47ea29b804438a4979`; exact immutable release source `f8a30882c473568293b3123e1f23feca22e54334`.
- Exact-source CI: START `44111408334` — **1448/1448**; Windows `44111408360`; Win7 `44111408405`; macOS Intel/ARM `44111408772` — SUCCESS. Defender та post-scan integrity PASS.
- Trigger PR #497 змінив лише кінцевий перенос рядка stable marker; значення `10.20-r5` лишилось незмінним. Merged `a301ed020d62831257748c7658d5bc61987d4e98`; publisher `44113848030` SUCCESS.
- [v10.21-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r3) опубліковано як Test prerelease; tag exact source `f8a30882c473568293b3123e1f23feca22e54334`; рівно 6 uploaded assets: 4 Portable + START + SHA256.
- На момент публікації r3 Stable/Latest ще була **v10.20-r5**; пізніше за прямою командою власника r2 підвищено до Stable/Latest (див. запис вище). Сховище/файли/скани/backup/status не змінювались; без КЕП/e-signature, auto «підписано», physical purge, migration або нових залежностей.
- **10.21-r4 не розпочата.** Наступний крок визначати лише після fresh recovery. Детальний аудит: `docs/maintenance/AUDIT_DOCUMENT_TYPE_FILTER_10_21_R3.md`.

## 17.11.2026 — 10.21-r2: фільтр документів за періодом «Від / До»

- На старті live GitHub випереджав HANDOFF: 10.21-r1 уже була інтегрована й опублікована, відкритим лишався recovery PR #492. r1 не повторювали. У #492 macOS arm64 мав лише DNS `ENOTFOUND` під час upload artifact; перезапущено один job, після SUCCESS recovery merged як `bc63503e3b87bb0c5767c9c14ebd2f8b804aa6e3`.
- Після fresh verification готової r2 гілки/PR не було. Один bounded slice Issue #289: у загальному каталозі «Документи» додано необов'язковий read-only період «Від / До» у форматі РРРР-ММ-ДД.
- Межі включні, застосовуються до повного snapshot до пагінації та комбінуються з пошуком, джерелом і фільтром сканів. Некоректні межі дають явну помилку; записи без коректної дати не вважаються такими, що входять у активний період.
- Product PR #493 merged; final product head `96c9a551e031adf44846263d4f44cc3acb533083`; exact immutable release source `b104f94ace0ae355df79c914b3be6f39417bd6e9`.
- Exact-source CI: START `44102833144` — **1442/1442**; Windows `44102833224`; Win7 `44102833082`; macOS Intel/ARM `44102833261` — SUCCESS. Defender та post-scan integrity PASS.
- Trigger PR #494 змінив лише кінцевий перенос рядка stable marker; значення `10.20-r5` лишилось незмінним. Merged `751480375503f74cdc205d1d20ba5b34ff44cffe`; publisher `44105145533` SUCCESS.
- [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2) опубліковано як Test prerelease; tag exact source `b104f94ace0ae355df79c914b3be6f39417bd6e9`; рівно 6 uploaded assets: 4 Portable + START + SHA256.
- Stable/GitHub Latest лишається **v10.20-r5**, 8 assets. Сховище/файли/скани/backup/status не змінювались; без КЕП/e-signature, auto «підписано», physical purge, migration або нових залежностей.
- **10.21-r3 не розпочата.** Наступний крок визначати лише після fresh recovery. Детальний аудит: `docs/maintenance/AUDIT_DOCUMENT_DATE_FILTER_10_21_R2.md`.

## 17.11.2026 — 10.21-r1: фільтр документів за наявністю сканів

- Fresh verification почався з main `9965827de5a75c64872848b54df2ccb6012d6a52`; перевірено 402 refs, включно з гілками без PR. Готової 10.21-r1 не було, тому стару роботу не повторювали.
- Один bounded slice Issue #289: у загальному каталозі «Документи» додано read-only фільтр «Усі» / «Є скани» / «Немає сканів» / «Помилка перевірки».
- Фільтр працює на повному snapshot до пагінації та поєднується з пошуком і джерелом. Вузькі режими стосуються лише DocumentVault; помилка перевірки не маскується як відсутність сканів.
- Product PR #490 merged; final product head `d0c2f0f34821f7443a877f556cb3152837422616`; exact immutable release source `c5e17aec02e60d8b87fc518165b7f62086dc5a9f`.
- Exact-source CI: START `44095180937` — **1436/1436**; Windows `44095181008`; Win7 `44095180907`; macOS Intel/ARM `44095180721` — SUCCESS. Defender та post-scan integrity PASS.
- Trigger PR #491 змінив лише кінцевий перенос рядка stable marker; значення `10.20-r5` лишилось незмінним. Merged `086b0c5dfbbbf707717dbabe97f4698d7d09f8f3`; publisher `44097198739` SUCCESS.
- [v10.21-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r1) опубліковано як Test prerelease; tag exact source `c5e17aec02e60d8b87fc518165b7f62086dc5a9f`; рівно 6 uploaded assets: 4 Portable + START + SHA256.
- Stable/GitHub Latest лишається **v10.20-r5**, 8 assets. Файли/статуси/backup не змінювались; без КЕП/e-signature, auto «підписано», physical purge, migration, нових бізнес-статусів або залежностей.
- **10.21-r2 не розпочата.** Наступний крок визначати лише після fresh recovery. Детальний аудит: `docs/maintenance/AUDIT_DOCUMENT_SCAN_FILTER_10_21_R1.md`.

## 17.11.2026 — 10.20-r10: заміна скана зі збереженням історії

- PR #486 з виправленням RELEASE_INDEX перевірено й інтегровано: `2aa5f104d2b74a3e23fefbee626ae9e814adec87`. Fresh verification всіх refs виявив уже розпочату r10 гілку `6b798332c18c1adbe2ad299020c7b06e16867b70`, попри старий HANDOFF «не розпочата». Існуючу роботу збережено, дублювання не створювалось.
- Один slice #289: явна «Замінити…» для активного скана. Попередній файл фізично зберігається, історія показує «Замінено», full backup/restore зберігає обидві копії.
- Завершено legacy version guards; їхня предметна логіка не змінена. Додано відмову заміни неактивного скана, дві помилки запису/відкату без втрати байтів, tamper detection старого файла, реальне Tk-скасування/відмову і геометрію кнопок на 900×600 / 1024×700 / 1366×768 зі збільшеним шрифтом.
- Перша відновлена перевірка Win7 знайшла несумісний з Python 3.8 виклик `nametofont(root=...)` у новому тесті; виправлено через сумісний `Font(..., exists=True)`, без зміни продукту.
- Product PR #487 merged / exact immutable release source: `4661c929c2056f449a30152ed7fb231b1c9ba553`; final product head `c09842704889a1da1fab00e5280aa7561daa7ad6`. Release notes включено у product PR.
- Exact-source CI: START `44086412942` — **1430/1430**; Windows `44086412912`; Win7 `44086412809`; macOS Intel/ARM `44086412799` — SUCCESS. Defender та post-scan integrity PASS.
- Trigger PR #488 змінює лише HANDOFF і кінцевий перенос рядка stable marker (значення `10.20-r5` незмінне); merged `71f5bec74f2dad469a0dc7c67be1d232db77bf89`. Publisher `44087486860` SUCCESS.
- [v10.20-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r10) опубліковано як Test prerelease; tag exact source `4661c929c2056f449a30152ed7fb231b1c9ba553`; рівно 6 uploaded assets: 4 Portable + START + SHA256.
- Stable/GitHub Latest лишається **v10.20-r5**, 8 assets. Без КЕП/e-signature, auto «підписано», physical purge, migration, нових бізнес-статусів або залежностей.
- Scan-filter відкладений і не реалізований. **10.21-r1 не розпочата**; наступний крок визначати після fresh recovery. Детальний аудит: `docs/maintenance/AUDIT_DOCUMENT_SCAN_REPLACEMENT_10_20_R10.md`.

## 17.11.2026 — 10.20-r9: індикатор активних сканів у каталозі документів

- Після fresh recovery з `main` `8743f964ce30740b463defe2c3cc1663cb883926` r8 не повторювали; вибрано один bounded slice Issue #289.
- У загальному вікні «Документи» додано колонку «Скани»: для DocumentVault показується «Немає» або «Є: N» за активними сканами. Прибрані у r8 скани не рахуються.
- Пошкодження/помилка перевірки сховища сканів не приховує каталог: показується «Помилка перевірки». КЕП, auto «підписано», physical purge, migration і нові формати даних не додавались.
- Перший START CI на проміжному head виявив 41 legacy version-guard із верхньою межею 10.20-r8. Оновлено тільки дозволи поточної версії; предметна логіка старих тестів не змінювалась.
- Product PR #482 merged as `3669470cd80304f0f82f6eb542664e59fbfcca1e`; final product head `e490e1cdac9624d288ae38cceab08e306bafeb25`.
- Release-notes PR #483 merged; exact release source `a607024d25557136b92c5de4a91ee1d6c7e8b1e1`.
- Exact-source CI: START `44074962416` — **1419/1419**; Windows `44074962450`; Win7 `44074962376`; macOS Intel/ARM `44074962435` — SUCCESS; Defender/integrity PASS.
- Release-trigger PR #484 merged as `d16617ed7e094405ece7e8bb90eecd3bd778b429`; publisher `44076489530` SUCCESS.
- [v10.20-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r9) published as immutable **Test Portable** prerelease, exactly 6 assets, tag target exact source `a607024d...`.
- Stable/GitHub Latest remains **v10.20-r5**, 8 assets.
- **10.20-r10 не розпочата.** Наступний bounded slice визначати лише після нового live recovery.

## 16.11.2026 — звірка після переведення 10.20-r5 у Stable

- Live GitHub показав новіший стан, ніж HANDOFF: за рішенням власника PR #470 перевів історичний checkpoint **10.20-r5** у Stable/Latest.
- Початкове підвищення існуючого portable-only prerelease не могло сформувати повний stable-комплект; PR #472 виправив цей шлях. PR #473 закрито як дубль.
- Workflow `43910071886` на main `5e8b65e71ba502fc2116584027881fab099d79fe` — SUCCESS. GitHub Latest тепер [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5), exact source `8a56a2da438777e1fa4549ad2a63883a2ac67e31`, 8 assets.
- 10.20-r6 лишається Test prerelease і поточною інтегрованою продуктовою ревізією main.
- Виявлено, що **10.20-r7 уже реалізована** у draft PR #471, head `bd2ff059f88f38a50e730705a785dce1bf91e962`; START/Windows/Win7/macOS перевірки SUCCESS. Реалізацію не повторювати.
- Гілка r7 відстає від main лише на службові stable-promotion файли; продуктових конфліктів не виявлено.
- Поточні README, переклади, QUICK_START, recovery/state і release index приведено до фактичного Stable r5. Історичні release notes не переписуються.
- Наступна дія: після merge цього recovery/docs checkpoint повторно звірити PR #471 і інтегрувати готову r7, якщо live GitHub лишається зеленим.

## 16.11.2026 — 10.20-r6: додавання і перегляд списку сканів

- У звичайному вікні «Документи» для документа зі сховища додано «Скани…».
- Вікно показує назву, тип, розмір і SHA-256 прикріплених сканів та дозволяє додати PDF/JPG/JPEG/PNG/TIFF.
- Копіювання виконується у фоні; після успіху список оновлюється.
- Використовується захищене зберігання r5; скан не змінює бізнес-статус документа і не означає «підписано».
- Product PR #466 merged as `aae93d168b0054cb106d8bfc9f58e1e766827f81`; final product head `a0ac440e744ee05b01dd97c43aa8f4cc04e5e7d5`.
- Release-notes PR #467 merged; exact release source `5e2155e281f70dade77c5e4280a75b6634a31ffb`.
- Exact-main: 1404/1404; START `43902826028`; Windows `43902825913`; Win7 `43902826046`; macOS Intel/ARM `43902825971` — SUCCESS; Defender/integrity PASS.
- Release-trigger PR #468 merged as `60078a8193efc309e0ff509cef64b7452d452796`; publisher `43904948481` SUCCESS → [v10.20-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r6), 6 files. Stable/Latest v10.18-r3 unchanged.
- Наступний крок **10.20-r7**: явне «Відкрити» для вибраного скана після повторної перевірки файла; без автоматичного відкриття, КЕП, «підписано» чи міграції.

## 16.11.2026 — 10.20-r5: основа для сканів паперових оригіналів

- Додано безпечне зберігання добровільного скана як окремого незмінного вкладення до конкретного документа у сховищі.
- Підтримано PDF, JPG/JPEG, PNG, TIFF; перевіряється фактичний формат файла.
- Для вкладення зберігаються власний ID, розмір і SHA-256. Повтор того самого файла до одного документа блокується; підміна збереженого файла виявляється.
- Повна резервна копія та відновлення зберігають документ разом зі сканом.
- Наявність скана не означає «підписано»; КЕП і UI-кнопка не входили в r5.
- Product PR #462 merged as `b569bb012981956389feb8e66bfbcd19359c5ea8`.
- Release-notes PR #463 merged; exact release source `8a56a2da438777e1fa4549ad2a63883a2ac67e31`.
- Exact-main: 1400/1400; START `43894675169`; Windows `43894675281`; Win7 `43894675146`; macOS Intel/ARM `43894675212` — SUCCESS; Defender/integrity PASS.
- Release-trigger PR #464 merged as `c0773f1cb88fb132fcda794cab727e70a618c7ca`; publisher `43896901808` SUCCESS → [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5), 6 files. Stable/Latest v10.18-r3 unchanged.
- Наступний крок **10.20-r6**: кнопка «Додати скан…» + read-only перелік вкладень у звичайному документному шляху; без КЕП, автоматичного «підписано» і міграції.

## 16.11.2026 — 10.20-r4: єдиний список документів зі сховищем

- DocumentVault підключено до звичайного вікна «Документи».
- Той самий контрольований Word-документ у PaperDocuments + Vault показується одним рядком «Word + сховище» лише за точним ID-зв'язком; назва/дата не використовуються для автоматичного злиття.
- Додано фільтр «У сховищі», колонку «Джерело» і оновлення списку одразу після збереження у сховище.
- Помилка читання сховища не приховує справні Word-документи або накази.
- Під час оновлення старих перевірок версій була технічна помилка в тестових файлах; її виправлено до інтеграції. Після виправлення повний набір — 1390/1390.
- Product PR #458 merged as `7991806cedb3b2a19db431a40145f6fbab42d00c`; final product head `e9fa93d17d9e5508d59dcd22ec4fcde1aef5a0cb`.
- Release-notes PR #459 merged; точне джерело релізу `e38cb58a48e7d9b10f9b5d5006fed937b79c259e`.
- Перевірки: START `43849898433` — 1390/1390; Windows `43849898492`; Win7 `43849898530`; macOS Intel/ARM `43849898512` — SUCCESS; Defender/integrity PASS.
- Release-trigger PR #460 merged as `7678f720e2f8a4d8ae9f398b0371c941a16e4531`; publisher `43851460354` SUCCESS → [v10.20-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r4), 6 assets. Stable/Latest v10.18-r3 unchanged.
- Наступний крок **10.20-r5**: основа для добровільних сканів паперових оригіналів як окремих незмінних вкладень до документа; без UI, КЕП, автоматичного «підписано» або міграції старих документів.

## 16.11.2026 — 10.20-r3: DocumentVault UI bridge

- Recovery виявив уже розпочату гілку `work/v10.20-r3-document-vault-ui`; реалізацію не повторювали, а продовжили з фактичного head.
- Додано явну дію збереження вибраної контрольованої prepared DOCX-редакції у чинний DocumentVault та окремий read-only browser/list/detail.
- Картка показує title/kind/date/status, revision, PaperDocuments/PreparedDocuments/CompanyTemplate provenance та exact SHA-256. Vault record не трактує файл як «підписано» чи інший бізнес-факт.
- Запис виконується через r2 immutable core поза Tk UI thread; duplicate/tamper/index/object/hash помилки лишаються fail-closed. `main.py` не роздувався.
- Перший CI на проміжному head знайшов лише два пропущені historical VERSION.txt guards; їх доповнено без зміни функціональної логіки. Final product head `b5fd4e2a4223d3cfef2d1ea09279b7e7cee3a376`.
- Product PR #454 merged as `42e7a1d71fbf80cc1b4c85551bb710d2f4d13496`. Release-notes PR #455 merged; exact product/release source `eec360a965738ecab97f38aeaa5ab8a7452ee1dd`.
- Exact-main CI: START `43842526461` — 1385/1385; Windows `43842526290`; Win7 `43842526261`; macOS Intel/ARM `43842526193` — SUCCESS; Defender/integrity PASS.
- Release-trigger PR #456 merged as `fefeb885b81b54709e69010a1251051ef7faf842`; publisher `43844149251` SUCCESS → [v10.20-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r3), exactly 6 assets, target exact source SHA. Stable/Latest v10.18-r3 unchanged.
- Наступний bounded slice **10.20-r4**: DocumentVault як read-only source у чинному агрегованому каталозі «Документи» + exact provenance-based dedupe PaperDocuments/Vault; без migration/scans/signatures/business-status changes.

## 16.11.2026 — 10.20-r2: DocumentVault core

- Після recovery 10.20-r1 реалізовано один bounded slice без повторення prepared DOCX/PDF шляху.
- Додано окремий `document_vault_store.py` з workspace-relative `Data/DocumentVault`, immutable object storage та index schema `taxo.document-vault-index.v1`.
- Exact prepared DOCX-редакція реєструється лише явно; зберігаються PaperDocuments ID, prepared snapshot, document family/revision, CompanyTemplate provenance, exact SHA-256, title/kind/date і status `ready|archived`.
- Заборонено дублікати; tampered index/object, unknown fields, orphan files і source/hash mismatch виявляються fail-closed.
- Не додано auto-migration, scans/originals, signature evidence, digital signature чи implicit «підписано». UI навмисно не входив у цей core slice.
- Додано 10 нових regression tests; загальний exact-main набір — 1379/1379.
- Product PR #449 merged; final head `633922f32f4594fc0b6b4db9b8ed181fc4306447`, product merge `1519ebda983649a524a03fe0d14c8924d53fe2ff`.
- Release-notes PR #450 merged; exact product/release source `21eb1f668fbd6e915321afe40e2c78d105cdd48b`.
- Exact-main CI: START `43832998489`; Windows `43832998423`; Win7 `43832998510`; macOS Intel/ARM `43832998365` — SUCCESS; Defender/integrity PASS.
- Release-trigger PR #451 merged as `8ec2d07c4e7332748e419e9c7fad1eb6384888df`; publisher `43834523785` SUCCESS → [v10.20-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r2), 6 assets, exact product target. Stable/Latest v10.18-r3 unchanged.
- Наступний bounded slice **10.20-r3**: окремий UI-міст prepared revision → DocumentVault і read-only list/detail; без migration/scans/signatures/implicit signed status.

## 15.11.2026 — 10.20-r1: inline images у prepared DOCX → PDF/print

- Після recovery 10.19-r10 номерна лінія коректно перейшла на 10.20-r1.
- Додано окремий `prepared_document_pdf_images.py`: безпечне вилучення/нормалізація inline-зображень із exact контрольованого DOCX.
- Підтримано inline image у body paragraphs та table cells; text/image order і базове paragraph alignment переносяться у ReportLab story.
- Безпека: limits на image count, compressed blob size, pixel count і normalized payload; зовнішні linked images не завантажуються.
- Fail-closed лишено для floating drawings, VML/legacy pictures, header/footer drawings, nested/complex table layout. Непідтримані конструкції не губляться мовчки.
- Перший CI failure був лише historical r10 guard, який вимагав відхиляти **всі** images; guard еволюціоновано так, щоб нові safe inline images дозволялись, а unsupported layouts лишались fail-closed.
- Product PR #446 merged; final head `1037f5923293ca4c265067537cd19cb6aa5ef589`, exact product/release source `f80a1e583f896f4d0d8f63265e7ab0aadb657185`.
- Exact-main CI: START `43761081149` — 1369/1369; Windows `43761081164`; Win7 `43761081155`; macOS Intel/ARM `43761081179` — SUCCESS; Defender/integrity PASS.
- Release-trigger PR #447 merged as `9fc246f335da4c3853e891a219fc7fdc8d839f6a`; publisher `43762135252` SUCCESS → [v10.20-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r1), 6 assets, exact product target. Stable/Latest v10.18-r3 unchanged.
- Наступний bounded slice **10.20-r2**: DocumentVault core — storage/registry + provenance link to prepared revision; без migration/scans/signatures/implicit signed status.
- Через повторні `Error in input stream` наступний великий slice переноситься у новий чат після recovery checkpoint.

## 15.11.2026 — 10.19-r10: назва підприємства з БД та prepared PDF/друк

- За зауваженням власника `company.name` у формі CompanyTemplates більше не вимагає дублювання, якщо значення є у таблиці `company` активного workspace. Це editable default конкретної чернетки; TemplateLibrary/CompanyTemplates не мутуються.
- Додано `prepared_document_pdf.py` і дію «PDF / друк…» у каталозі контрольованих prepared DOCX. PDF береться саме з вибраної r1/r2/r3, записується окремо в Output і відкривається існуючим Taxo viewer/Print.
- PDF path не змінює DOCX, history, prepared/signature/business status і не вводить DocumentVault. Нових залежностей нема: python-docx + ReportLab.
- Під час pre-merge macOS ARM regression виявив, що системний шрифт може бути symlink. Перевірку виправлено без послаблення вимоги до реального font file; final head `14d41a88fd622547f04ef4eebc07a061210d51a3`.
- Embedded images у r10 fail-closed: Taxo відмовляється робити неповний PDF і радить Word, доки image/layout fidelity не реалізована окремо.
- Product PR #443 merged; exact product/release source `ff93ab2ddfe92f4eb8079d890ad8e7ffd7fe03e2`.
- Exact-main CI: START `43757634383` (1362/1362), Windows `43757634381`, Win7 `43757634387`, macOS Intel/ARM `43757634384` — SUCCESS; Windows/Win7 Defender та integrity PASS.
- Release-trigger PR #444 зберіг semantic Stable marker `10.18-r3`; publisher `43758634481` SUCCESS → [v10.19-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r10), рівно 6 assets, target exact product SHA. Stable/Latest v10.18-r3 не змінено.
- Після r10 номерна лінія переходить на **10.20-r1**. Наступний bounded slice: embedded images у prepared PDF/print; DocumentVault/скани/підписи окремо.

## 15.11.2026 — 10.19-r9: повторне відкриття чернеток і історія Word-редакцій

- Продовжено шлях документа після r8 без повторення збереження DOCX у каталог.
- Додано окремий список збережених `PreparedDocuments`: після перезапуску Taxo snapshot можна знайти, переглянути, повторно експортувати в DOCX або явно зареєструвати в каталозі без повторного заповнення шаблону.
- Prepared DOCX редагується через окрему зовнішню копію. Відредагований Word-файл імпортується як нова незмінна редакція r2/r3…, старий файл не перезаписується. Каталог зберігає family ID, revision, previous document ID і content SHA-256.
- Пряме редагування prepared-файла з каталогу заблоковано на UI-шляху; імпорт перевіряє DOCX, відхиляє незмінений файл, небезпечні ZIP-шляхи та спробу імпортувати сам файл каталогу.
- Додано спільний lock запису PaperDocuments та regression на паралельні записи, щоб два вікна Taxo не втрачали записи `index.json`.
- Під час pre-merge CI знайдено лише пропущений historical version guard r7; виправлено до інтеграції. Final PR head `1e9a6e6b1ea5d81ae3ad4445c3213a935ff5007c` пройшов START/Windows/Win7/macOS; Defender/integrity PASS.
- Product PR #440 merged; exact product/release source `bc2bb95d26f0d89d40acb98a3c37efaee6ab060b`.
- Exact-main CI: START `43753739079`, Windows `43753739074`, Win7 `43753739194`, macOS Intel/ARM `43753739130` — SUCCESS; Windows/Win7 Defender та integrity PASS.
- Release-trigger PR #441 зберіг semantic Stable marker `10.18-r3`; publisher `43754690935` SUCCESS → [v10.19-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r9), рівно 6 assets, target exact product SHA. Stable/Latest v10.18-r3 не змінено.
- Наступна дозволена ревізія **10.19-r10**: PDF/print із вибраної контрольованої prepared-редакції; DocumentVault, скани та підписні докази — окремо.

## 15.11.2026 — 10.19-r8: DOCX до каталогу документів

- Власник виявив розрив між експортом Word та реєстром документів. Змінено план r8 з PDF/print на цю практичну проблему.
- `prepared_document_registry.py`: явний запис immutable snapshot-backed DOCX у чинний PaperDocuments без бізнес-факту чи статусу підпису.
- У PaperDocuments index збережено source snapshot ID, CompanyTemplates ID, source revision/SHA, `document_status=prepared`. Без перезапису старих записів; дублі того самого snapshot відхиляються.
- UI preview: кнопка «Зберегти DOCX у каталозі Taxo» доступна лише після успішного збереження snapshot. Окремий зовнішній експорт DOCX працює як раніше.
- Product PR #437 merged; exact SHA `4829bc7e3369442cc7cee7ad9ec8797fc26362e5`.
- Exact-main CI: START `43747281993`, Windows `43747281941`, Win7 `43747281957`, macOS Intel/ARM `43747281991` — SUCCESS; обидва Windows Defender і integrity PASS.
- Release PR #438 merged; publisher `43748041618` SUCCESS → [v10.19-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r8), 6 файлів, exact source SHA. Stable/Latest v10.18-r3 не змінено.
- Наступна 10.19-r9: перелік збережених prepared snapshots та безпечний імпорт відредагованого DOCX з історією, без заміни старого файла. PDF/print, скани та повний DocumentVault — окремо.

## 14.11.2026 — 10.19-r7 завершено й опубліковано

- DOCX export із immutable PreparedDocuments snapshot; окремий модуль, без повторного читання поточного шаблону, зі збереженням exact provenance.
- Product PR #434 merged, exact product SHA `0cfccee73eec9bcf0fbb07afc64c5d7a7949dfcc`.
- Exact-main START `43625038373`, Windows `43625038453`, Win7 `43625038422`, macOS Intel/ARM `43625038460` — SUCCESS. Windows/Win7 Defender та integrity PASS.
- Release PR #435 merged; publisher `43627285299` SUCCESS; [Test prerelease v10.19-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r7) містить 4 Portable + START + SHA256 і вказує точно на product SHA.
- Stable/Latest v10.18-r3 не змінено. Наступна дозволена 10.19-r8, PDF/print окремо від фінального архіву.
- Recovery після chat delivery timeout: з’ясовано, що GitHub продовжив і завершив PR #434 та main-builds, отже повторних збірок не запускали; закінчено вже підготовлений release PR #435.

## 14.11.2026 — 10.19-r6 recovered, integrated and released

- Recovery після нестабільного чату почався з live GitHub. Документи ще вказували r5 як завершену, але фактично вже існувала незавершена гілка `work/v10.19-r6-prepared-snapshot`; номер r6 не перевикористовувався і робота не починалась заново.
- Незавершена r6 вже містила immutable prepared-document snapshot storage. Після обриву лишилися застарілі historical version/START guards та один текстовий static guard; їх узгоджено без зміни snapshot design. Final branch exact head `1535bd7f92facf2d636f9dc7e656653a6eea1a24`.
- r6 додає explicit save підготовленої CompanyTemplates-чернетки в `Data/PreparedDocuments`: exact template ID/SHA/edit revision, normalized facts, rendered structure/content, SHA-256/size integrity index, atomic write, immutable API boundary і backup/restore coverage. Немає автоматичного business fact, DOCX/PDF, final archive, scan/signature side effects.
- Product PR #431 merged; exact product/release source `eca31f5d61fc382cebc4663ec511619b9dcd69e7`.
- Exact-main CI: START `43622027078`, Windows `43622027016`, Win7 `43622027066`, macOS Intel/ARM `43622027010` — SUCCESS. Windows і Win7 Microsoft Defender та post-scan integrity — PASS.
- Release trigger PR #432 зберіг semantic Stable marker `10.18-r3` і запустив existing guarded publisher. Publisher `43622926821` SUCCESS → immutable [v10.19-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r6), target exactly `eca31f5d61fc382cebc4663ec511619b9dcd69e7`, 6 assets (4 Portable + START + SHA256).
- GitHub Latest/Stable лишається [v10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3).
- Наступна кодова ревізія після recovery checkpoint: **10.19-r7**, окремий DOCX renderer/export з immutable prepared snapshot-а; PDF/print і DocumentArchive — пізніші окремі slices.

## 14.11.2026 — 10.19-r5 integrated and released

- Exact product/release source `0ab0cc761078b38e391c1998ddf9feee7447d3a8`.
- Added user-facing CompanyTemplates flow: typed fact form backed by current employee/driver/vehicle registries, stable-ID snapshots, participant multi-select, explicit driver–vehicle pairs and read-only in-memory preview.
- Self-audit before merge found a weaker pair rule in the first r5 draft. Fixed before integration: one vehicle may have several drivers, one driver cannot be assigned to several different vehicles in one draft set, exact duplicate pairs are rejected. Regression covers both allowed and rejected cases.
- Tk values are collected only on UI thread; renderer workers receive plain Python facts. Stale form is rejected by exact source SHA guard. Registry adapter performs no SQL writes.
- PR #428 strict ruleset initially blocked merge because branch was behind main by 5 recovery commits. Verified zero changed-file intersection: main changed only HANDOFF/PROJECT_STATE/WORKLOG/RELEASE_INDEX. Main was merged into r5 with an ordinary two-parent merge commit, no force; required Windows check then PASS.
- Exact-main CI: START `43614552144`, Windows `43614552146`, Win7 `43614552095`, macOS `43614552161` — SUCCESS; Defender/integrity PASS.
- Release trigger PR #429 used existing guarded publisher. Publisher `43615561706` SUCCESS → immutable [v10.19-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r5), target exactly `0ab0cc761078b38e391c1998ddf9feee7447d3a8`, 6 assets (4 Portable + START + SHA256). Stable/Latest remains [v10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3).
- Next code revision: **10.19-r6**, immutable snapshot of a filled draft as an intermediate document state; no automatic business fact, DOCX/PDF, DocumentArchive, scan or signature in the same slice.

## 14.11.2026 — 10.19-r4 integrated and released

- Exact product/release source `a408ddbea823defdc91d1dd562e99ebddd032622`.
- Added typed fact normalization and separate structural in-memory renderer for CompanyTemplates.
- Preview is write-free: no template mutation, main DB write, business fact, DocumentArchive or DOCX/PDF output.
- Exact-main CI: START 43607027278, Windows 43607027231, Win7 43607027233, macOS 43607027263 — SUCCESS; Defender/integrity PASS.
- Publisher 43607894395 SUCCESS → immutable `v10.19-r4 — Test Portable`, 6 assets.
- Intermediate regex escaping defect found by CI during module split was fixed before merge/release; final release source is correct.
- Next code revision: **10.19-r5**, fact-entry/selection UI + in-memory preview only.

## 14.11.2026 — 10.19-r3 editor threading fix integrated and released

- After v10.19-r2 publication, static review found one UI-thread defect: the CompanyTemplates save worker read Tk `StringVar` through `title.get()` from a background thread. This was a thread-safety risk, not a deterministic CI failure.
- Corrective PR #422 produced 10.19-r3 only: title is captured on the Tk/UI thread before worker start; the worker receives a plain Python string. Regression guard prevents Tk variable access from the save worker. No new product feature was added.
- Exact product/release source: `a89291553bca88a1b792d45f56cc99d5e93876b7`.
- Exact-main CI: START `43598231924`, Windows `43598231921`, Win7 `43598231945`, macOS Intel/ARM `43598231954` — SUCCESS. Windows and Win7 Defender + post-scan integrity — PASS.
- Release trigger PR #423 used the guarded publisher. Publisher `43599116472` SUCCESS → immutable prerelease [v10.19-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r3), 6 assets, target exactly `a89291553bca88a1b792d45f56cc99d5e93876b7`. Stable/Latest remains [v10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3).
- Issued v10.19-r2 was not overwritten or reused; release index marks it superseded by r3 for the UI-thread fix.
- Next product revision after recovery: **10.19-r4**, typed fact substitution into a selected CompanyTemplates revision and an in-memory preview draft; no DOCX/PDF/DocumentArchive in the same slice.

## 14.11.2026 — 10.19-r2 editor integrated and released

- PR #419 integrated the second CompanyTemplates slice; exact product/release source `6414e0fbeeca3f60d8bf609bc15fbf66482e5e82`.
- Added separate company-template list, structured text editor and versioned storage updates. Vendor `TemplateLibrary` remains read-only. Save writes a new company revision file and atomically moves the current index; the previous file is preserved. SHA-256 optimistic concurrency rejects stale silent overwrites.
- Editable surface is limited to user-visible text: title/description, block text/notes, list items, static-table text and appendices. IDs, block types, variables, data sources and provenance remain structural. Large instruction text roundtrip is covered.
- UI has Save/Cancel/X unsaved-change protection and background load/save workers. Storage, service, list UI and editor UI remain separate from `main.py`.
- Exact-main CI: START `43595242155`, Windows `43595242166`, Win7 `43595242114`, macOS `43595242059` — SUCCESS. Windows and Win7 Defender + post-scan integrity — PASS.
- Release trigger PR #420 used the existing guarded publisher without changing Stable semantics. Publisher `43595998112` SUCCESS → immutable prerelease [v10.19-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r2), target exactly `6414e0fbeeca3f60d8bf609bc15fbf66482e5e82`, 6 assets (4 Portable + START + SHA256).
- Stable/Latest remains [v10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3).
- Next code revision after recovery checkpoint: **10.19-r3** — typed fact substitution and a non-persistent document draft/preview; no final archive side effects.

## 14.11.2026 — 10.19-r1 integrated, released; full-build release rule changed

- PR #414 integrated product checkpoint 10.19-r1; exact product/release source `c1357d6ba84e521bfa332f99024fbc85c8304ec3`.
- r1 adds separate `CompanyTemplates` copies while vendor `TemplateLibrary` remains read-only; provenance/integrity, duplicate guard and template-zone backup checks are covered. Editor/Word/PDF/DocumentArchive remain for later revisions.
- Exact-main CI: START `43592182090`, Windows `43592182079`, Win7 `43592182138`, macOS `43592182091` — SUCCESS. Windows and Win7 Microsoft Defender gates and post-scan integrity checks — PASS.
- Release trigger PR #416 used the existing guarded publisher without changing Stable semantics. Publisher `43592683925` SUCCESS → immutable prerelease [v10.19-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r1), target exactly `c1357d6ba84e521bfa332f99024fbc85c8304ec3`, 6 assets (4 Portable + START + SHA256). Stable/Latest remains [v10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3).
- Owner changed release policy: when a new revision already has successful START + Windows + Windows 7 + macOS Intel + macOS ARM builds on one exact source SHA and required security/integrity gates pass, publish a Test prerelease from those completed exact-SHA artifacts if an immutable release does not already exist. Do not rebuild only for publication; never promote Stable automatically.
- PR #417 integrated this rule into `PROJECT_RULES.md`; stale PR #415 closed as superseded.
- Next code revision after recovery checkpoint: **10.19-r2**, editor for user-owned `CompanyTemplates` copy; vendor source remains untouched.

## 10.11.2026 — уточнення документації випуску 10.15-r4

- Після публікації встановлено: tag `ae0c673a42c5b633706efdffc1adfd5b1b70681d` створює START з документацією до PR #305. README у випущеному START містить застарілий стан r3, включно з помилковим твердженням про неопублікований r3.
- Актуальні описи й переклади вже в main; immutable тег і release не перезаписувалися. Включити актуальну документацію до наступної кодової ревізії.

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


## 11.11.2026 — recovery checkpoint після 10.15-r10

- За рішенням власника уточнено критерій перебудови: скорочення `main.py` не є метою; Taxo має рости, але домени слід будувати в окремих зрозумілих модулях і оформлювати код так, щоб його могла нормально читати людина.
- Незлита структурна лінія доведена до 10.15-r10, draft PR #325, exact head `05cb7341146f46e2a2233b6966b85ed670b0b8f7`. Реєстр працівників і картку працівника винесено в `employee_registry_ui.py` із сумісними App-adapters.
- Після виправлення технічної помилки переносу й перенаправлення 7 старих source-location regression tests усі вимоги залишилися активними. Exact r10: Windows 42996976591 SUCCESS, 1097 tests; Win7 compatibility 42996977191 SUCCESS, 1097 tests; macOS 42996976642 Intel + ARM SUCCESS, 1097 tests кожна. Windows START preflight та incomplete-package guard SUCCESS.
- Окремий START artifact r10 не створено; ручні тестові архіви під час перебудови дозволено групувати більшими етапами. Не видавати START preflight за готовий архів.
- r7/r8/r9/r10 не merged і не stable. Stable лишається v10.15-r4; r5 — робоча rollback/reference точка. Наступна кодова ревізія — 10.16-r1.
- `HANDOFF_CURRENT.md` та `PROJECT_STATE.md` оновлено, бо попередній PROJECT_STATE помилково вказував r6 як наступну ревізію.


## 11.11.2026 — 10.16-r1: поділ центру наказів за відповідальностями

- На гілці `work/v10.16-r1-operations-center-modules` (draft PR #327) налаштування відповідальних/місця/нумерації винесено в `operations_settings_ui.py`, каталог типів наказів — у `order_type_catalog_ui.py`.
- Мета — не зменшення рядків, а запобігання другому моноліту. `operations_orders_ui.py` лишився координатором + реєстром наказів; нові модулі оформлено читабельно.
- Кодовий head `81fd6740bed0e1fe32a2503d45c924a5c8f98ac7`: Windows 42999564972 SUCCESS, 1103 tests; Win7 compatibility 42999565006 SUCCESS, 1103 tests; macOS 42999564999 Intel + ARM SUCCESS, 1103 tests. Після синхронізації форматування PROJECT_STATE поточний head PR #327 — `5971bd57c00d919c70247f7fb55298c9fe263add`; код не змінено, повторні regression-перевірки Windows/Win7 compatibility/macOS Intel+ARM також SUCCESS.
- Під час regression виявлено 4 старі source-location тести; їх перенаправлено без послаблення вимог. Також повернуто випадково втрачений історичний anchor Taxo 10.3 у PROJECT_STATE через docs PR #328.
- r1 не merged/stable. Stable v10.15-r4, r5 rollback/reference. Наступна кодова ревізія — 10.16-r2.


## 11.11.2026 — 10.16-r2: окремий реєстр наказів

- Від exact verified r1 створено `work/v10.16-r2-order-register`, draft PR #331; recovery docs синхронізовано перед кодовою зміною.
- Реєстр наказів (список, фільтр, дії, історія, preview/друк, зв'язок із закріпленнями та учасниками) винесено в `order_register_ui.py`. Через `OrderRegisterController` coordinator отримує лише чотири потрібні дії. `operations_orders_ui.py` тепер лише збирає спеціалізовані модулі й оформлений читабельніше.
- Перший regression знайшов реальну runtime-помилку: після перейменування відповідальної змінної один виклик editor лишив `operations_resp_var`; створення наказу падало з NameError й каскадом ламало живі тести закріплень. Виправлено; source-location tests перенаправлено на новий модуль без послаблення вимог.
- Exact final head `baf785b95bc32403e9b7a7a888dfc7b23766d1dc`: Windows 43002030779 SUCCESS, 1108 tests; Win7 compatibility 43002030767 SUCCESS, 1108 tests; macOS 43002030758 Intel + ARM SUCCESS, 1108 tests кожна. Windows START preflight та incomplete-package guard SUCCESS.
- Artifacts: Windows 13847301165; Win7 compatibility 13846587755; macOS ARM64 13847340326; macOS x86_64 13845959220.
- r2 не merged/stable. Stable v10.15-r4; r5 rollback/reference. Наступна кодова ревізія — 10.16-r3.


## 11.11.2026 — 10.16-r3: окремий реєстр і картка водія

- Від exact verified r2 створено `work/v10.16-r3-driver-registry-ui`, draft PR #333; recovery docs синхронізовано перед кодовою зміною.
- У `driver_registry_ui.py` винесено реєстр водіїв, картку, створення/редагування, завершення/виправлення ролі та базове завантаження. Табельні й атестаційні списки водіїв навмисно лишено поза модулем як окремі відповідальності.
- Стару стислу картку розгорнуто в читабельні секції та явні залежності. `main.py` приблизно 15857 → 15558 рядків лише як наслідок поділу; новий модуль близько 821 рядка.
- Перший regression знайшов 2 source-location checks (driver_form/build_drivers у main.App); їх перенаправлено на новий модуль без послаблення правил завершення ролі й `driver_end_date`.
- Exact final head `2caaafb390bb9040ec7c65b4ca5dbb7292d81a94`: Windows 43004222187 SUCCESS, 1114 tests; Win7 compatibility 43004222283 SUCCESS, 1114 tests; macOS 43004222630 Intel + ARM SUCCESS, 1114 tests кожна. Windows START preflight та incomplete-package guard SUCCESS.
- Artifacts: Windows 13847841763; Win7 compatibility 13846489953; macOS ARM64 13846744008; macOS x86_64 13847228709.
- r3 не merged/stable. Stable v10.15-r4; r5 rollback/reference. Наступна кодова ревізія — 10.16-r4.

## 11.11.2026 — 10.16-r4: окремий UI документів транспортних засобів

- Від exact verified r3 `2caaafb390bb9040ec7c65b4ca5dbb7292d81a94` створено `work/v10.16-r4-vehicle-documents-ui`, draft PR #335.
- CRUD-вікно документів ТЗ і загальний контроль документів винесено в `vehicle_documents_ui.py`. `vehicle_documents.py` лишив схему, статуси, строки дії, report data/export, копіювання файлів і сумісні точки входу; `vehicle_registry_ui.py` явно підключає UI-модуль.
- Мета — модульність і читабельність, не зменшення рядків. DB schema, backup/restore, формати робочих даних і правила документів не змінювались.
- Перший START regression виявив 24 історичні прив'язки: 19 version allowlists не знали r4, 5 source-location checks шукали UI у старому файлі. Тести перенаправлено/розширено без послаблення поведінкових вимог.
- Exact final head `a3509473ec3d884ec18bbbceb07fa78dd24ad3b3`: START/source 43015674097 SUCCESS, 1119 tests; Windows 43015867380 SUCCESS, 1119 tests; Win7 compatibility 43015867350 SUCCESS, 1119 tests на Python 3.8; macOS 43015867478 Intel + ARM SUCCESS, 1119 tests кожна. Windows START preflight та incomplete-package guard SUCCESS.
- Artifacts: START 13852362721; Windows 13852962058; Win7 compatibility 13851949739; macOS x86_64 13853106845; macOS ARM64 13852288612.
- Через docs-only divergence основного cumulative PR платформні PR-only workflows перевірено через тимчасовий validation PR #336 до exact r3; PR #336 закрито без merge після SUCCESS.
- r4 не merged/stable. Stable лишається v10.15-r4; r5 — rollback/reference. Наступна кодова ревізія — 10.16-r5.

## 11.11.2026 — 10.16-r5: документна межа інструктажів і детермінований каталог

- Від exact verified r4 `a3509473ec3d884ec18bbbceb07fa78dd24ad3b3` створено `work/v10.16-r5-safety-instruction-documents`, draft PR #338.
- У `safety_instruction_document_service.py` винесено документну операцію інструктажу: побудова існуючого editable DOCX, збереження через існуючий `paper_document_store` і відкриття через існуючий cross-platform handler. `safety_instructions_ui.py` лишився UI збору/редагування даних і делегує цю операцію сервісу.
- Це поділ відповідальності, а не скорочення коду. Формат DOCX, каталог `Data/PaperDocuments`, схема БД, backup/restore та правило «підготовлений документ не означає проведення чи підписання» не змінені.
- Перший macOS ARM64 regression виявив історичний live-test, прив'язаний до фізичного місця `safety_instructions_ui.document_store`. Тест перенаправлено на `instruction_documents.open_briefing_document`; реальне створення DOCX і перевірка файла в каталозі залишилися активними.
- Наступний Win7/Python 3.8 regression виявив реальний дефект: два швидко створені документи могли мати однаковий `created_at`, тому stable reverse-sort іноді ставив старіший append першим. `paper_document_store.list_documents()` отримав детермінований tie-breaker за append-позицією; додано окремий regression на однакові timestamps.
- Exact final head `8fa5687012abd6731327bbd65af8df572e017fa4`: Windows 43021465684 SUCCESS, 1125 tests; Win7 compatibility 43021465639 SUCCESS, 1125 tests на Python 3.8; macOS 43021467222 Intel + ARM SUCCESS, 1125 tests кожна. Windows START preflight та incomplete-package guard SUCCESS.
- Artifacts: Windows 13855272500 `Taxo-current-Windows-x64`; regression log 13854499080; Win7 13854479547 `Taxo-current-Windows7-x64`; Win7 build log 13855491714; macOS x86_64 13854264580; macOS ARM64 13855755743.
- Через docs-only divergence cumulative PR платформний CI запущено через validation base `validation/v10.16-r5-base-r4` і PR #339. Після повного SUCCESS PR #339 закрито **без merge**.
- 10.16-r5 не merged і не stable. `main` лишається 10.15-r5; stable — v10.15-r4; 10.15-r5 — rollback/reference. Наступна кодова ревізія — **10.16-r6**.

## 11.11.2026 — 10.16-r6: документна межа стажування

- Від exact verified r5 `8fa5687012abd6731327bbd65af8df572e017fa4` створено `work/v10.16-r6-driver-internship-documents`, draft PR #341.
- У `driver_internship_document_service.py` винесено документну операцію стажування/контрольної поїздки: побудова існуючого editable DOCX, збереження через існуючий `paper_document_store` і відкриття через існуючий cross-platform handler. `driver_internship_ui.py` лишився Tk-формою збору й перевірки даних та делегує документну операцію сервісу.
- Це поділ відповідальності, а не скорочення коду. Формат DOCX, каталог `Data/PaperDocuments`, схема БД, backup/restore та правило «підготовлений документ не означає фактично проведене стажування, підпис чи допуск» не змінені.
- Історичний live-test стажування лишив реальне створення DOCX і перевірку файла в тестовому каталозі, але open-file patch перенаправлено з фізичного `driver_internship_ui.document_store` на новий сервіс.
- Перший START push run `43024216657` виявив одну packaging-прогалину: новий сервіс не був внесений до package guard `START.bat`. Guard додано; бізнес-поведінка не змінювалася.
- Exact final head `21c11679892d47c61118517fe96dc5a3548267f8`: START/source 43024413444 SUCCESS, 1129 tests; Windows 43024422301 SUCCESS, 1129 tests; Win7 compatibility 43024422268 SUCCESS, 1129 tests на Python 3.8; macOS 43024422266 Intel + ARM SUCCESS, 1129 tests кожна. Windows START preflight та incomplete-package guard SUCCESS.
- Artifacts: START 13857285030 `Taxo_v10_16_candidate_r6_START`; Windows 13857145797; regression log 13857155379; Win7 13855789085; Win7 build log 13856487531; macOS x86_64 13857315862; macOS ARM64 13856552190.
- Через docs-only divergence cumulative PR платформний CI перевірено через validation base `validation/v10.16-r6-base-r5` і PR #342. Після повного SUCCESS PR #342 закрито **без merge**.
- Recovery evidence: PR #341 comment 6796510877; Issue #61 comment 6796511722.
- 10.16-r6 не merged і не stable. `main` лишається 10.15-r5; stable — v10.15-r4; 10.15-r5 — rollback/reference. Наступна кодова ревізія — **10.16-r7**.

## 11.11.2026 — визнання 10.15-r5 стабільною версією

- Власник уточнив, що вже прийнята робоча 10.15-r5 мала бути stable. Підтверджено існуючий release з 8 assets і SHA256 та незмінним source SHA `0a5420cb9285ae5a8fc085c2689303d3e070ffbb`.
- Docs/marker PR #346 інтегровано в `main` як `5425175b87c4f7c027bf99a97e23b79e648e97fb`. `.release/stable-current` = `10.15-r5`; release notes більше не називають r5 тестовою.
- Publish workflow 43037738240 — SUCCESS. GitHub API `releases/latest` та `releases/tags/v10.15-r5` підтвердили `Taxo 10.15-r5 — Stable`, prerelease=false, Latest=v10.15-r5. Тег та старі assets не переписувались.
- Для наступних 10.16 власник визначив тестові portable-only випуски (Windows/Win7/macOS Intel/ARM, START/source, SHA256), без публікації інсталяторів. Не інтегрувати код 10.16 у main без окремого рішення.

## 11.11.2026 — 10.16-r7: транзакційне збереження наказів і portable-only prerelease

- Від exact r6 `21c11679892d47c61118517fe96dc5a3548267f8` створено `work/v10.16-r7-order-editor-persistence`, draft PR #344; кодовий exact head `b0d848b86b8344d1064024ca1d3a3f7186adc27c`.
- Додано `order_editor_persistence.py`. Сервіс створює й редагує накази та перевіряє повний запис вибраних пар водій–ТЗ. Tk-редактор зберігає підготовку пар, повідомлення й транзакцію: commit тільки після перевірки, rollback при помилці. Існуючі API, структура БД, шаблони наказів і резервування не змінені.
- Нові regression на масові пари, неповний запис, редагування та створення загального наказу. Exact-head CI: Windows 43036224116 — SUCCESS 1135; Win7 compatibility 43036224099 — SUCCESS 1135 на Python 3.8; macOS Intel/ARM 43036224219 — SUCCESS 1135 на кожній архітектурі.
- START workflow 43036142029 двічі провалився при встановленні `python3-tk` через тимчасову DNS-помилку `azure.archive.ubuntu.com` / `security.ubuntu.com`; source/test stage не виконався, тому не називати цей workflow SUCCESS.
- Окремий release workflow `release/v10.16-r7-portable` перевірив exact code SHA, 3 зелені платформні workflow, сам створив START ZIP із exact SHA, перевірив його склад/чистоту й ZIP integrity. Перший запуск 43038310336 зупинився до публікації на SIGPIPE в release-shell; виправлено тільки isolated release workflow. Другий 43038435601 — SUCCESS.
- Опубліковано immutable [v10.16-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r7) як prerelease, tag `b0d848b86b8344d1064024ca1d3a3f7186adc27c`, рівно 6 assets: Windows x64 portable, Windows 7 x64 portable, macOS x86_64 portable, macOS arm64 portable, START/source ZIP, SHA256. **Без інсталяторів**. Перевірено: GitHub Latest лишається `v10.15-r5`.
- Тимчасовий validation PR #345 закрито без merge. Draft PR #344 залишається незлитим; main код і stable 10.15-r5 не змінені.
- Наступна нова кодова ревізія — **10.16-r8**.

## 11.11.2026 — 10.16-r8: окремий assignment-UI редактора наказу і portable-only prerelease

- На старті сесії live GitHub виявив, що переданий recovery-контекст відставав: після r5 уже були завершені r6 та r7. За правилом невикористання виданих ревізій роботу продовжено не повторним r6, а **10.16-r8** від exact verified r7 `b0d848b86b8344d1064024ca1d3a3f7186adc27c`.
- Створено `work/v10.16-r8-order-editor-assignments`, draft PR #349. У `order_editor_assignments_ui.py` винесено блок вибору/підготовки пар водій–ТЗ, відображення існуючих закріплень і переходу до менеджера. `order_editor_ui.py` лишився координатором форми; `order_editor_persistence.py` лишився місцем збереження. Схема БД, backup/restore, формати документів і правила парування не змінені.
- Збережено live-test hooks критичного bulk-сценарію. Додано r8 regression на делегування assignment-UI, збереження підготовлених пар після втрати виділення/фокусу та підтвердження порожнього наказу. Верхню частину координатора редактора розформатовано для читабельності без зміни логіки.
- Перший platform CI на проміжному head `b3f6aaa9019c010f104eb96fec0dd572ce88d444` завершив 1139 тестів з одним failure: історичний `test_v10_14_r4` не допускав r8 у version allowlist. Gate розширено без послаблення тесту; final exact head — `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`.
- Final exact-head CI: Windows 43042553534 SUCCESS, 1139/1139, START preflight та incomplete-package guard SUCCESS; Win7 compatibility 43042553636 SUCCESS, 1139/1139 на Python 3.8; macOS 43042553516 — Intel і ARM SUCCESS, 1139/1139 кожна. Temporary validation PR #350 закрито без merge.
- START/source workflow 43042538213 **двічі** не дійшов до тестів через однаковий DNS GitHub runner-а під час apt (`Temporary failure resolving azure.archive.ubuntu.com / archive.ubuntu.com / security.ubuntu.com`, exit 100). Це infra incident, не помилка коду; цей workflow не приймався як доказ продукту.
- Ізольований release workflow 43043571230 — SUCCESS: перевірив exact source SHA та три зелені platform runs, завантажив тільки portable artifacts, сам створив і перевірив START ZIP, заборонив installer-файли та перевірив stable/latest.
- Опубліковано immutable [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8) як prerelease, tag `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`, рівно 6 assets: Windows x64 portable, Windows 7 x64 portable, macOS x86_64 portable, macOS arm64 portable, START/source ZIP і SHA256. **Інсталяторів у релізі нема; Latest лишається v10.15-r5.**
- Draft PR #349 не merged/stable. Наступна кодова ревізія — **10.16-r9**.


## 11.11.2026 — власник затвердив stable v10.16-r8 та повний комплект інсталяторів

- Рішення власника: видану тестову r8 перевести в Stable/Latest; додати інсталятори Windows x64 та Win7 x64, залишити portable Windows/Win7/macOS Intel/ARM, START/source, повний SHA256. R9 до релізу не включати; стару stable 10.15-r5 зберегти.
- Integrate PR #352 (exact r8 source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6` + збережені recovery docs main) merged `890d9734a1de54020267ed0a08f789785508b803`. PR Windows run 43073483675 SUCCESS, Win7 compatibility 43073483820 SUCCESS, macOS Intel/ARM 43073483665 SUCCESS.
- Release promotion workflow 43077555581 спочатку зупинився на SIGPIPE `exit 141` у `git show | grep -Fq`; gate виправлено, failure не приховано. Повторний run [43077702929](https://github.com/RomanZavadaM/Taxo/actions/runs/43077702929) — **SUCCESS**, перевірив exact source/tag, оригінальні 6 assets і контрольні суми; витягнув Setup_Windows_x64.exe і Setup_Windows7_x64.exe з перевірених exact-r8 CI artifacts; оновив повний SHA256, перевів release у Stable/Latest; фінально завантажив усі 8 assets і перевірив SHA256.
- Release [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8) — Stable/Latest, exact tag як і був. Реліз 10.15-r5 залишився незмінною rollback.
- Зауваження власника до типових документів: бібліотека повинна бути **своя редагована для кожного користувача**, підтримувати створення власних шаблонів; шаблон не є фінальним документом. Заповнювати конкретними датами, ПІБ, транспортом та іншими реквізитами з робочих даних; не вигадувати зайві положення для простих наказів про закріплення. Історичні накази власника (до 20 років) можуть використовуватися для аналізу за умови приватності. Детальна карта: `docs/planning/ORDER_TEMPLATE_LIBRARY_PLAN_2026-11-11.md`.

## 17.11.2026 — 10.20-r7 завершено та опубліковано

- Після обриву попереднього чату виконано live GitHub reconciliation; повторної реалізації або повторної публікації r7 не робилось.
- Product PR #471 merged як `48ef40c77aa43da4140a390dbc14cc3ef3483b47`.
- Release-notes PR #475 дав exact issued source `172cc44d863c60e63d89f45dcc11d31fa575db46`.
- r7 додає явне відкриття вибраного паперового скана тільки після свіжої перевірки цілісності. Якщо користувач закрив вікно під час фонової перевірки, результат ігнорується і файл не відкривається.
- Скан не означає «підписано»; КЕП, автоматичний статус підпису, міграція старих документів і нові бізнес-статуси не додавались.
- Exact-source checks: START `43918902181` — SUCCESS, **1408/1408**; Windows `43918902255` — SUCCESS; Win7 `43918902260` — SUCCESS; macOS Intel/ARM `43918902511` — SUCCESS; Defender/integrity PASS.
- Trigger PR #476 merged `3239e6dd87a44a7210ea7ae1f6d3d0deeffaf5c2`; publisher `44054730816` — SUCCESS.
- [v10.20-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r7) — Test prerelease, exact target `172cc44d863c60e63d89f45dcc11d31fa575db46`, рівно 6 assets: 4 Portable, START, SHA256.
- Stable/Latest лишається [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5), 8 assets.
- Issue #61 вже містить аварійний підсумок r7 після збою доставки.
- На момент recovery **10.20-r8 не розпочата**: відповідної гілки, PR або коду немає. Наступний крок — після цього docs checkpoint вибрати один обмежений r8 slice з чинного плану DocumentVault/сканів.

## 17.11.2026 — 10.20-r8: безпечне прибирання помилкового скана з історією

- Після повного recovery r7 створено `work/v10.20-r8-paper-scan-removal-history` від `77aca7f68823ec86a139223cc6e46246dc79e18f`; Product PR #478 merged як `05e3132003f21054e63707ec231b017bba9ec7b1`.
- r8 додає явне **«Прибрати»** для вибраного скана після підтвердження. Скан зникає з активного списку, але immutable-файл фізично не стирається.
- Дія записується в окрему перевірювану історію; **«Історія…»** показує прибрані скани. Збережені байти лишаються під SHA-256/integrity контролем і входять у чинний повний backup/restore.
- Прибирання/історія не змінюють бізнес-статус документа і не означають «підписано». КЕП/e-signature validation, auto signed status, physical purge та migration старих документів не додавались.
- Перший exact head `88b430e82dbd34b98e9fb8377fc6df9f8ac22d2d` виявив **один** legacy static regression із r7: тест вимагав зберегти точну форму керування кнопкою «Відкрити». Сумісну форму повернуто без зміни поведінки r8.
- Final product head `5591f01459c17277cf486b04047c2dfe1babd5b6`: START `44059242234`, Windows `44059242262`, Win7 `44059242222`, macOS `44059242233` — SUCCESS; **1414/1414**; Defender/integrity PASS.
- Release-notes PR #479 merged як exact issued source `5c8513af9ee6d919d5812ebc39ee9769a83b1c44`.
- Exact release-source CI: START `44061025151` — **1414/1414**; Windows `44061025064`; Win7 `44061025223`; macOS Intel/ARM `44061025032` — SUCCESS; Defender/integrity PASS.
- Trigger PR #480 semantic marker залишив `10.20-r5`; merged `6aa04d1229f18b9ac67409b2af34d5868353f5ec`. Publisher `44065537111` — SUCCESS.
- [v10.20-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r8) — Test prerelease, exact target `5c8513af9ee6d919d5812ebc39ee9769a83b1c44`, рівно 6 assets: 4 Portable, START, SHA256.
- GitHub Latest/Stable лишається [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5), 8 assets.
- **10.20-r9 не розпочата.** Наступний slice визначати лише після fresh live verification; r8/tag/release не перевикористовувати.



## 20.11.2026 — 10.23-r3 інтегровано без публікації

- Live recovery виявив, що HANDOFF відставав: існував готовий PR #567 `feature/10.23-r3-documents-workspace`, хоча PROJECT_STATE ще казав «r3 не розпочата».
- r3 зібрано як один більший пакет за рішенням власника, а не як серію дрібних ревізій: #562 регульована область бланків/історії; #556 регульоване дерево каталогу та компактні дії; #553 накопичуваний вибір учасників/ТЗ, тема активного наказу, перехід до закріплень і підтвердження результату.
- Exact product head `149254b25da390892dcb09b8e2138fb0e88004cc`: START #44777829338, Windows #44777829188, Win7 #44777829261, macOS #44777829358 — SUCCESS; 36 strict runtime routes.
- Власник прямо вказав пропустити цю збірку й просунути проєкт далі. PR #567 інтегровано в main як `12a675a8f16c1f22190281339f62824aaad6a11d`; **release v10.23-r3 не створювати**. Stable лишається v10.23-r1, останній опублікований Test — v10.23-r2.
- Через Firefox warning для Windows artifact 14650119537 окремий diagnostic PR #568 перевірив exact outer SHA256, Microsoft Defender і ClamAV без запуску бінарників. Final run #44789160753 — SUCCESS; malware signature не знайдено. #568 закрито без merge.
- До початку 10.23-r4 обов'язково завершити документаційний резерв Google Drive та recovery-checkpoint; код/збірки на Drive більше регулярно не дублювати.


## 20.11.2026 — документаційний резерв Drive оновлено

- Створено `05_CURRENT_DOCS_2026-11-20_main-r3` у резервному комплекті Taxo.
- Скопійовано й контрольним читанням перевірено: START_HERE.md, PROJECT_RULES.md, HANDOFF_CURRENT.md, PROJECT_STATE.md, приватний TAXO_PROFILE.md і DEVELOPMENT_LOG.md.
- Старий великий `RECOVERY_CURRENT_MAIN` перейменовано на `RECOVERY_HISTORY — Taxo — legacy combined archive`; історію не видалено.
- `00_ОПИС` оновлено: main r3 інтегрований без release, наступна ревізія r4. Код, START, portable та Setup на Drive не дублювалися.
- Наступний кодовий крок: 10.23-r4, більший пов'язаний пакет залишкових UI-виправлень #556.
