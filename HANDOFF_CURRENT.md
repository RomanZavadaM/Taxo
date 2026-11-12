# HANDOFF_CURRENT — Taxo

**12.11.2026 — Stable / Latest: v10.17-r10 (ПІДТВЕРДЖЕНО). Остання перевірена test revision — 10.18-r1. Наступна кодова ревізія — 10.18-r2.**

## Підтверджена база

- **Stable/Latest: [v10.17-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.17-r10)**, exact immutable release source `6536a6da6cade49229fa1944e2aa47f941df40a6`, 8 assets, `prerelease=false`. Попередня Stable/rollback — [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8), exact `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`.
- Публічну документацію Stable синхронізовано через [PR #382](https://github.com/RomanZavadaM/Taxo/pull/382), merge `f054c33c7d3fdf5302534eaaef64e2cff26286d0`: README, Quick Start, User Manual, переклади та release index тепер показують 10.17-r10 / rollback 10.16-r8 і ведуть на фактичні release assets.
- **Останній перевірений test CODE checkpoint — 10.18-r1:** draft [PR #383](https://github.com/RomanZavadaM/Taxo/pull/383), branch `work/v10.18-r1-military-transport-sorting`, exact head `0d8a1e1d8fe6d767da48af4374932ecd4b331484`, **не merged у main і не Stable**.
- r1: у центрі «Військово-транспортний облік ТЗ» усі п'ять робочих таблиць мають type-aware сортування; дати/datetime/status сортуються за явними типами; повторний клік перемикає ▲/▼; після refresh сортування та виділення відновлюються за стабільним ID. SQLite schema і бізнес-дані не змінені.
- START/source [43280934103](https://github.com/RomanZavadaM/Taxo/actions/runs/43280934103) — **SUCCESS**, artifact [13971634693](https://github.com/RomanZavadaM/Taxo/actions/runs/43280934103/artifacts/13971634693) `Taxo_v10_18_candidate_r1_START`.
- Windows [43281001453](https://github.com/RomanZavadaM/Taxo/actions/runs/43281001453) — **SUCCESS**, executable artifact [13972961464](https://github.com/RomanZavadaM/Taxo/actions/runs/43281001453/artifacts/13972961464). Win7 [43281001344](https://github.com/RomanZavadaM/Taxo/actions/runs/43281001344) — **SUCCESS**, artifact [13972054443](https://github.com/RomanZavadaM/Taxo/actions/runs/43281001344/artifacts/13972054443). macOS Intel/ARM [43281001216](https://github.com/RomanZavadaM/Taxo/actions/runs/43281001216) — **SUCCESS**, artifacts [Intel 13971724906](https://github.com/RomanZavadaM/Taxo/actions/runs/43281001216/artifacts/13971724906), [ARM 13973026075](https://github.com/RomanZavadaM/Taxo/actions/runs/43281001216/artifacts/13973026075).
- r1 не створює GitHub Release: за рішенням власника автоматичний тестовий Pre-release потрібен на r5/r10. Stable/Latest лишається v10.17-r10.
- **Не прийнято вручну:** Windows DPI 100/125/150 %, фокус/табуляція, X із незбереженою чернеткою та повторне відкриття. Автоматичні тести не замінюють ручної перевірки.
- Бібліотеку шаблонів і сховище документів **не чіпати** до окремої команди.

## Одна наступна дія

**Почати 10.18-r2 від exact test head `0d8a1e1d8fe6d767da48af4374932ecd4b331484`** і продовжити карту `docs/maintenance/UI_NAVIGATION_CONSISTENCY_AUDIT_2026-11-12.md`: наступним ізольованим проходом перевірити робочі таблиці та службові Toplevel військового обліку працівників (`military_accounting_ui.py`) на сортування, стабільний вибір, явний вихід, X та повторне відкриття. Stable не змінювати; ручний Windows UI/DPI gate лишити pending.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile `RomanZavadaM/dev-strategy:profile/taxo/TAXO_PROFILE.md` → live GitHub PR #383 / CI / releases → `PROJECT_RULES.md` та `PROJECT_STATE.md`.
