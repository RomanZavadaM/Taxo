# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.5-r8** / `v10.5-r8`  
**Latest issued fast-test:** Taxo **10.6-r3** / `v10.6-r3`  
**Issued r3 source/tag target:** `97e646936d14d163faf93882daf7894f5bb38ab6`  
**r3 regression:** `530/530 OK`  
**r3 START verify run:** `36434131185` — success  
**r3 publisher run:** `36434348730` — success  
**r3 Release START SHA-256:** `ea97909e7ae8a895730172aef4f6cabf61c18c227adce12cdaec803dfe8c490c`  
**r3 release:** https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3  
**Next code revision:** **10.6-r4**  
**Tracking:** Issue #83 — completed; live ledger #61

## DONE — 10.6-r3

- [x] Відтворити причину: historical r9 sanitizer очищав `doctor_*`, `mechanic_*`, `odometer_*` та `distance_km` разом із route-only полями.
- [x] Не змінювати immutable r9 helper; додати зовнішній runtime layer `v1063_features.py`.
- [x] Для нерегулярної шляхівки очищати тільки `start_direction`, `outbound_stops`, `return_stops`.
- [x] Зберегти лікаря I/II, механіка I/II, спідометр і фактичний пробіг, якщо вони реально є в payload.
- [x] Провести аудит решти автоматично заповнюваних полів шляхівки.
- [x] Зафіксувати, що `schedule_code` не має канонічного джерела і не повинен вигадуватися.
- [x] Залишити ДАІ/лінійний контроль/причину заїзду та підписні факти ручними.
- [x] Додати PDF regression: операційні поля друкуються, фіктивні маршрутні точки — ні.
- [x] Синхронізувати `main.APP_VERSION`, `VERSION.txt`, runtime chain і START guard як 10.6-r3.
- [x] Повний regression: `530/530 OK`.
- [x] Чистий START package перевірено у run `36434131185`.
- [x] Опубліковано immutable prerelease `v10.6-r3` на exact source `97e646936d14d163faf93882daf7894f5bb38ab6`.
- [x] Release START asset: `Taxo_v10_6_candidate_r3_START.zip`; SHA-256 `ea97909e7ae8a895730172aef4f6cabf61c18c227adce12cdaec803dfe8c490c`.
- [x] Release notes, `PROJECT_STATE.md`, `RELEASE_INDEX.md` і live ledger синхронізовано post-issuance docs commits без пересування tag/release.
- [x] Issue #83 закрито як completed.

## AUDIT — поля шляхівки

Автоматичні дані, які мають джерело у Taxo, передаються в PDF: реквізити підприємства, номер/серія, дата, маршрут/замовник, автобус, водій/табельний №, планові часові межі, тривалість роботи/керування, лікарі, механіки, спідометр/пробіг та маршрутні таблиці для регулярного маршруту.

Виявлена одна свідомо незаповнена автоматична графа: **«Графік» / `schedule_code`**. У поточній моделі немає канонічного коду графіка, тому r3 не підставляє вигадане значення.

Ручні/фактичні поля без джерела — ДАІ/служба руху, лінійний контроль, причина заїзду, підписи та подібні фактичні відмітки — залишаються порожніми до фактичного внесення.

## PRESERVED

- `10.6-r2`: нерегулярні замовлення/розвозки/міські/обласні/міжобласні поїздки, вибір автобуса під час видачі, route/stops validation тільки для реального регулярного маршруту.
- `10.6-r1`: фільтр неактивних ТЗ.
- plan/fact і тахографічна межа не змінюються.

## NEXT

`10.6-r3` виданий та immutable. Наступна кодова зміна — тільки **10.6-r4** у новій work-гілці. У `main` r3 не зливати без окремої команди власника.

## BLOCKED

Немає.
