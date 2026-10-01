# Аудит infrastructure-межі SQLite — Taxo 10.8-r10

## Мета

Винести з великого `main.py` одну вузьку низькорівневу відповідальність — відкриття поточної SQLite-БД та застосування усталеної connection policy — без зміни предметної логіки, схеми БД, workspace або UI.

## До r10

`main.db()` безпосередньо виконував `sqlite3.connect()` і встановлював:

- timeout 30 секунд;
- `sqlite3.Row` як `row_factory`;
- `PRAGMA foreign_keys=ON`;
- `PRAGMA busy_timeout=30000`;
- `PRAGMA journal_mode=DELETE`;
- `PRAGMA synchronous=FULL`.

## Після r10

Додано `database_runtime.py` з функцією `connect_database(path)`.

`main.py` зберігає compatibility wrapper `db()`, який передає актуальний `DB_PATH` у новий infrastructure-модуль. Це важливо для чинного механізму переключення workspace: шлях до БД не кешується всередині `database_runtime.py`.

## Інваріанти

- SQLite policy збережена без змін;
- `journal_mode=DELETE` лишається навмисно, оскільки Taxo допускає workspace на мережевих/синхронізованих файлових системах;
- `foreign_keys` лишаються увімкнені;
- `busy_timeout` лишається 30000 мс;
- `synchronous=FULL` лишається чинним;
- `sqlite3.Row` лишається форматом рядків;
- `main.db()` лишається сумісною точкою входу для наявних call sites.

## Межі модуля

`database_runtime.py`:

- не імпортує Tkinter;
- не визначає schema migrations;
- не містить бізнес-правил;
- не знає про водіїв, табель, бланки, СТОІР чи документи ТЗ;
- не обирає workspace;
- не зберігає глобальний шлях до БД.

## Перевірка

`tests/test_v10_8_r10.py` фіксує:

1. identity `10.8-r10`;
2. відсутність Tk dependency у infrastructure-модулі;
3. точне збереження SQLite PRAGMA/row policy;
4. те, що `main.db()` став compatibility wrapper без власних PRAGMA/`sqlite3.connect`;
5. наявність `database_runtime.py` у START package guard.

## Ризик і сумісність

Зміна навмисно мала: рухається лише низькорівнева connection policy. Схема робочої БД, формат даних, шляхи workspace, backup/restore semantics та UI не змінюються.

Після видачі `v10.8-r10` ревізія заморожується. Наступна кодова зміна за правилом версіювання — `10.9-r1`.
