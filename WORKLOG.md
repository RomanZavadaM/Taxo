# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest published full checkpoint:** `v10.4-r2` → `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`  
**Latest issued fast-test revision:** Taxo `10.5-r2` / issued code head `d9e7beefa52c7774e1b4bd6711dfc5907e06de37` — immutable  
**Issued START:** run `36356444031`, artifact `10944042965`, `425/425 OK`, SHA-256 `c88c806c9deb4821080f63adea46001cbd4a885b9dc7702d80e0b9dcbd675c26`  
**Previous issued fast-test revision:** Taxo `10.5-r1` / `d7e5a730767ebc17e6935b2d3f25208a9f151c16` — immutable  
**Active revision:** немає  
**Next code revision:** тільки `10.5-r3`  
**Live ledger:** Issue #61

## DONE — Taxo 10.5-r2

Напрям: **покомпонентна кольорова звірка ТЗ з ліцензійним реєстром «Шлях» з історією рішень**.

- [x] кожне офіційне поле «Шлях» має окремий стан: відповідає / можна доповнити / розбіжність / критичний конфлікт / немає у витягу;
- [x] кольорова індикація працює на рівні поля;
- [x] рішення по полю: `Прийняти дані реєстру` / `Залишити Taxo` / `Потрібно виправити у реєстрі` / `Відкласти`;
- [x] рішення та append-only історія зберігаються між квартальними імпортами;
- [x] `Потрібно виправити у реєстрі` автоматично закривається, коли наступний витяг уже збігається з Taxo;
- [x] порожнє або відсутнє поле «Шлях» ніколи не очищає локальне значення Taxo;
- [x] VIN і держномер трактуються як ідентифікаційні поля; їх розбіжність — критичний конфлікт;
- [x] існуючі режими `Лише звірити / Доповнити / Оновити + доповнити` та створення нових карток після підтвердження збережені;
- [x] `Є у Taxo, але немає у витягу` не видаляє і не деактивує ТЗ;
- [x] локальний контроль документів ТЗ та військово-транспортний облік залишаються незалежними;
- [x] `vehicle_reconciliation.py` і `v1052_features.py` включені до START guard;
- [x] identity `10.5-r2` синхронізовано в `VERSION.txt` і `main.APP_VERSION`;
- [x] regression `425/425 OK`;
- [x] чистий START archive сформовано та перевірено;
- [x] `10.5-r2` видано й зафіксовано immutable.

Канонічний тестовий START `10.5-r2`:
- code head: `d9e7beefa52c7774e1b4bd6711dfc5907e06de37`;
- run: `36356444031` — success;
- artifact: `10944042965` / `Taxo_v10_5_candidate_r2_START`;
- size: `878678` bytes;
- SHA-256: `c88c806c9deb4821080f63adea46001cbd4a885b9dc7702d80e0b9dcbd675c26`;
- regression: `425/425 OK`;
- START guard підтвердив r1/r2 runtime-файли й відсутність DB/SQLite/cache/development clutter.

## DONE — Taxo 10.5-r1

`10.5-r1` закрито та не перевикористовується. Канонічний START: code head `d7e5a730767ebc17e6935b2d3f25208a9f151c16`, run `36355353170`, artifact `10943696206`, SHA-256 `107d745a15ead27d22e6e8407da1dc2599264b538deb8a4eedd761a0c4751049`, regression `399/399 OK`.

## NEXT

Новий код не писати під `10.5-r2`. Наступний завершений кодовий крок — тільки **Taxo `10.5-r3`** у новій work branch від останнього зеленого r2 guard.

## BLOCKED

Немає.
