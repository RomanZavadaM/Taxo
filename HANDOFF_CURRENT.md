# HANDOFF_CURRENT — Taxo

**11.11.2026.** Поточна робота — структурна перебудова поверх робочої 10.15-r5. Скорочення файлів не є ціллю: Taxo має рости функціонально, але кожна система повинна мати зрозуміле місце в коді й залишатися читабельною для людини.

## Підтверджена база

- **Stable / Latest:** [v10.15-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r4).
- Код, інтегрований у `main`, має `APP_VERSION = 10.15-r5`; [v10.15-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r5) — prerelease. Власник перевірив r5 і не знайшов зауважень. **r5 лишається робочою rollback/reference точкою**, а не stable.
- 10.15-r6 скасовано; PR #317 не інтегровано.
- До завершення великої перебудови нові стани — **лише тестові checkpoints**. Власник дозволив робити ручні тестові архіви більшими етапами, а не після кожного дрібного перенесення.

## Незлита лінія перебудови

- **r7:** [draft PR #320](https://github.com/RomanZavadaM/Taxo/pull/320) — накази/інструктажі/паперові документи розкладено на окремі модулі; exact head `0828870a92cceae0f653f85948a195c4c1e0cd25`.
- **r8:** [draft PR #323](https://github.com/RomanZavadaM/Taxo/pull/323) — звіт документів ТЗ винесено в `vehicle_documents_report_ui.py`; exact head `1b33a18d7df73fc1de3e5f67120c2c5ed0af472f`.
- **r9:** [draft PR #324](https://github.com/RomanZavadaM/Taxo/pull/324) — базовий UI транспорту винесено в `vehicle_registry_ui.py` із сумісними App-adapters; exact head `c1ac30431dc785296760385cd1d701e32110cbd8`.
- **r10:** [draft PR #325](https://github.com/RomanZavadaM/Taxo/pull/325), exact head `05cb7341146f46e2a2233b6966b85ed670b0b8f7`. Реєстр працівників, картку працівника й базові дії статусу винесено в `employee_registry_ui.py`; App API збережено через adapters. `main.py` став меншим лише як наслідок поділу — функціонал не видалявся.
- r10: Windows run 42996976591 — SUCCESS, 1097/1097; START preflight і guard неповного пакета — SUCCESS. Win7 compatibility 42996977191 — SUCCESS, 1097/1097 (**не фізичний Windows 7**). macOS 42996976642 — Intel і ARM SUCCESS, 1097/1097 на кожній архітектурі.
- **10.16-r1 — поточний checkpoint:** [draft PR #327](https://github.com/RomanZavadaM/Taxo/pull/327), exact head `5971bd57c00d919c70247f7fb55298c9fe263add`. Налаштування відповідальних/місця/нумерації винесено в `operations_settings_ui.py`, каталог типів наказів — в `order_type_catalog_ui.py`. `operations_orders_ui.py` лишився координатором і реєстром наказів. Кодова перевірка на попередньому head `81fd6740bed0e1fe32a2503d45c924a5c8f98ac7`: Windows, Win7 compatibility та macOS Intel/ARM — SUCCESS, 1103/1103. Поточний head `5971bd57c00d919c70247f7fb55298c9fe263add` відрізняється лише форматуванням PROJECT_STATE; повторні regression-перевірки на всіх платформах також SUCCESS.
- Під час r1 regression повернуто втрачений у recovery-документації історичний anchor Taxo 10.3 через docs PR #328; це виправлення вже в `main`.
- Для r10 окремий START-архів цими PR-triggered workflow не створювався. Не називати START preflight готовим START artifact.
- Схема БД, бізнес-правила, backup/restore та формати робочих даних у r8-r10 не змінювалися.

## Важлива настанова власника

Не оптимізувати проєкт за кількістю рядків. Мета — **розвиток Taxo в модульній, зрозумілій людині структурі**. Новий код оформлювати читабельно: зрозумілі назви файлів і функцій, явні залежності, нормальне форматування; не стискати код заради цифри. При перенесеннях захищати вже робочі сценарії поведінковими regression-тестами.

## Наступна дія

1. При новій сесії ще раз звірити live GitHub і exact head PR #327.
2. Не merge-ити r7/r8/r9/r10/r1 і не робити їх stable без окремої команди власника.
3. Наступна кодова ревізія за правилом версій — **10.16-r2**.
4. Продовжити планове розділення наказів / інструктажів / документів одним цілісним безпечним кроком, з урахуванням читабельності й розвитку функцій; `main.py` не «худнути заради худнення».
5. r5 зберігати недоторканою точкою повернення.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
