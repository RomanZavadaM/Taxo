# Taxo 10.9-r9 — сумісність схеми SQLite

Fast-test ревізія поверх immutable `v10.9-r8`. Stable `v10.3` не змінюється.

## Що додано

- перший explicit SQLite schema baseline через `PRAGMA user_version`;
- `SUPPORTED_SCHEMA_VERSION = 1` для r9;
- legacy-бази без explicit version лишаються `user_version=0` до успішного завершення чинного `init_db()`;
- після успішного schema init/migration база отримує `user_version=1`;
- r9 та наступні збірки відмовляються відкривати базу з schema version, вищою за підтримувану;
- connection гарантовано закривається, якщо compatibility check не пройдено;
- schema version не зменшується migration helper-ом.

## Чого r9 не робить

- не переписує історичний `init_db()` одним великим migration refactor;
- не виконує destructive migration;
- не змінює існуючі робочі дані під час простого відкриття БД;
- не може ретроспективно захистити binaries до r9: pre-r9 версії не знають про `user_version`.

## Технічна реалізація

- compatibility logic у `database_runtime.py`;
- additive runtime layer `v1099_schema_compatibility.py`;
- поведінкові тести `tests/test_v10_9_r9.py`;
- START/package guards вимагають r9 runtime.

Перед видачею: exact-head source/START + Windows + macOS x86_64/arm64. Злиття в `main` — тільки за окремою прямою командою власника.
