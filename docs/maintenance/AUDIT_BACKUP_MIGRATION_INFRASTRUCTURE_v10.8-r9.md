# Аудит інфраструктури backup / restore / legacy migration — Taxo 10.8-r9

## Причина

Taxo продовжує розширюватися. Після `10.8-r6`–`r8` уже створені окремі infrastructure helpers, registry feature layers і application-services context. Наступний безпечний крок — прибрати з великого `main.py` ще один нейтральний infrastructure-блок, не змінюючи бізнес-поведінку.

До r9 у `main.py` одночасно жили:

- пошук старої локальної БД;
- одноразова legacy migration;
- створення SQLite backup;
- auto-backup guard;
- validation резервної БД;
- atomic restore і safety rollback.

Це не предметні правила водіїв, табеля, Бланків чи СТОІР, тому такий код не повинен залишатися власністю центрального UI/application module.

## Рішення r9

Створено `backup_migration.py` як вузький low-level infrastructure module.

Він отримує потрібні paths і callback `init_db` параметрами. Модуль не імпортує `main`, не читає UI-state і не знає про Tkinter.

`main.py` зберігає історичні функції як compatibility wrappers:

- `find_legacy_database()`;
- `migrate_legacy_database()`;
- `backup_database()`;
- `auto_backup_database()`;
- `validate_database_file()`;
- `restore_database_from_file()`.

Тому існуючі call sites продовжують працювати без масового переписування.

## Збережені invariants

### Дані користувача

- робоча БД не входить у repository/release;
- legacy migration не перезаписує вже існуючу поточну БД;
- restore спочатку перевіряє джерело;
- перед заміною чинної БД створюється safety backup;
- заміна виконується через тимчасову SQLite-БД і `os.replace()`;
- після restore виконується повторна validation;
- при винятку робиться best-effort rollback із safety backup.

### Сумісність

- формат SQLite-БД не змінено;
- workspace layout не змінено;
- імена зовнішніх helper-функцій у `main.py` збережено;
- чинний UX резервної копії/відновлення не перепроєктовано в цій ревізії.

### Архітектура

`backup_migration.py` не є місцем для доменних правил. Зокрема сюди не повинні потрапляти:

- plan/fact;
- правила табеля;
- Бланки підтвердження діяльності;
- кадрові правила;
- СТОІР;
- документи ТЗ;
- військовий облік;
- рішення UI про діалоги/підтвердження.

## Regression guard

`tests/test_v10_8_r9.py` перевіряє:

1. identity `10.8-r9`;
2. що `main.py` містить wrappers, а не стару SQLite implementation;
3. узгодженість створеної backup-БД;
4. safety backup перед restore;
5. legacy migration не перезаписує існуючу workspace-БД;
6. відсутність Tkinter/UI dependency в infrastructure module.

## Масштабування далі

Для великих майбутніх функцій Taxo приймаємо напрямок:

`domain model -> repository/data access -> service/use-case -> UI adapter -> FeatureLayer`

Спільні технічні сервіси передаються через explicit application infrastructure boundary, а не через імпорт глобального `main`.

Наступні декомпозиції виконувати малими revision slices з compatibility adapters, regression guards і без одночасного переписування бізнес-логіки.
