# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest published full checkpoint:** `v10.4-r2` → `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`  
**Latest issued fast-test revision:** Taxo `10.5-r7` / issued code head `19a9f462993767a43ca3d5add8c7afabcbd39a96` — immutable  
**Issued START r7:** run `36396485974`, artifact `10958596374`, regression `476/476 OK`, SHA-256 `62bd734c82db132557376d5e6b01c37a84b5b358e32a0eedc7e1a4afd7f2c295`  
**Issued archive:** `Taxo_v10_5_candidate_r7_START.zip`  
**Next code revision:** Taxo `10.5-r8` — not started  
**Live ledger:** Issue #61

## DONE — Taxo 10.5-r7

Напрям: **повний локальний робочий цикл щорічного звіряння персонального військового обліку через Дію без імітації державного API**.

Реалізовано:
- [x] `diia_reconciliation.py`: локальний цикл `отримання → актуалізація → фіксація` поверх існуючого офіційного журналу;
- [x] точні офіційні сервіси Дії для отримання відомостей, актуалізації працівників і фінальної фіксації;
- [x] readiness-контроль: ЄДРПОУ, останній імпорт державних відомостей, кількість активних працівників, РНОКПП і військових карток;
- [x] «Відомості отримано й імпортовано» дозволяється лише після наявності реального імпорту державного витягу в Taxo;
- [x] локальні етапи підготовки не створюють статус «офіційно звірено»;
- [x] `RECONCILIATION_DIIA` записується в наявний `military_official_reconciliations` тільки після окремого підтвердження фактичної зовнішньої «Фіксації відомостей персонального обліку»;
- [x] для факту завершення зберігаються дата, реквізит/номер підтвердження та/або короткий результат;
- [x] UI «Звіряння через Дію» відкриває офіційні сервіси, показує стан циклу й резервний порядок за п. 46 Порядку №1487;
- [x] у UI прямо зазначено: Taxo не відправляє дані в Дію/«Оберіг» і не може сам підтвердити державний результат;
- [x] identity `10.5-r7`, outermost `v1057_features.py`, START guard містить `diia_reconciliation.py` та `v1057_features.py`;
- [x] synthetic regression без персональних даних;
- [x] фінальний clean CI: **476/476 OK**;
- [x] чистий START artifact `Taxo_v10_5_candidate_r7_START`;
- [x] r7 видано й заморожено як immutable.

Точний checkpoint:
- issued code head: `19a9f462993767a43ca3d5add8c7afabcbd39a96`;
- workflow run: `36396485974` — success;
- artifact: `10958596374`;
- archive: `Taxo_v10_5_candidate_r7_START.zip`;
- size: `942091` bytes;
- regression: `476/476 OK`;
- SHA-256: `62bd734c82db132557376d5e6b01c37a84b5b358e32a0eedc7e1a4afd7f2c295`.

## DONE — Taxo 10.5-r6

Робочі редаговані дані працівників / Дія та ТЗ / «Шлях» відокремлено від immutable державних snapshots; персональний військовий UI переведено на Diia-first порядок 2026; транспортний військовий вхід веде до відомості підприємства. Issued head `5f6c7643ce63bffb8069de9775194322a71f13df`; regression `465/465 OK`; START run `36394049520`, artifact `10957441841`, SHA-256 `7da722f840626720f8dd82c39d866e17b67f24312e89059055038ffc609b1458`.

## DONE — Taxo 10.5-r5

Сумісність XLSX «Шлях» з `ChildSheet/tabId`: вузький in-memory compatibility retry без зміни вихідного XLSX. Issued head `23064b775087c9dfc05867dc65f27e6d6d87e9b4`; regression `456/456 OK`; START run `36390554799`, artifact `10955647596`, SHA-256 `66942b88ec245f5563838b134d137cbc02fb48510c7b9722bbb687b1684132a5`.

## DONE — Taxo 10.5-r4

Lossless-імпорт двох фактичних форм державних XLSX працівників: raw snapshot усіх колонок, окрема примітка витягу, невалідні паспорт/ID значення не забруднюють canonical-поля. Issued head `117b305b048c2588e21d7908f39a3bb1071f74aa`; START run `36360262795`, artifact `10944963733`.

## DONE — Taxo 10.5-r3

Єдиний реєстр документів працівників поверх `employee_documents`. Issued code head `ca1a1288f915c3fa0eb57c82a3e91aea3b0887d1`; regression `440/440 OK`; START run `36359285033`, artifact `10944184721`.

## DONE — Taxo 10.5-r2

Покомпонентна кольорова звірка ТЗ з «Шлях». Issued code head `d9e7beefa52c7774e1b4bd6711dfc5907e06de37`; regression `425/425 OK`; START run `36356444031`, artifact `10944042965`.

## DONE — Taxo 10.5-r1

Офіційна відомість військово-транспортного обліку по власному/балансовому транспорту. Issued code head `d7e5a730767ebc17e6935b2d3f25208a9f151c16`; regression `399/399 OK`; START run `36355353170`, artifact `10943696206`.

## NEXT

`10.5-r7` immutable. Будь-який наступний кодовий крок — тільки **10.5-r8** в окремій work-гілці. `main` не змінювати без окремої команди власника на повний checkpoint.

## BLOCKED

Немає.
