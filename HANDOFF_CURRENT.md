# HANDOFF_CURRENT — Taxo

**12.11.2026 — Stable/Latest: v10.18-r3 (ПІДТВЕРДЖЕНО). Наступна кодова ревізія — 10.18-r4.**

## Підтверджена база

- **Stable/Latest: [v10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3)**, exact immutable source/tag `65bc80ecae85793cb7c2c14edd4d3eabaa2b4470`, 8 assets: Windows/Win7 Setup + portable, macOS Intel/ARM portable, START, SHA256. Full guarded release run [43303075684](https://github.com/RomanZavadaM/Taxo/actions/runs/43303075684) — SUCCESS.
- **Попередня Stable / rollback:** [v10.17-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.17-r10) — незмінна.
- Код 10.18-r1/r2/r3 (типізоване сортування військового обліку та СТОІР, стабільний вибір, контроль дочірніх вікон) інтегровано через [PR #387](https://github.com/RomanZavadaM/Taxo/pull/387), merge `cff3e8fe10bc210b67a1fb1dfb00efd092e30aee`; релізні маркери через [PR #388](https://github.com/RomanZavadaM/Taxo/pull/388), merge `743c8f94d784f389538c5181f80578635fc79fd1`.
- Owner manual acceptance **25/25 PASS** на r3 без зауважень (коментар у PR #387). Exact-source Windows, Win7, macOS Intel/ARM і START CI — SUCCESS; повторний CI інтеграції та promotion — SUCCESS.
- Спеціалізований ручний UI gate Windows DPI 100/125/150 %, фокус/табуляція/scrollbar не вважати автоматично пройденим.
- Бібліотеку шаблонів і сховище документів **не чіпати** до окремої команди.

## Одна наступна дія

**Почати 10.18-r4 від актуального main після цього docs checkpoint.** Продовжити UI-аудит решти ще не перевірених робочих таблиць та Toplevel; regression для відсутніх дат, нульових числових значень і сортування; не переписувати 25 прийнятих сценаріїв без конкретного дефекту. Stable v10.18-r3 не змінювати. Тестовий Pre-release із portable assets обов'язковий на r5.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub PR/CI/releases → `PROJECT_RULES.md`, `PROJECT_STATE.md`.
