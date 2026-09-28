# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest published full checkpoint:** `v10.4-r2` → `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`  
**Latest issued fast-test revision:** Taxo `10.5-r5` / issued code head `23064b775087c9dfc05867dc65f27e6d6d87e9b4` — immutable  
**Issued START r5:** run `36390554799`, artifact `10955647596`, regression `456/456 OK`, SHA-256 `66942b88ec245f5563838b134d137cbc02fb48510c7b9722bbb687b1684132a5`  
**Next code revision:** Taxo `10.5-r6` — not started  
**Live ledger:** Issue #61

## DONE — Taxo 10.5-r5

Виправлено читання окремих XLSX-експортів транспортних засобів з державного реєстру «Шлях», які в openpyxl 3.1.5 падали з `ChildSheet.__init__() got an unexpected keyword argument 'tabId'`.

Реалізовано:
- вузький compatibility layer `v1055_features.py`;
- спочатку XLSX читається штатно;
- retry спрацьовує тільки для точного `ChildSheet/tabId` TypeError;
- для retry створюється лише in-memory копія XLSX, з якої прибирається несумісний `tabId` у `xl/workbook.xml`;
- вихідний XLSX користувача не переписується і не змінюється;
- звичайна логіка розпізнавання колонок/рядків «Шлях» не змінена;
- synthetic regression відтворює фактичний openpyxl-збій, перевіряє успішне читання Taxo та незмінність байтів вихідного файлу;
- `10.5-r5` outermost у `taxo_app.py`, `main.APP_VERSION` і `VERSION.txt` синхронізовані;
- regression `456/456 OK`;
- START archive `Taxo_v10_5_candidate_r5_START`, run `36390554799`, artifact `10955647596`, SHA-256 `66942b88ec245f5563838b134d137cbc02fb48510c7b9722bbb687b1684132a5`.

`10.5-r5` видано та зафіксовано як immutable. Наступний кодовий крок — тільки `10.5-r6`.

## DONE — Taxo 10.5-r4

Lossless-імпорт двох фактичних форм державних XLSX працівників: окрема `Примітка державного витягу`, raw snapshot усіх колонок, невалідні паспорт/ID значення зберігаються як факт витягу без забруднення canonical-полів, UI доступу до оригінального snapshot. Issued head `117b305b048c2588e21d7908f39a3bb1071f74aa`; START run `36360262795`, artifact `10944963733`, SHA-256 `1b6200bc60064f842214b5eb6813c4e6b8992c3524c0631fcc9b067b8f2026e0`.

## DONE — Taxo 10.5-r3

Єдиний реєстр документів працівників поверх `employee_documents`. Issued code head `ca1a1288f915c3fa0eb57c82a3e91aea3b0887d1`; regression `440/440 OK`; START run `36359285033`, artifact `10944184721`.

## DONE — Taxo 10.5-r2

Покомпонентна кольорова звірка ТЗ з «Шлях». Issued code head `d9e7beefa52c7774e1b4bd6711dfc5907e06de37`; regression `425/425 OK`; START run `36356444031`, artifact `10944042965`.

## DONE — Taxo 10.5-r1

Офіційна відомість військово-транспортного обліку по власному/балансовому транспорту. Issued code head `d7e5a730767ebc17e6935b2d3f25208a9f151c16`; regression `399/399 OK`; START run `36355353170`, artifact `10943696206`.

## NEXT

Перевірити `Taxo_v10_5_candidate_r5_START` на тому самому фактичному XLSX «Шлях», який давав `ChildSheet/tabId`. Будь-яка наступна кодова зміна — тільки `10.5-r6`.

## BLOCKED

Немає.
