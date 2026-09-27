# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest published full checkpoint:** `v10.4-r2` → `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`  
**Latest issued fast-test revision:** Taxo `10.5-r3` / issued code head `ca1a1288f915c3fa0eb57c82a3e91aea3b0887d1` — immutable  
**Issued START r3:** run `36359285033`, artifact `10944184721`, `440/440 OK`, SHA-256 `c48fbc67a40dddfd91da8e52d0a947633e403c7ca61508f3ab2525e1ca6020ee`  
**Issued branch:** `work/v10.5-r3-employee-document-register`  
**Live ledger:** Issue #61  
**Next code revision:** only `10.5-r4`.

## DONE — Taxo 10.5-r3

Напрям: **єдиний реєстр документів працівників**.

- [x] реєстр працює поверх існуючої `employee_documents`, без другої таблиці й дублювання документів;
- [x] загальний список документів усіх працівників: ПІБ, тип, серія/номер, дата видачі, строк, орган видачі, джерело, стан;
- [x] пошук за працівником/табельним номером/реквізитами/органом/джерелом/приміткою;
- [x] фільтри за типом документа, станом, джерелом та архівністю;
- [x] стани строку: чинний / строк не вказано або безстроковий / закінчується ≤30 днів / прострочений / перевірити дату / архів;
- [x] кольорова індикація є інформаційною і не змінює документ;
- [x] редагування використовує існуючий редактор документа картки працівника;
- [x] відкриття прикріпленого файла, перехід до картки працівника, явне архівування;
- [x] `manual` та державний XLSX видно в одному реєстрі з provenance;
- [x] відсутність документа в новому державному витягу не видаляє й не архівує локальні дані;
- [x] synthetic regression без реальних персональних даних;
- [x] identity `10.5-r3`, чистий START, regression **440/440 OK**.

Issued code head: `ca1a1288f915c3fa0eb57c82a3e91aea3b0887d1`  
START run: `36359285033`  
Artifact: `10944184721` / `Taxo_v10_5_candidate_r3_START`  
Size: `891392` bytes  
SHA-256: `c48fbc67a40dddfd91da8e52d0a947633e403c7ca61508f3ab2525e1ca6020ee`

## DONE — Taxo 10.5-r2

Покомпонентна кольорова звірка ТЗ з «Шлях», рішення по кожному полю, append-only history, auto-resolve, safe fill/update, local-only preservation. Issued code head `d9e7beefa52c7774e1b4bd6711dfc5907e06de37`; regression `425/425 OK`; START run `36356444031`, artifact `10944042965`.

## DONE — Taxo 10.5-r1

Офіційна відомість військово-транспортного обліку по власному/балансовому транспорту. Issued code head `d7e5a730767ebc17e6935b2d3f25208a9f151c16`; regression `399/399 OK`; START run `36355353170`, artifact `10943696206`.

## NEXT

`10.5-r3` виданий і immutable. Будь-яка нова кодова зміна — тільки окрема гілка **10.5-r4** після повторного читання `START_HERE.md`, `PROJECT_STATE.md`, цього WORKLOG та Issue #61.

## BLOCKED

Немає.
