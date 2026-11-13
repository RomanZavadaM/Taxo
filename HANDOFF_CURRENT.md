# HANDOFF_CURRENT — Taxo

**13.11.2026 — Stable/Latest: v10.18-r3 (ПІДТВЕРДЖЕНО). Перевірений test checkpoint: 10.18-r4 (draft/unmerged). Наступна кодова ревізія — 10.18-r5.**

## Підтверджена база

- **Stable/Latest: [v10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3)**, exact immutable source/tag `65bc80ecae85793cb7c2c14edd4d3eabaa2b4470`, 8 assets: Windows/Win7 Setup + portable, macOS Intel/ARM portable, START, SHA256. Stable не змінювалася під час r4.
- **Попередня Stable / rollback:** [v10.17-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.17-r10) — незмінна.
- Продуктовий `main` перед цим docs-only recovery checkpoint — `f8649163e9d2d408dba6c827af4adbaa4ea16802`; код Stable r3 інтегрований, r4 у `main` **не зливалася**.
- **10.18-r4 перевірена як окремий test checkpoint:** [draft PR #393](https://github.com/RomanZavadaM/Taxo/pull/393), branch `work/v10.18-r4-tachograph-sorting`, exact head `eb762664dbd85650d3b8e5a6a59a7f3dfb4ea551`.
- r4: type-aware сортування каталогу тахокарт і таблиці інтервалів; стабільні row ID, повторне застосування сортування та відновлення видимого вибору після refresh; числовий `0` більше не вважається відсутнім значенням. SQLite schema, розпізнавання тахокарт, plan/fact, документи, backup, бібліотека шаблонів і сховище документів не змінені.
- Final exact-head CI: START/source [43388583728](https://github.com/RomanZavadaM/Taxo/actions/runs/43388583728) — SUCCESS, **1229/1229**; Windows [43388592068](https://github.com/RomanZavadaM/Taxo/actions/runs/43388592068) — SUCCESS; Win7 compatibility [43388591962](https://github.com/RomanZavadaM/Taxo/actions/runs/43388591962) — SUCCESS; macOS Intel/ARM [43388592056](https://github.com/RomanZavadaM/Taxo/actions/runs/43388592056) — SUCCESS.
- CI artifacts: START `14019367531`; Windows `14019114202`; Win7 `14019701961`; macOS Intel `14019752076`; macOS ARM64 `14020215887`.
- Спеціалізований **ручний** UI gate Windows DPI 100/125/150 %, фокус/табуляція, scrollbar/нижні кнопки, double-click та повторне відкриття лишається pending.
- Бібліотеку шаблонів і сховище документів **не чіпати** до окремої команди.

## Що не завершено

- r4 не merged у `main`, не tagged і не Stable; PR #393 лишається draft.
- Фізичне Windows UI/DPI приймання для неперевірених сценаріїв не підміняти CI.
- 25 сценаріїв, уже прийнятих власником на r3, без конкретного дефекту повторно не переробляти.

## Одна наступна дія

**Почати 10.18-r5 від exact verified r4 head `eb762664dbd85650d3b8e5a6a59a7f3dfb4ea551` після цього recovery checkpoint.** Продовжити карту `docs/maintenance/UI_NAVIGATION_CONSISTENCY_AUDIT_2026-11-12.md`. r5 — обов'язковий GitHub **Pre-release** з усіма portable-версіями (Windows, Win7, macOS Intel/ARM), START і SHA256. Stable v10.18-r3 не змінювати без рішення власника.

## Recovery

`START_HERE.md` → цей файл → live GitHub PR/CI/releases → private Taxo-profile → `PROJECT_RULES.md`, `PROJECT_STATE.md`.
