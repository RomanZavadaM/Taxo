# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest published full checkpoint:** `v10.4-r2` → `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`  
**Latest issued fast-test revision:** Taxo `10.5-r2` / issued code head `d9e7beefa52c7774e1b4bd6711dfc5907e06de37` — immutable  
**Issued START r2:** run `36356444031`, artifact `10944042965`, `425/425 OK`, SHA-256 `c88c806c9deb4821080f63adea46001cbd4a885b9dc7702d80e0b9dcbd675c26`  
**Active revision:** Taxo `10.5-r3`  
**Active branch:** `work/v10.5-r3-employee-document-register`  
**Base:** r2 docs/admin guard `ab49a4e9159863d81210e4ad02214560afc0857a`  
**Live ledger:** Issue #61

## DOING — Taxo 10.5-r3

Напрям: **єдиний реєстр документів працівників**.

Передумова: `employee_documents` і вкладка «Документи» вже існують у картці конкретного працівника, а імпорт держреєстру вже може створювати/оновлювати паспортні підказки з джерелом. r3 не створює другу таблицю документів — він будує загальний реєстр поверх наявної моделі.

- [ ] загальний список документів усіх працівників із ПІБ, типом, серією/номером, строком, органом видачі, джерелом і станом;
- [ ] пошук та фільтри: працівник/реквізити, тип документа, стан, джерело, активні/архівні;
- [ ] стани строку: чинний / безстроковий або строк не вказано / закінчується / прострочений / архів;
- [ ] кольорова індикація стану документа без зміни даних;
- [ ] швидкий перехід до картки працівника та редагування документа через існуючу модель;
- [ ] джерело `manual` та державний XLSX лишаються видимими; реєстровий імпорт не затирає локальні документи;
- [ ] синтетичні regression-тести без реальних персональних даних;
- [ ] identity `10.5-r3`, чистий START, regression green;
- [ ] після видачі r3 — immutable, наступний кодовий крок тільки `10.5-r4`.

## DONE — Taxo 10.5-r2

Покомпонентна кольорова звірка ТЗ з «Шлях», рішення по кожному полю, append-only history, auto-resolve, safe fill/update, local-only preservation. Issued code head `d9e7beefa52c7774e1b4bd6711dfc5907e06de37`; regression `425/425 OK`; START run `36356444031`, artifact `10944042965`.

## DONE — Taxo 10.5-r1

Офіційна відомість військово-транспортного обліку по власному/балансовому транспорту. Issued code head `d7e5a730767ebc17e6935b2d3f25208a9f151c16`; regression `399/399 OK`; START run `36355353170`, artifact `10943696206`.

## NEXT

Завершити r3 як окремий fast-test START checkpoint. `10.5-r2` і старі ревізії не змінювати.

## BLOCKED

Немає.
