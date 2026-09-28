# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.5-r8** / `v10.5-r8`  
**Latest issued fast-test:** Taxo **10.6-r2** / `v10.6-r2`  
**Issued r2 source/tag target:** `4d976bc7686015c00a3af5387634e8486cefc48b`  
**Regression:** **519/519 OK**  
**START verify run:** `36428981516` — success  
**Publisher run:** `36429169682` — success  
**Release START SHA-256:** `35ec71dcde4fb39924d513cba6b5a72f8746ab8150524510dffdf9b8939bacb3`  
**Branch:** `work/v10.6-r2-waybill-nonregular-ui`  
**Tracking:** Issue #82; live ledger #61  
**Next code revision:** **10.6-r3**

## DONE — 10.6-r2

- [x] Прибрано хибну вимогу регулярного маршруту для кожного виїзду автобуса.
- [x] Якщо `route_id` відсутній, стандартна кнопка формування шляхівки відкриває сценарій нерегулярної поїздки замість route/stops error.
- [x] Підтримано замовлення, розвозки, по місту/області, міжобласні та інші разові поїздки.
- [x] Час нерегулярної шляхівки береться з графіка водія.
- [x] Автобус можна вибрати прямо під час формування, якщо він ще не прив'язаний до дня.
- [x] Вибір автобуса зберігається як планове призначення `worklog`, не як факт тахографа.
- [x] Поле «Поїздка / замовник» вільно редагується; default — «по області».
- [x] Зворотний бік не заповнюється фіктивними маршрутними точками/розкладом.
- [x] Для реального каталожного маршруту збережена чинна сувора validation.
- [x] Окрема дія перейменована на «Інша поїздка / замовлення…».
- [x] Вікно «Про програму» ущільнене, щоб нижня кнопка не обрізалась на масштабованому/невисокому екрані.
- [x] `main.APP_VERSION`, `VERSION.txt`, runtime layer, regression і START guard синхронізовані як 10.6-r2.
- [x] Повний regression: 519/519 OK.
- [x] Чистий START package перевірений.
- [x] Опублікований prerelease `v10.6-r2` на точний issued source.
- [x] Прямий Release asset перевірений.

## RELEASE

- Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r2
- START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r2/Taxo_v10_6_candidate_r2_START.zip
- SHA-256: `35ec71dcde4fb39924d513cba6b5a72f8746ab8150524510dffdf9b8939bacb3`

## PRESERVED

- `10.6-r1`: фільтр «Сховати неактивні автомобілі» увімкнений за замовчуванням.
- `10.5-r10`: аудит конкретного дня не порівнює історичний план з поточним шаблоном маршруту; plan/fact не змішуються.
- `10.5-r9`: blank reverse side і редагований опис нерегулярної поїздки; r2 робить сценарій нормальним для будь-якого дня без `route_id` та додає вибір автобуса.

## NEXT

10.6-r2 виданий та immutable. Наступна кодова зміна — тільки **10.6-r3**. У `main` не зливати без окремої команди власника.

## BLOCKED

Немає.
