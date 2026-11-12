# HANDOFF_CURRENT — Taxo

**12.11.2026 — stable r8; останній перевірений тестовий artifact-checkpoint r10.**

## Підтверджений стан

- **Stable/Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**, immutable source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`. Stable/Latest і його assets **не змінювалися**. Попередня stable v10.15-r5 лишається rollback.
- **`main` за кодом залишається 10.16-r8.** Документаційний recovery-checkpoint r10 може змінити лише HEAD документації; код r10 у `main` не зливався.
- Попередній tagged test checkpoint — **[v10.16-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r9)**, exact `53428d4287c0f4e83a55a739109c0bd209e3a623`, draft PR #355. Він не merged у main.
- **Новий перевірений тестовий r10**: draft [PR #357](https://github.com/RomanZavadaM/Taxo/pull/357), branch `work/v10.16-r10-vehicle-form-module`, exact head `1b39d60a7bce22843ebab575faa7173e3c818454`. Картку ТЗ винесено з `vehicle_registry_ui.py` у `vehicle_form_ui.py`; сумісний entry point `vehicle_registry_ui.vehicle_form` збережено. SQL INSERT/UPDATE, валідація року, ownership/active поля і виклик `app.load_vehicles()` не змінені за поведінкою.
- r10 exact-head CI: START/source [43189898943](https://github.com/RomanZavadaM/Taxo/actions/runs/43189898943), Windows [43189936525](https://github.com/RomanZavadaM/Taxo/actions/runs/43189936525), Win7/Python 3.8 compatibility [43189936785](https://github.com/RomanZavadaM/Taxo/actions/runs/43189936785), macOS Intel/ARM [43189936420](https://github.com/RomanZavadaM/Taxo/actions/runs/43189936420) — **усі SUCCESS, по 1147 тестів**.
- r10 CI artifacts існують на exact head: START artifact `13929863257`; Windows x64 `13930327101`; Windows7 x64 `13930436491`; macOS Intel `13930925650`; macOS ARM `13929962887`. Із Windows artifact перевірено portable `Taxo_v10_16_candidate_r10_Windows_x64_Portable.zip`, SHA-256 `8d4a4ccf9262e2439b6f3a594ecbacf996b0152853a3145ebd15761abb07d0d1`.
- **Для r10 GitHub tag/release не створено.** Підключений GitHub connector не має безпечної дії workflow-dispatch/create-release; release/build workflow навмисно не змінювався й `main` не використовувався як обхід. Якщо потрібен довготривалий prerelease, публікувати тільки exact head r10 штатним publisher без зміни коду.
- Відкладена `work/v10.16-r9-order-editor-presets` лишається parked і не повинна зливатися.

## Рішення власника

- **Бібліотеку шаблонів і сховище/архів документів не чіпати** до нової команди. Архітектурні плани в `docs/planning/` не реалізовувати й не змінювати.
- Продовжувати модульну перебудову інших систем. Скорочення коду не є метою; пріоритет — читабельні модулі та збереження робочої поведінки.
- Stable 10.16-r8 не змінювати без прямої команди.

## Наступна дія

1. Нова сесія: `START_HERE.md` → цей HANDOFF → private Taxo-profile → live GitHub (main / PR #357 / exact-head checks).
2. r10 уже отримав окремий тестовий artifact-checkpoint і **не перевикористовується для нового коду**. Наступна кодова ревізія за правилом rollover — **10.17-r1**.
3. Перед 10.17-r1 вибрати наступну безпечну модульну межу поза бібліотекою шаблонів і сховищем документів; не починати її, якщо live GitHub суперечить цьому recovery.

## Recovery

`START_HERE.md` → цей файл → приватний Taxo-profile → live GitHub → `PROJECT_STATE.md`.
