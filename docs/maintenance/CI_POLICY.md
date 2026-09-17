# CI / збірки Taxo 9.x

Після стабілізації **Taxo 9.0** службові workflow репозиторію переведені з історичних назв `v8.70` на актуальну лінію `Taxo 9.x`.

## Правила

- кожен Pull Request запускає обов'язкову Windows-перевірку `build-windows`;
- macOS-перевірка запускається для двох архітектур: `arm64` та `x86_64`;
- звичайний PR виконує компіляцію та автоматичні тести без побудови великих executable-пакетів;
- executable-збірки запускаються вручну через `workflow_dispatch`;
- бази даних користувачів, SQLite-файли та кеші не повинні потрапляти в пакети;
- START source archive формується окремим workflow на основі `VERSION.txt`;
- stable release 9.0 публікується окремим workflow `publish-v9.0.yml`.

## Поточні workflow

- `build-windows-v9.yml` — Windows test/build;
- `build-macos-v9.yml` — macOS test/build;
- `source-test-archive.yml` — START source archive;
- `publish-v9.0.yml` — відтворення/публікація stable release 9.0.

Назви `v8.70` у CI після переходу на 9.0 вважаються історичними й у `main` не використовуються.
