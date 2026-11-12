# HANDOFF_CURRENT — Taxo

**12.11.2026 — stable 10.16-r8; останній перевірений test code/artifact-checkpoint 10.17-r10; Pre-release НЕ опубліковано.**

## Підтверджений стан

- **Stable/Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**, stable source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`; stable code/tag/assets незмінні.
- **Останній перевірений test CODE checkpoint — 10.17-r10:** [draft PR #378](https://github.com/RomanZavadaM/Taxo/pull/378), branch `work/v10.17-r10-order-history-sorting`, exact head `4d74649bb0e1904321cc196bced3e645a50d3e7a`, не merged у `main`.
- r10: журнал історії наказів сортується за чотирма заголовками, включно з повним datetime (хронологія з годинами/хвилинами/секундами). Повторний клік перемикає ▲/▼. Журнал лишається read-only; «Закрити»/X не змінюють БД. Додано regression і UI-аудит. Код r10 накопичує r1–r9.
- START/source run [43253284345](https://github.com/RomanZavadaM/Taxo/actions/runs/43253284345) — **SUCCESS, 1205 tests OK**. Windows [43253295294](https://github.com/RomanZavadaM/Taxo/actions/runs/43253295294), Win7/Python 3.8 [43253294988](https://github.com/RomanZavadaM/Taxo/actions/runs/43253294988), macOS Intel/ARM [43253295224](https://github.com/RomanZavadaM/Taxo/actions/runs/43253295224) — усі **SUCCESS** на exact code head.
- **Тимчасові виконувані Actions archives:** [Windows x64](https://github.com/RomanZavadaM/Taxo/actions/runs/43253295294/artifacts/13960276960), [Windows 7](https://github.com/RomanZavadaM/Taxo/actions/runs/43253294988/artifacts/13961051624), [macOS Intel](https://github.com/RomanZavadaM/Taxo/actions/runs/43253295224/artifacts/13960601723), [macOS ARM](https://github.com/RomanZavadaM/Taxo/actions/runs/43253295224/artifacts/13961590915), [START/source](https://github.com/RomanZavadaM/Taxo/actions/runs/43253284345/artifacts/13961430842).
- **ПУБЛІКАЦІЯ Pre-release r10 ЩЕ НЕ ВИКОНАНА.** Штатний `.github/workflows/publish-current.yml` має ручний `workflow_dispatch`, який при запуску на гілці r10 збирає готові exact-head файли, додає START, SHA256 і створює immutable GitHub Pre-release. `docs/releases/RELEASE_NOTES_v10.17-r10.md` створено на r10 branch. Поточне GitHub-підключення дозволяє читати Actions, але НЕ має `workflow_dispatch`/create-release дії. **Не запускати publisher від `main`**: `main` ще має stable code 10.16-r8. Для публікації відкрити [Publish current Taxo release](https://github.com/RomanZavadaM/Taxo/actions/workflows/publish-current.yml), натиснути **Run workflow**, вибрати `work/v10.17-r10-order-history-sorting`, перевірити SUCCESS, після цього підтвердити новий `v10.17-r10` у [Releases](https://github.com/RomanZavadaM/Taxo/releases) та assets. Доки результат не перевірено, **не називати r10 виданим релізом**.
- Відповідно до нового рішення власника, кожні r5/r10 мають виходити як тестові GitHub Pre-release з усіма portable; «зливай у main» означає повний stable release. Правило інтегроване в `PROJECT_RULES.md` через docs-only PR #377.
- **Ручний Windows UI/DPI gate** 100/125/150 %, фокус, X із незбереженими даними та повторне відкриття залишаються pending. Бібліотеку шаблонів і сховище документів не чіпати.

## Рішення власника

- Продовжувати карту аудиту й перевіряти не лише кнопки, а навігацію, доступність функцій, збереження даних і регресії.
- **Бібліотеку шаблонів і сховище документів не чіпати**; повернутися до їх проєктування окремо після завершення поточної роботи.
- Продовжувати модульну перебудову; скорочення коду не є ціллю.
- Stable 10.16-r8 не змінювати; тестовий код не зливати в `main` без прямої команди.

## Наступна дія

1. `START_HERE.md` → цей файл → private Taxo-profile → live GitHub `main` / PR #378 exact head і чотири CI → `PROJECT_STATE.md`.
2. **Пріоритет — завершити плановий r10 Pre-release:** запустити штатний `Publish current Taxo release` на гілці `work/v10.17-r10-order-history-sorting` (не `main`), звірити immutable tag, portable Windows/Win7/macOS Intel/ARM, START, installers, SHA256 та `prerelease=true`, `Latest` все ще 10.16-r8. Наразі ручний GitHub workflow dispatch недоступний цьому підключенню; не обходити release/security workflow.
3. **Наступна кодова ревізія після завершення r10 checkpoint — 10.18-r1.** Продовжити інші робочі таблиці та Toplevel за картою аудиту, із окремим CI та recovery; stable не змінювати, тестовий код без команди власника у `main` не зливати.
4. Бібліотеку шаблонів і сховище документів не чіпати. Ручний Windows UI smoke залишається окремим прийманням.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
