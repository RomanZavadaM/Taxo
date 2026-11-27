# HANDOFF_CURRENT — Taxo

**27.11.2026 — Stable/Latest = 10.24-r9; Current Test = 10.25-r2.**

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r2), exact issued source `f013e244ad42c9d5c101b5c5eacf4f55738fadbd`, 8 canonical assets, prerelease=true.
- Current main after release trigger: `460484945159ee3dc433c3f4f6b986a2c9872d73`.

## 10.25-r2 — завершено

- Додано `src/taxo/briefing_quarter_view.py`.
- У вкладці «Інструктажі та журнали» є кнопка **«На цей квартал…»**.
- Квартальний екран: попередній/наступний квартал, фільтр «Усі / БДР / Охорона праці», дата, вид, режим, програма, кількість працівників, стан.
- Стани: Заплановано / Підготовлено / Прострочено / Проведено; overdue похідний і не переписує історію.
- «Відкрити програму…» читає точну immutable program revision, на яку посилається session.
- Подієвий захід не закриває плановий.
- Explicit plan helper ідемпотентний: same planning_key + same spec повертає існуючий session; conflict не переписується.
- Додано strict live route `operations.instructions_quarter`; small-window 780×540 перевіряє mapped + onscreen + usable + activation.
- Реальна база власника не відкривалась.

## Приймання r2

- Prep START: **1721/1721 PASS**, 3/3 r2 scenarios.
- Candidate START: **1722/1722 PASS**, 4/4 r2 scenarios.
- Candidate PR #662: START #46035757012, Windows #46035757099, Win7 #46035757130, macOS #46035756981 — SUCCESS; Defender/integrity PASS.
- Exact issued source: `f013e244ad42c9d5c101b5c5eacf4f55738fadbd`.
- Exact-source CI: START #46036612119, Windows #46036612155, Win7 #46036612125, macOS #46036612192 — SUCCESS.
- Release trigger PR #663 merged `460484945159ee3dc433c3f4f6b986a2c9872d73`.
- Publisher #46037622127 — SUCCESS.
- Release `v10.25-r2`: 8 assets, prerelease=true, target = exact issued source.
- Stable/Latest лишається 10.24-r9.

## Що далі

**10.25-r3 — програми, вибір працівників і масова підготовка до друку.**

Межа r3: UI створення нової редакції програми без переписування старої; вибір груп/працівників із реєстру з накопиченням multi-select; explicit planned sessions із frozen snapshots; «Підготувати до друку» використовує PaperDocuments і ставить лише prepared, не conducted; backup/restore плану + готових DOCX.

Після завершення r3: virtual/synthetic acceptance → full CI → окремий GitHub Test release. Stable 10.24-r9 не змінювати без окремого прямого рішення власника.

Execution plan: `docs/planning/INSTRUCTIONS_10_25_EXECUTION_PLAN_2026-11-27.md`.

Recovery: `START_HERE.md → HANDOFF_CURRENT.md → PROJECT_STATE.md → private profile/taxo → live GitHub → execution plan`.
