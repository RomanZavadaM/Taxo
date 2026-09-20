# Аудит Taxo 10.1-r1 candidate

**Дата:** 20.09.2026  
**Stable baseline:** Taxo 10.0 / tag `v10.0`  
**Stable target:** `91c0d6365a40eb09fe40f97a2965da40b314bc15`  
**Робоча гілка:** `work/v10.1-driver-role-ui-refresh`

## Фактична причина дефекту

У стартовій legacy-синхронізації `init_db()` для пов'язаного працівника значення `drivers.active` записувалось у `employees.active`, а роль `Водій` додавалась через `INSERT OR IGNORE` при кожному запуску.

Додатково картка працівника могла очищати `driver_end_date`, «Звільнити / поновити» напряму перемикало і employee-, і driver-active, а legacy-картка водія могла змінити `employees.active`.

Це змішувало два різні поняття: **працевлаштований працівник** і **активна роль водія**.

## Внесене виправлення

1. Додано `sync_legacy_driver_employee()`: для існуючого працівника `employees.active` є authoritative.
2. `drivers.active` більше не переписує статус працевлаштування.
3. Роль `Водій` синхронізується лише для справді активної driver-картки без дати завершення.
4. `driver_end_date` не очищається звичайним редагуванням.
5. Звільнення завершує поточну роль водія; поновлення працівника не відновлює її автоматично.
6. Деактивація ролі з картки водія вимагає дати завершення.
7. Додано repair конкретного старого пошкодження: `driver_end_date` є, `dismissal_date` порожня, але `employees.active=0` через старий startup sync.

## UI / branding

- окремий модуль `branding.py`;
- text-free мотив сонця й автобуса;
- приглушена синьо-жовта палітра;
- верхня brand-шапка;
- динамічна назва з `company.name` / поля «Назва підприємства»;
- фіксований напис «АТП Завада» у графіці відсутній;
- runtime icon і build-time генерація ICO/ICNS.

## Regression result

GitHub Actions run `35525130436`: **126 tests / OK**.

START package також пройшов package preflight: без БД/SQLite/cache; `START.bat` ASCII-only + CRLF.

Нові тести покривають завершену роль при активному працівнику, repair старого помилкового status, реальне звільнення, re-employment, збереження історичного `driver_end_date`, запит дати при деактивації водія, dynamic enterprise name та text-free branding.

## Статус

**10.1-r1 — candidate / test checkpoint, не stable.** `main` і `v10.0` не змінюються до ручної Windows-перевірки; для перевірки публікується окремий immutable source/START prerelease `v10.1-r1`.
