# HANDOFF_CURRENT — Taxo

**27.11.2026 — Stable/Latest = 10.24-r9; Current Test = 10.25-r1.**

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r1), exact issued source `2e0a0df392b5b79b6e2efbf1793df470bf6623f8`, 8 canonical assets, prerelease=true.
- Current main after release trigger: `44e20e7bac1803afb1b9853a821c60e6154780db`.

## 10.25-r1 — завершено

- Додано `src/taxo/briefing_planner.py` і `Data/BriefingPlanning`.
- Незмінні редакції програм; planned/event sessions; frozen snapshot працівників.
- Unique `planning_key` блокує дублювання планового заходу.
- Event session має обов'язкову підставу і не закриває planned session.
- `prepared` / друк не означає `conducted`.
- `conducted` потребує явної фактичної дати та примітки/посилання на паперовий запис; вже зафіксований факт не переписується мовчки.
- `overdue` обчислюється без автоматичного запису в історію.
- JSON store fail-closed; full workspace backup/restore зберігає planning store.
- Реальна база власника не відкривалась.

## Приймання r1

- Prep START: 1717/1717 PASS; 3/3 нових r1 scenarios.
- Candidate START: **1718/1718 PASS**; 4/4 r1 scenarios.
- Candidate PR #658: START #46027162850, Windows #46027162761, Win7 #46027162706, macOS #46027162770 — SUCCESS; Defender/integrity PASS.
- Exact issued source: `2e0a0df392b5b79b6e2efbf1793df470bf6623f8`.
- Exact-source CI: START #46028063211, Windows #46028063203, Win7 #46028063190, macOS #46028062948 — SUCCESS.
- Release trigger PR #659 merged `44e20e7bac1803afb1b9853a821c60e6154780db`.
- Publisher #46032557836 — SUCCESS.
- Release `v10.25-r1`: 8 assets, prerelease=true, target = exact issued source.
- Stable/Latest лишається 10.24-r9.

## Що далі

**10.25-r2 — екран «На цей квартал» поверх r1 planning store.**

Межа r2: квартальний view, перемикання кварталу, planned/prepared/overdue/conducted, фільтр БДР/ОП, відкриття точної редакції програми, повторне формування без дублів, small-window/live-route control. Жодного автозакриття інструктажу.

Після завершення r2: virtual/synthetic acceptance → full CI → окремий GitHub Test release. Stable 10.24-r9 не змінювати без окремого прямого рішення власника.

Execution plan: `docs/planning/INSTRUCTIONS_10_25_EXECUTION_PLAN_2026-11-27.md`.

Recovery: `START_HERE.md → HANDOFF_CURRENT.md → PROJECT_STATE.md → private profile/taxo → live GitHub → execution plan`.
