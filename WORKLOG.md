# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.5-r8** / `v10.5-r8`  
**Latest issued fast-test:** Taxo **10.6-r2** / `v10.6-r2`  
**Issued r2 source/tag target:** `4d976bc7686015c00a3af5387634e8486cefc48b`  
**Active revision:** **10.6-r3**  
**Active branch:** `work/v10.6-r3-waybill-reverse-fields`  
**Base:** post-r2 docs head `78cbb7c8d036d00bb75d5ca98f2e5671d597eec6`  
**Tracking:** Issue #83; live ledger #61

## DOING — 10.6-r3

- [x] Відтворити причину: historical r9 sanitizer очищав `doctor_*`, `mechanic_*`, `odometer_*` та `distance_km` разом із route-only полями.
- [x] Не змінювати immutable r9 helper; додати зовнішній runtime layer `v1063_features.py`.
- [x] Для нерегулярної шляхівки очищати тільки `start_direction`, `outbound_stops`, `return_stops`.
- [x] Зберегти лікаря I/II, механіка I/II, спідометр і фактичний пробіг, якщо вони реально є в payload.
- [x] Провести аудит решти автоматично заповнюваних полів шляхівки.
- [x] Зафіксувати, що `schedule_code` не має канонічного джерела і не повинен вигадуватися.
- [x] Залишити ДАІ/лінійний контроль/причину заїзду та підписні факти ручними.
- [x] Додати PDF regression: операційні поля друкуються, фіктивні маршрутні точки — ні.
- [x] Синхронізувати `main.APP_VERSION`, `VERSION.txt`, runtime chain і START guard як 10.6-r3.
- [ ] Дочекатися успішного повного regression/CI для фінального code/docs head.
- [ ] Перевірити чистий START package.
- [ ] Опублікувати immutable prerelease `v10.6-r3` з прямим START asset.
- [ ] Зафіксувати issued SHA/run/checksum у `PROJECT_STATE.md`, `WORKLOG.md`, release index, Issue #61 та закрити Issue #83.

## AUDIT — поля шляхівки

Автоматичні дані, які мають джерело у Taxo, передаються в PDF: реквізити підприємства, номер/серія, дата, маршрут/замовник, автобус, водій/табельний №, планові часові межі, тривалість роботи/керування, лікарі, механіки, спідометр/пробіг та маршрутні таблиці для регулярного маршруту.

Виявлена одна свідомо незаповнена автоматична графа: **«Графік» / `schedule_code`**. У поточній моделі немає канонічного коду графіка, тому r3 не підставляє вигадане значення.

Ручні/фактичні поля без джерела (ДАІ/служба руху, лінійний контроль, причина заїзду, підписи тощо) залишаються порожніми до фактичного внесення.

## PRESERVED

- `10.6-r2`: нерегулярні замовлення/розвозки/міські/обласні/міжобласні поїздки, вибір автобуса під час видачі, route/stops validation тільки для реального регулярного маршруту.
- `10.6-r1`: фільтр неактивних ТЗ.
- plan/fact і тахографічна межа не змінюються.

## NEXT

Дочекатися final source-test workflow для актуального r3 head; після success зафіксувати exact issued source і опублікувати GitHub prerelease/START. У `main` не зливати без окремої команди власника.

## BLOCKED

Немає.
