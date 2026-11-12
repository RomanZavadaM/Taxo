# HANDOFF_CURRENT — Taxo

**12.11.2026 — stable 10.16-r8; останній перевірений тестовий artifact-checkpoint 10.17-r3.**

## Підтверджений стан

- **Stable/Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**; immutable source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`. `main` зберігає код 10.16-r8; stable і release assets не змінювалися.
- Раніші тестові checkpoints: `10.16-r9` exact `53428d4287c0f4e83a55a739109c0bd209e3a623` (draft #355, tagged test release), `10.16-r10` exact `1b39d60a7bce22843ebab575faa7173e3c818454` (draft #357), `10.17-r1` exact `fa9ba20497cd179038129cb61ad9d72df1617cc0` (draft #359), `10.17-r2` exact `eb77fa477e75daa9a9264fbab4f07adf99184d2b` (draft #361).
- **Останній тестовий checkpoint 10.17-r3:** [draft PR #363](https://github.com/RomanZavadaM/Taxo/pull/363), `work/v10.17-r3-stoir-navigation`, exact head `190f920b78160dca2510321921631ee720bd8d16`, **не merged у main**. За картою UX-аудиту додано видиму кнопку «Закрити» у заголовку двох окремих центрів: СТОІР та військово-транспортного обліку ТЗ. Команда закриває лише відповідне дочірнє вікно (`win.destroy`); існуюча логіка повторного відкриття збережена. Схеми, бізнес-дані, backup та вкладені форми не змінені.
- Аудит, відомі межі та черга приймання — `docs/maintenance/UI_NAVIGATION_CONSISTENCY_AUDIT_2026-11-12.md` у PR #363. Це **аналіз коду**, а не твердження про повне ручне тестування UI. Пріоритет далі: дочірні діалоги СТОІР (Зберегти/Скасувати/X, незбережений ввід), тахограф, маршрути, решта Toplevel, таблиці/сортування, масштабування/DPI.
- START/source run [43216847925](https://github.com/RomanZavadaM/Taxo/actions/runs/43216847925) — **SUCCESS, 1163 tests OK**, head `605cc1de6ff1356c3b9504ab66ba4f5d9bc27b73`; наступний і фінальний commit тільки оновив Markdown audit. Платформні CI фінального head: Windows [43216987040](https://github.com/RomanZavadaM/Taxo/actions/runs/43216987040), Win7/Python 3.8 [43216986869](https://github.com/RomanZavadaM/Taxo/actions/runs/43216986869), macOS Intel/ARM [43216987211](https://github.com/RomanZavadaM/Taxo/actions/runs/43216987211) — **усі SUCCESS**.
- CI artifacts: START `13944281665` на попередньому code-identical head; Windows `13943334510`, Win7 `13944272142`, macOS Intel `13943932746`, ARM `13943783179` — усі три платформні workflows на exact final head. Windows portable `Taxo_v10_17_candidate_r3_Windows_x64_Portable.zip` витягнуто з CI; SHA-256 `14e41b76d17b7dfd03e6b10781e0e03370c16d26baf3f75bbe6762a4fbd8c008` збігається з маніфестом.
- r3 — перевірений Actions artifact-checkpoint **без GitHub tag/release**. Стабільна версія не змінюється.

## Рішення власника

- Працювати по карті аудиту інтерфейсу, послідовно виправляти підтверджені неузгодженості й захищати існуючі функції.
- **Бібліотеку шаблонів і сховище документів не чіпати.** До їхнього проєктування повернутися лише після завершення поточного етапу в окремому чаті.
- Stable `10.16-r8` не змінювати; тестові ревізії не зливати в main без прямої команди.

## Наступна дія

1. Recovery: `START_HERE.md` → цей файл → private Taxo-profile → live GitHub (main / PR #363 / CI).
2. **Наступна нова кодова ревізія 10.17-r4:** продовжити за картою, насамперед перевірку дочірніх діалогів СТОІР, збереження/скасування/X та повторного відкриття; не торкатися припаркованих документних систем.
3. Окремо провести ручний UI smoke на Windows, включно з DPI та маршрутами; automation і source regression не замінюють це приймання.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
