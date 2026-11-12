# HANDOFF_CURRENT — Taxo

**12.11.2026 — stable 10.16-r8; останній перевірений тестовий artifact-checkpoint 10.17-r1.**

## Підтверджений стан

- **Stable/Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**, immutable source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`. Stable і release assets не змінювалися.
- `main` зберігає код **10.16-r8**. Остання документаційна база перед цією сесією `d83e704ca13d5abc1792f594a15b5e803eecb8ad`. Тестові PR не зливати в `main` без прямого рішення власника.
- Попередній тестовий r9 має [immutable tag/release](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r9), exact `53428d4287c0f4e83a55a739109c0bd209e3a623` (draft PR #355); r10 має перевірений Actions artifact-checkpoint exact `1b39d60a7bce22843ebab575faa7173e3c818454` (draft PR #357) без tag/release.
- **Останній перевірений test checkpoint 10.17-r1**: [draft PR #359](https://github.com/RomanZavadaM/Taxo/pull/359), branch `work/v10.17-r1-vehicle-table-sorting`, exact code head `fa9ba20497cd179038129cb61ad9d72df1617cc0`. На звернення власника додано сортування натисканням заголовків для всіх 10 колонок реєстру ТЗ; наступне натискання змінює напрям, стрілка показує напрямок. ID/рік сортуються числово, назви — природно, `Документи` групує `Актуально` окремо від проблем (це **не** дозвіл на рейс). Сортування зберігається після `Оновити`; вибір авто відновлюється за ID; існуючий фільтр неактивних лишається незалежним.
- Спільний `src/taxo/table_sorting.py` підготовлений для інших таблиць, але в r1 змінено **тільки реєстр ТЗ**. Жодного масового втручання в інші екрани.
- CI exact-head [START/source 43193698666](https://github.com/RomanZavadaM/Taxo/actions/runs/43193698666), [Windows 43193742440](https://github.com/RomanZavadaM/Taxo/actions/runs/43193742440), [Win7/Python 3.8 43193742341](https://github.com/RomanZavadaM/Taxo/actions/runs/43193742341), [macOS Intel/ARM 43193742503](https://github.com/RomanZavadaM/Taxo/actions/runs/43193742503) — **усі SUCCESS**. START regression: **1154 tests OK**.
- START/source GitHub Actions artifact `13931428348`, назва `Taxo_v10_17_candidate_r1_START`, exact head confirmed. Windows artifact `13931254289`; Win7 `13932331375`; macOS Intel `13932850359`; macOS ARM `13931463723`. Це **CI artifacts**, не GitHub release. Для r1 tag/release **не створено**, stable не змінювали.
- Невикористана `work/v10.16-r9-order-editor-presets` лишається parked. Ревізії r9/r10/r1 не перевикористовувати.

## Рішення власника

- **Бібліотеку шаблонів і сховище документів поки не чіпати.** Не підхоплювати незалежний незавершений архів іншого ШІ.
- Продовжувати модульну перебудову інших систем, не скорочувати код заради рядків.
- Stable **10.16-r8 не змінювати** без прямої команди. Тестові ревізії — START або portable на контрольних точках.

## Наступна дія

1. Наступна сесія: `START_HERE.md` → HANDOFF → private Taxo-profile → live GitHub (main / draft #359 / CI exact-head).
2. Після 10.17-r1 наступна нова кодова ревізія — **10.17-r2**, не reuse r1.
3. Перевірити реакцію власника на сортування ТЗ; наступну окрему модульну або UI-роботу обрати поза бібліотекою шаблонів і сховищем документів. Пріоритет — стабільність, читабельність, захист даних.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
