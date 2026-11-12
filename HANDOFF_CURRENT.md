# HANDOFF_CURRENT — Taxo

**12.11.2026 — Stable/Latest v10.18-r3 (ПІДТВЕРДЖЕНО). Наступна кодова ревізія — 10.18-r4.**

## Підтверджена база

- **Stable/Latest:** [v10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3), exact tag/source `65bc80ecae85793cb7c2c14edd4d3eabaa2b4470`, 8 assets (2 Windows Setup, 4 portable, START, SHA256). Guarded promotion [43303075684](https://github.com/RomanZavadaM/Taxo/actions/runs/43303075684) — **SUCCESS**. Попередня immutable rollback — [v10.17-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.17-r10) (8 assets).
- **Код інтегровано:** PR [#387](https://github.com/RomanZavadaM/Taxo/pull/387) merged `cff3e8fe10bc210b67a1fb1dfb00efd092e30aee`. Sync CI Windows/Win7/macOS Intel/ARM — SUCCESS, exact merge-validation head `e98b9ab29a9b071ad19aefad1ae093a58a8a5910`.
- **Релізний marker:** PR [#388](https://github.com/RomanZavadaM/Taxo/pull/388) merged `743c8f94d784f389538c5181f80578635fc79fd1`, generic publisher штатно SKIPPED, guarded publisher SUCCESS.
- **Ручне приймання власником:** 25/25 PASS без зауважень для навігації/виходів, сортування таблиць і вибору після refresh, СТОІР та військового обліку. Доказ — коментар у PR #387.
- Бібліотека шаблонів і сховище документів **відкладені**. Не змінювати до окремого рішення.
- Не вважати 25/25 доказом окремих Windows DPI 100/125/150 %, keyboard focus/tab і всіх малих viewport; ці gates залишаються pending.

## Одна наступна дія

**Почати 10.18-r4** після preflight від фактичного `main`: спершу regression на крайні випадки відображення/сортування (порожні дати, числовий нуль, відсутні значення); далі наступний ізольований неперевірений UI slice за `docs/maintenance/UI_NAVIGATION_CONSISTENCY_AUDIT_2026-11-12.md`. Не перевикористовувати r3, не порушувати Stable та backup. Для r5 — тестовий Pre-release з portable.

## Recovery

`START_HERE.md` → цей HANDOFF → приватний Taxo-profile → live GitHub `main`/CI/releases → `PROJECT_RULES.md` і `PROJECT_STATE.md`.
