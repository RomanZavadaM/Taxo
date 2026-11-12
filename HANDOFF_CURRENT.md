# HANDOFF_CURRENT — Taxo

**12.11.2026 — Stable / Latest: v10.17-r10 (ПІДТВЕРДЖЕНО). Остання перевірена test revision — 10.18-r2. Наступна кодова ревізія — 10.18-r3.**

## Підтверджена база

- **Stable/Latest: [v10.17-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.17-r10)**, exact immutable release source `6536a6da6cade49229fa1944e2aa47f941df40a6`, 8 assets. Rollback — [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8).
- Публічна документація Stable синхронізована через PR #382, merge `f054c33c7d3fdf5302534eaaef64e2cff26286d0`.
- **Останній перевірений test CODE checkpoint — 10.18-r2:** draft [PR #385](https://github.com/RomanZavadaM/Taxo/pull/385), branch `work/v10.18-r2-military-accounting-ui`, exact head `67772f0884d2a82a05953cf2e80cdd80d97a983a`, **не merged у main і не Stable**.
- r1 (входить у r2): type-aware сортування п'яти таблиць військово-транспортного обліку ТЗ, stable selection після refresh.
- r2: три вікна військового обліку працівників стали single-instance; таблиці дій і офіційних звірянь отримали type-aware sorting + stable selection; перед «Позначити виконаною» додано підтвердження. Спільний sort/selection helper винесено в `table_sorting.py`. Юридичні строки та SQLite schema не змінені.
- START/source [43283089055](https://github.com/RomanZavadaM/Taxo/actions/runs/43283089055) — **SUCCESS**, artifact [13974580181](https://github.com/RomanZavadaM/Taxo/actions/runs/43283089055/artifacts/13974580181) `Taxo_v10_18_candidate_r2_START`.
- Windows [43283188306](https://github.com/RomanZavadaM/Taxo/actions/runs/43283188306) — **SUCCESS**, artifact [13973897367](https://github.com/RomanZavadaM/Taxo/actions/runs/43283188306/artifacts/13973897367). Win7 [43283188213](https://github.com/RomanZavadaM/Taxo/actions/runs/43283188213) — **SUCCESS**, artifact [13973523015](https://github.com/RomanZavadaM/Taxo/actions/runs/43283188213/artifacts/13973523015). macOS Intel/ARM [43283188271](https://github.com/RomanZavadaM/Taxo/actions/runs/43283188271) — **SUCCESS**, artifacts [Intel 13972718485](https://github.com/RomanZavadaM/Taxo/actions/runs/43283188271/artifacts/13972718485), [ARM 13972693537](https://github.com/RomanZavadaM/Taxo/actions/runs/43283188271/artifacts/13972693537).
- r2 не створює GitHub Release: тестові Pre-release автоматично потрібні на r5/r10. Stable/Latest лишається v10.17-r10.
- **Ручний gate pending:** Windows DPI 100/125/150 %, фокус/табуляція, X/«Закрити», незбережені дані та повторне відкриття.
- Бібліотеку шаблонів і сховище документів **не чіпати** до окремої команди.

## Одна наступна дія

**Почати 10.18-r3 від exact test head `67772f0884d2a82a05953cf2e80cdd80d97a983a`** і продовжити UI-аудит одним ізольованим проходом робочих таблиць СТОІР: сортування, стабільний вибір після refresh, вихід/X і destructive actions. Stable не змінювати; ручний Windows gate лишити pending.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub PR #385 / CI / releases → `PROJECT_RULES.md` та `PROJECT_STATE.md`.
