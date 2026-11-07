# WORKLOG — Taxo

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
