# Аудит сумісності схеми БД — Taxo 10.9-r9

**Дата:** 01.10.2026  
**База:** immutable `v10.9-r8` → `b8c3fb2d19323e8c9564eedc2f0540250dd51b29`  
**Branch:** `work/v10.9-r9-schema-compatibility`

## Вихідний стан

До r9 Taxo не використовував `PRAGMA user_version`. `database_runtime.py` відповідав за параметри відкриття SQLite, а історичний `init_db()` створював таблиці та виконував накопичені additive schema upgrades. Через відсутність явної версії схеми новіша база не могла бути відрізнена старішою збіркою від сумісної бази.

## Рішення r9

### Незалежна версія схеми

Версія схеми БД не дорівнює версії програми. Перший централізований baseline:

- `LEGACY_SCHEMA_VERSION = 0` — усі існуючі бази без explicit version;
- `SUPPORTED_SCHEMA_VERSION = 1` — база, яка успішно пройшла чинний historical `init_db()` під режимом r9.

### Безпечне відкриття

`database_runtime.connect_database()` після встановлення звичних SQLite safety settings читає `PRAGMA user_version`.

- `0` і `1` відкриваються r9;
- значення `> 1` викликає `SchemaTooNewError` і connection закривається до доменної роботи;
- просте відкриття legacy-бази **не** змінює `user_version`.

### Коли legacy-база отримує baseline 1

r9 не переносить сотні історичних DDL-кроків у новий migration engine одним ризикованим переписуванням. Additive layer `v1099_schema_compatibility.py` обгортає чинний `init_db()`:

1. виконується старий перевірений `init_db()`;
2. якщо він завершився успішно — окреме connection ставить `PRAGMA user_version=1` і commit;
3. якщо `init_db()` падає — stamp не виконується, база лишається `user_version=0`.

Це робить r9 безпечним baseline для наступних централізованих міграцій без перезапису чинної schema logic.

## Важливе обмеження

Збірки **до 10.9-r9** неможливо ретроспективно навчити читати `user_version` і відмовлятися від новішої схеми. Future-schema guard гарантований для r9 та наступних версій. Тому після першої майбутньої несумісної schema migration користувач не повинен відкривати ту саму робочу базу pre-r9 binary.

## Поведінкові тести

`tests/test_v10_9_r9.py` перевіряє:

- legacy DB відкривається як `user_version=0` без неявного stamp;
- explicit baseline stamp `1` зберігається після reopen;
- DB з `user_version=2` відхиляється r9 до використання;
- schema version не можна зменшити через migration helper;
- wrapper ставить baseline тільки після успішного original `init_db()`;
- failure original `init_db()` не ставить baseline навіть якщо до помилки була часткова DDL-операція.

## Межі r9

- r9 не виконує destructive data/schema migration;
- існуючі таблиці й дані не переписуються;
- historical `init_db()` залишається чинним baseline migration path;
- новий `user_version=1` є точкою, від якої наступні revisions можуть будувати явний послідовний migration path;
- immutable `v10.9-r8` не змінюється;
- `main` не змінюється без окремої прямої команди власника.
