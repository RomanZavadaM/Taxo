# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest published full checkpoint:** `v10.4-r2` → `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`  
**Latest issued fast-test revision:** Taxo `10.5-r1` / issued code head `d7e5a730767ebc17e6935b2d3f25208a9f151c16` — immutable  
**Issued START:** run `36355353170`, artifact `10943696206`, `399/399 OK`, SHA-256 `107d745a15ead27d22e6e8407da1dc2599264b538deb8a4eedd761a0c4751049`  
**Previous issued fast-test revision:** Taxo `10.4-r10` / issued code head `0f7944ad3f86bb6ee8ad19b40cfb2b38d924b934` — immutable  
**Active revision:** немає  
**Next code revision:** тільки `10.5-r2`  
**Live ledger:** Issue #61

## DONE — Taxo 10.5-r1

Напрям: **офіційна відомість військово-транспортного обліку по власному/балансовому транспорту підприємства**.

- [x] scope уточнено власником: відомість по власному транспорту є окремим потрібним результатом;
- [x] branch відкрито від фінального зеленого r10 guard `5c964a2278d59f40542cb5b4679b95cc56b809fb`;
- [x] додано окремі локальні реквізити відомості ТЗ: явна належність до власного/балансового парку, тип, технічний стан, залишкова балансова вартість;
- [x] ТЗ не потрапляє у відомість лише через `active`, «Шлях», наряд або військовий статус;
- [x] підтягуються тільки явно закріплені за ТЗ працівники та наявні військово-облікові дані;
- [x] сформовано 12 колонок додатка 1;
- [x] додано PDF і XLSX export;
- [x] додано `Відомість (додаток 1)` до існуючого контуру `Відомості 20.06 / 20.12`;
- [x] формування документа не означає автоматично його подання;
- [x] відсутні/невизначені дані показуються користувачу, а не вигадуються;
- [x] identity синхронізовано на `10.5-r1`;
- [x] regression `399/399 OK`;
- [x] чистий START archive сформовано та перевірено;
- [x] `10.5-r1` видано й зафіксовано immutable.

Канонічний тестовий START `10.5-r1`:
- code head: `d7e5a730767ebc17e6935b2d3f25208a9f151c16`;
- run: `36355353170` — success;
- artifact: `10943696206` / `Taxo_v10_5_candidate_r1_START`;
- SHA-256: `107d745a15ead27d22e6e8407da1dc2599264b538deb8a4eedd761a0c4751049`;
- regression: `399/399 OK`;
- START guard підтвердив наявність r9/r10/r1 runtime-файлів і відсутність DB/SQLite/cache/development clutter.

## DONE — Taxo 10.4-r10

`10.4-r10` закрито та не перевикористовується. Канонічний START: run `36351811271`, artifact `10942183754`, SHA-256 `03e18c7c52cadf46ed35a27d5b1b63f454cedd39aab47d12395fd7750e09082c`, regression `388/388 OK`.

## NEXT

Новий код не писати під `10.5-r1`. Наступний завершений кодовий крок — тільки **Taxo `10.5-r2`** у новій work branch від останнього зеленого r1 guard.

## BLOCKED

Немає.
