# Taxo 10.9-r9 — інтегрований full multi-platform checkpoint

`v10.9-r9` — актуальний інтегрований candidate/checkpoint у `main`. Stable `v10.3` не змінюється без окремого рішення власника.

## Що увійшло безпосередньо в r9

- перший explicit SQLite schema baseline через `PRAGMA user_version`;
- `SUPPORTED_SCHEMA_VERSION = 1`;
- legacy-бази без explicit version лишаються `user_version=0` до успішного завершення чинного `init_db()`;
- після успішного schema init/migration база отримує `user_version=1`;
- r9 та наступні збірки відмовляються відкривати базу з schema version, вищою за підтримувану;
- connection гарантовано закривається, якщо compatibility check не пройдено;
- schema version не зменшується migration helper-ом.

## Кумулятивно інтегровано з 10.9-r2 → 10.9-r9

- r2 — незворотна історія виданих шляхівок і номерів;
- r3 — контроль чинності документів ТЗ на весь період рейсу;
- r4 — посилений work/rest compliance;
- r5 — безпечніший пріоритет фактичних джерел у 60-денному реєстрі;
- r6 — historical employment / P-5 / personnel balance safety;
- r7 — odometer chronology і STOIR forecast hardening;
- r8 — immutable approved/signed orders і driver→vehicle assignment safety;
- r9 — explicit SQLite schema compatibility baseline.

## Інтеграція в main

- issued source/tag: `a368bf3bdfd4a16cc099844b830379c5e2646c2d`;
- cumulative PR #128 — merged;
- main code merge: `3f59544b8737cd4715d84f786e32378d87d1dd99`;
- documentation closeout PR #129 — merged;
- current main after closeout: `34a56e05133bedfc81e6273ea572f6e9757ddab7`;
- exact-head Windows gate `36919102579` — success;
- exact-head macOS gate `36919102540` — success.

## Пакети для тестування

Release `v10.9-r9` має повний user-test набір:

- Windows x64 Setup;
- Windows x64 Portable;
- Windows 7 SP1 x64 Setup;
- Windows 7 SP1 x64 Portable;
- macOS ARM64 Portable;
- macOS Intel x86_64 Portable;
- START/source archive;
- SHA-256 manifests.

Робочі БД, SQLite-файли, скани, кеші та персональні документи до release не входять.

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

## Далі

Наступна кодова ревізія після `10.9-r9` — тільки **10.9-r10**. Уже видана r9 не перевикористовується і tag не пересувається.
