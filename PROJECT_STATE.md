# PROJECT_STATE — Taxo

**Дата:** 12.11.2026.

## Підтверджений інтегрований стан

- **Stable / Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)** за прямим рішенням власника від 11.11.2026. Тег збережено на exact source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`; після guarded workflow [43077702929](https://github.com/RomanZavadaM/Taxo/actions/runs/43077702929) SUCCESS реліз містить 8 перевірених assets (2 Windows Setup EXE, 4 portable ZIP, START ZIP, SHA256). Github Latest = r8.
- **`main` інтегрував код 10.16-r8** через [PR #352](https://github.com/RomanZavadaM/Taxo/pull/352), merge `890d9734a1de54020267ed0a08f789785508b803`. Exact source r8 — його предок; `main.APP_VERSION = 10.16-r8`. PR CI Windows 43073483675, Win7 compatibility 43073483820, macOS Intel/ARM 43073483665 — всі SUCCESS. Повторні CI для main push оцінювати окремо.
- **Попередня стабільна / rollback — [v10.15-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r5)**, exact tag `0a5420cb9285ae5a8fc085c2689303d3e070ffbb`, 8 assets незмінні. Старіший r4 — історичний rollback.
- **Попередній tagged test checkpoint — [v10.16-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r9)**, exact code/tag `53428d4287c0f4e83a55a739109c0bd209e3a623`, draft PR #355, не merged у main. Він залишається незмінним.
- **Останній перевірений тестовий artifact-checkpoint — 10.16-r10**, exact code head `1b39d60a7bce22843ebab575faa7173e3c818454`, [draft PR #357](https://github.com/RomanZavadaM/Taxo/pull/357), **не merged у main**. Картку ТЗ винесено з `vehicle_registry_ui.py` у новий `vehicle_form_ui.py` зі збереженням сумісного `vehicle_registry_ui.vehicle_form`, старого App adapter, SQL storage contract та поведінки полів/валідації. Exact-head CI START/source 43189898943, Windows 43189936525, Win7/Python 3.8 compatibility 43189936785, macOS Intel/ARM 43189936420 — усі SUCCESS, по 1147 тестів. CI artifacts: START 13929863257, Windows x64 13930327101, Windows7 x64 13930436491, macOS Intel 13930925650, macOS ARM 13929962887. Перевірений Windows portable має SHA-256 `8d4a4ccf9262e2439b6f3a594ecbacf996b0152853a3145ebd15761abb07d0d1`. Для r10 GitHub tag/release не створено: connector не має безпечної workflow-dispatch/create-release дії, а release/build механізм та main не змінювалися як обхід. Stable/Latest залишається 10.16-r8. Наступна **нова кодова ревізія — 10.17-r1**; r10 не reuse.
- За рішенням власника **бібліотеку шаблонів та архів документів відкладено**, інший ШІ окремо обробляє історичні зразки; поточну розробку продовжувати в інших модулях. Незавершену `work/v10.16-r9-order-editor-presets` не вливати: її вміст не входить до виданої r9.
- Незмінні правила поведінки, форматів, резервного копіювання та збереження історії залишаються чинними. Фізичне приймання на Windows 7 не підтверджене; відповідна CI — перевірка сумісності на Python 3.8.

## Поточна стратегія перебудови

- Taxo має продовжувати функціонально рости; зменшення `main.py` або інших файлів не є самостійною метою.
- Великі домени розділяються поступово на зрозумілі модулі зі стабільними сумісними точками входу. Пріоритет: накази, інструктажі/стажування, документи, персонал/транспорт і спільні сервіси.
- Код має залишатися читабельним для людини: зрозумілі назви, явні залежності, нормальне форматування й тести, які перевіряють поведінку, а не лише фізичне місце коду.
- Після stable 10.16-r8 наступні ревізії залишаються тестовими без автоматичного переведення у stable. r9 має tagged prerelease; r10 має перевірений Actions artifact-checkpoint без GitHub release. Для майбутньої stable потрібні пряме рішення власника і повний релізний checkpoint. 10.15-r5 зберігається як rollback.

## Архітектура бібліотеки шаблонів (відкладено)

Кожен користувач має мати власну редаговану бібліотеку типових документів, незалежну від оновлень програми. Шаблон — основа; кінцевий наказ складається зі справжніх дат, ПІБ, ТЗ та інших даних і має власну незмінну історію. Тексти за призначенням: для закріплення достатньо чіткої дії «закріпити» й повного переліку пар, без вигаданої багатослівності. План — `docs/planning/ORDER_TEMPLATE_LIBRARY_PLAN_2026-11-11.md`.

## Незмінні умови

План і факт розділені; оновлення не має вимагати повторного введення робочих даних. Бази, скани і персональні документи не входять у випуски. Повний backup включає документи працівників і `Data/PaperDocuments`; документи ТЗ, скани та Output — за відповідного вибору. Windows 7 має окрему лінію сумісності; compatibility CI не дорівнює тесту на фізичному Windows 7.

Стабільні теги r4, 10.15-r5 і їхні файли не змінювати.

Історичний контрольний випуск: Taxo 10.3 / `v10.3`, source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.

Історичні матеріали й детальні докази зберігаються в приватному `dev-strategy/profile/taxo/taxo-history/`, `WORKLOG.md` та Issue #61.

## Recovery

`START_HERE.md` → `HANDOFF_CURRENT.md` → private Taxo-profile → live GitHub → цей файл.
