# HANDOFF_CURRENT — Taxo

**27.11.2026 — Stable/Latest = 10.24-r9; Current Test = 10.25-r3.**

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r3), exact issued source `0c76b38b3aa3970245f430bee2bde7b5c062c5dd`, 8 canonical assets, prerelease=true.
- Current main after release trigger: `8f8dc5ef52db6bdecba4adee7d9ab4f7d77dc4a6`.

## 10.25-r3 — завершено

- Додано `briefing_planning_ui.py`: програми, незмінні редакції, read-only історія редакцій.
- Вибір працівників читає єдиний реєстр; пошук не скидає вже накопичений multi-select.
- Planned session створюється з frozen snapshot Taxo ID / ПІБ / табельного № / посади.
- Детермінований planning key залежить від програми, редакції, дати й набору людей; однаковий план не дублює session.
- Exact program revision створює DOCX через чинний PaperDocuments.
- Новий backward-compatible `Data/BriefingPreparedOutputs` зв'язує session з конкретним PaperDocuments record: document_id + filename + SHA-256.
- Повторна підготовка не створює другий DOCX; missing/tampered file fail-closed.
- Після перевіреного DOCX session стає тільки `prepared`; автоматичного `conducted` або підпису немає.
- Full workspace backup/restore зберігає planning store + output links + PaperDocuments.
- Додано strict live routes: `operations.instructions_planning`, `operations.instructions_program_revision`, `operations.instructions_prepare_planned`.
- Перший prep зловив реальний UI-регрес: нова кнопка зсунула стару «Створити комплект DOCX для друку» на 4 px за межу 940×600. Нову кнопку перенесено у верхній рядок; тест не послаблювали.
- Реальна база власника не відкривалась.

## Приймання r3

- Prep PR #665 закритий без merge після виконання ролі: final START #46051503140 — **1727/1727 PASS**; Windows #46051503134, Win7 #46051503176, macOS #46051503178 — SUCCESS; Defender/integrity PASS.
- Candidate PR #666: START #46052184007 — **1728/1728 PASS**, 6/6 r3 tests; Windows #46052183718, Win7 #46052183685, macOS #46052183788 — SUCCESS; Defender/integrity PASS.
- Exact issued source після merge #666: `0c76b38b3aa3970245f430bee2bde7b5c062c5dd`.
- Exact-source CI: START #46052986259 — 1728/1728 PASS; Windows #46052986192 SUCCESS; macOS #46052986186 SUCCESS.
- Exact Win7 #46052986213: attempt 1 дійшов до Defender, але update сигнатур дав мережевий timeout `0x80072ee2`; malware detection не було. Без зміни коду rerun attempt 2 на тому самому SHA — SUCCESS, Defender/integrity PASS.
- Release trigger PR #667 merged `8f8dc5ef52db6bdecba4adee7d9ab4f7d77dc4a6`.
- Publisher #46054871091 — SUCCESS.
- Release `v10.25-r3`: 8 assets, prerelease=true, target = exact issued source.
- Stable/Latest лишається 10.24-r9.

## Що далі

**10.25-r4 — «За подією» + явна ручна фіксація факту проведення.**

Межа r4: окрема дія «За подією» з обов'язковою підставою; event session не впливає на регулярний planned; явна дія «Зафіксувати проведення» з фактичною датою + evidence note; history/audit; жодного автоматичного conducted від друку/скану.

Після завершення r4: virtual/synthetic acceptance → full CI → окремий GitHub Test release. Stable 10.24-r9 не змінювати без окремого прямого рішення власника.

Execution plan: `docs/planning/INSTRUCTIONS_10_25_EXECUTION_PLAN_2026-11-27.md`.

Recovery: `START_HERE.md → HANDOFF_CURRENT.md → PROJECT_STATE.md → private profile/taxo → live GitHub → execution plan`.
