# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest published full checkpoint:** `v10.4-r2` → `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`  
**Latest issued fast-test revision:** Taxo `10.5-r4` / issued code head `117b305b048c2588e21d7908f39a3bb1071f74aa` — immutable  
**Issued START r4:** run `36360262795`, artifact `10944963733`, workflow success, SHA-256 `1b6200bc60064f842214b5eb6813c4e6b8992c3524c0631fcc9b067b8f2026e0`  
**Active revision:** Taxo `10.5-r5`  
**Active branch:** `work/v10.5-r5-shlyakh-xlsx-tabid`  
**Base:** issued r4 head `117b305b048c2588e21d7908f39a3bb1071f74aa`  
**Live ledger:** Issue #61

## DOING — Taxo 10.5-r5

Напрям: **виправлення читання XLSX-експорту транспортних засобів з державного реєстру «Шлях»**.

Відтворений дефект:
- при відкритті окремих XLSX «Шлях» openpyxl 3.1.5 падає з `ChildSheet.__init__() got an unexpected keyword argument 'tabId'`;
- причина — атрибут `tabId` у `<sheet>` всередині `xl/workbook.xml`, якого поточний `ChildSheet` openpyxl не приймає;
- це проблема сумісності структури XLSX, а не даних конкретного транспортного засобу.

Рішення r5:
- [x] новий зовнішній compatibility layer `v1055_features.py`;
- [x] спочатку читаємо XLSX штатно; workaround запускається тільки для точного `ChildSheet/tabId` TypeError;
- [x] для retry створюється лише in-memory копія XLSX без `tabId`; вихідний файл користувача не змінюється;
- [x] звичайна логіка розпізнавання колонок/рядків «Шлях» лишається тією самою;
- [x] synthetic regression відтворює реальний збій і перевіряє успішне читання та незмінність вихідного файлу;
- [x] identity `10.5-r5`; r5 outermost у `taxo_app.py`;
- [x] START workflow вимагає `v1055_features.py` у пакеті;
- [ ] повний regression suite green;
- [ ] чистий START artifact;
- [ ] зафіксувати issued r5 у live ledger та release notes;
- [ ] після видачі r5 — immutable, наступний кодовий крок тільки `10.5-r6`.

## DONE — Taxo 10.5-r4

Lossless-імпорт двох фактичних форм державних XLSX працівників: окрема `Примітка державного витягу`, raw snapshot усіх колонок, невалідні паспорт/ID значення зберігаються як факт витягу без забруднення canonical-полів, UI доступу до оригінального snapshot. Issued head `117b305b048c2588e21d7908f39a3bb1071f74aa`; START run `36360262795`, artifact `10944963733`, SHA-256 `1b6200bc60064f842214b5eb6813c4e6b8992c3524c0631fcc9b067b8f2026e0`.

## DONE — Taxo 10.5-r3

Єдиний реєстр документів працівників поверх `employee_documents`. Issued code head `ca1a1288f915c3fa0eb57c82a3e91aea3b0887d1`; regression `440/440 OK`; START run `36359285033`, artifact `10944184721`.

## DONE — Taxo 10.5-r2

Покомпонентна кольорова звірка ТЗ з «Шлях». Issued code head `d9e7beefa52c7774e1b4bd6711dfc5907e06de37`; regression `425/425 OK`; START run `36356444031`, artifact `10944042965`.

## DONE — Taxo 10.5-r1

Офіційна відомість військово-транспортного обліку по власному/балансовому транспорту. Issued code head `d7e5a730767ebc17e6935b2d3f25208a9f151c16`; regression `399/399 OK`; START run `36355353170`, artifact `10943696206`.

## NEXT

Дочекатися green CI для r5, перевірити START artifact і видати `Taxo_v10_5_candidate_r5_START`. Після видачі r5 не змінювати; наступний кодовий крок — тільки `10.5-r6`.

## BLOCKED

Немає.
