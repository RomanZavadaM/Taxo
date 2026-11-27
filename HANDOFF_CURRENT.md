# HANDOFF_CURRENT — Taxo

**27.11.2026 — Stable/Latest = 10.24-r9; Current Test = 10.25-r4.**

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r4), exact issued source `ed3b79a96659aa011f60fa7912092fbc15157cdb`, 8 canonical assets, prerelease=true.
- Current main after release trigger: `f1f4724910ffc1935a7f08bc4e9e27fff3224ad6`.

## 10.25-r4 — завершено

- Додано окрему дію **«За подією…»** у модулі інструктажів.
- Підстава події обов'язкова; event session не закриває й не змінює regular planned session.
- Вибір працівників бере shared registry і накопичується під час пошуку.
- Event session зберігає exact program revision і frozen snapshots працівників.
- Event можна лише створити або створити + підготувати DOCX; DOCX змінює стан максимум на `prepared`.
- У квартальному вікні додано **«Зафіксувати проведення…»**: фактична дата + обов'язкова примітка/посилання на паперовий запис.
- Уже зафіксований `conducted` факт не переписується іншою датою/приміткою.
- **«Історія…»** read-only показує mode/reason/program revision/frozen people/created/updated/prepared/conducted/evidence/prepared DOCX + SHA-256.
- Strict live routes: open event, create event, manual conducted save, history.
- Full backup/restore зберігає event + evidence + prepared output.
- Реальна база власника не відкривалась.

## Приймання r4

- Prep PR #669 закритий без merge після ролі: START #46058038769 — **1731/1731 PASS**; Windows #46058038848, Win7 #46058038768, macOS #46058038830 — SUCCESS; Defender/integrity PASS.
- Candidate PR #670: START #46060419818 — **1732/1732 PASS**, 4/4 r4 scenarios; Windows #46060419824, Win7 #46060419944, macOS #46060419876 — SUCCESS; Defender/integrity PASS.
- Exact issued source після merge #670: `ed3b79a96659aa011f60fa7912092fbc15157cdb`.
- Exact-source CI: START #46061028041, Windows #46061028147, Win7 #46061028060, macOS #46061028199 — SUCCESS; Defender/integrity PASS.
- Release trigger PR #671 merged `f1f4724910ffc1935a7f08bc4e9e27fff3224ad6`.
- Trigger Win7 #46061090608 attempt 1 failed only on Defender signature-update network timeout `0x80072ee2`; no malware detection. Rerun attempt 2 on the same SHA — SUCCESS, Defender/integrity PASS.
- Publisher #46062424737 — SUCCESS.
- Release `v10.25-r4`: 8 assets, prerelease=true, draft=false, target = exact issued source.
- Stable/Latest лишається 10.24-r9.

## Що далі

**10.25-r5 — наскрізне контрольне приймання Інструктажів.**

Synthetic/virtual full cycle: program revision → quarter plan → employees → prepared DOCX → close/reopen → event briefing → manual conducted fact → overdue control → full backup/restore → equality/integrity. Це контрольний етап без автоматичного `conducted` і без робочої бази власника.

Після завершення r5: full CI → окремий GitHub Test release → ручне owner acceptance UI. Лише після цього вирішувати, чи закривати #237 і переходити до наступного великого блоку — єдиного сховища документів.

Execution plan: `docs/planning/INSTRUCTIONS_10_25_EXECUTION_PLAN_2026-11-27.md`.

Recovery: `START_HERE.md → HANDOFF_CURRENT.md → PROJECT_STATE.md → private profile/taxo → live GitHub → execution plan`.
