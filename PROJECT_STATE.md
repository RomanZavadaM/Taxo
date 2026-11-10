# PROJECT_STATE — Taxo

**Дата:** 10.11.2026.

## Підтверджений стан

- **Stable / Latest:** [v10.15-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r4); попередня stable — [v10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4).
- **Інтегровано 10.15-r4:** PR #304, product `ae0c673a42c5b633706efdffc1adfd5b1b70681d`; контроль документів працівників повідомляє про відсутній файл, строк контролюється окремо.
- Власник повідомив, що протестував r4 і він, за його оцінкою, працює. Exact-main START, Windows, Win7-сумісність і macOS Intel/ARM — SUCCESS. [Стабільний випуск v10.15-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r4): 8 файлів, тег на product commit. GitHub Latest і відсутність prerelease перевірено після рішення власника. Опис релізу оновлено та звірено; тег і всі 8 виданих файлів залишилися незмінними.
- Лінія 10.15 також включає друк інструктажів та лист стажування, початковий каталог Word-файлів у `Data/PaperDocuments` та резервування цих файлів. Підпис, проведення і допуск не засвідчуються автоматично.
- **Інтегровано та випущено 10.15-r5:** [PR #312](https://github.com/RomanZavadaM/Taxo/pull/312), product/tag `0a5420cb9285ae5a8fc085c2689303d3e070ffbb`; [v10.15-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r5) — prerelease, 8 файлів. Власник перевірив каталог і не знайшов зауважень. Exact-product START, Windows, Win7-сумісність та macOS Intel/ARM — SUCCESS; фізичний Win7 і реальний SMB/NAS не перевірені.
- Перший спільний каталог показує накази та підготовлені документи; скани не реалізовані. Значне винесення старих частин і зменшення `main.py` ще попереду.
- Наступна кодова ревізія — **10.15-r6** після recovery checkpoint і визначення протоколу вкладень та резерву. Пріоритет — поетапна структурна перебудова; див. [#290](https://github.com/RomanZavadaM/Taxo/issues/290).

## Обмеження документації r4

У START-архіві та вихідному коді тега v10.15-r4 залишився попередній README з неактуальним станом r3. [Актуальний комплект опису, перекладів та інструкцій](docs/releases/DOCUMENTATION_v10.15-r4.md) доступний окремо і з опису випуску. Включити документи до наступного кодового випуску; тег r4 і файли не змінювати.

## Незмінні умови

План і факт розділені; оновлення не має вимагати повторного введення робочих даних. Бази, скани і персональні документи не входять у випуски. Повний backup включає документи працівників і `Data/PaperDocuments`; документи ТЗ, скани та Output — за відповідного вибору. Windows 7 має окрему лінію сумісності.

Історію попереднього стану збережено у приватній гілці `dev-strategy/profile/taxo/taxo-history/2026-11-10-before-10.15-r4/`, у журналі `WORKLOG.md`, Git та [індексі випусків](docs/releases/RELEASE_INDEX.md).

Історичний контрольний випуск: Taxo 10.3 / `v10.3`, source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.

## Recovery

`START_HERE.md` → `HANDOFF_CURRENT.md` → private Taxo-profile → live GitHub → цей файл.
