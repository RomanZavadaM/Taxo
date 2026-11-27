# HANDOFF_CURRENT — Taxo

**27.11.2026 — Stable/Latest = 10.24-r9; Current Test = 10.25-r5.**

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r5), exact issued source `70bc3c6bf88f6edfd9f1ae1865c1efb3249ec2f3`, 8 canonical assets, prerelease=true.
- Current main after release trigger: `2627a57d8d63313f9eaf500ef17c123d4b700f35`.

## 10.25-r5 — завершено

r5 не додає нових бізнес-правил. Це фінальний synthetic end-to-end gate усієї лінії Інструктажів r1–r4:

1. immutable program revision 1;
2. regular planned session із frozen працівниками;
3. exact prepared DOCX у PaperDocuments + session link + SHA-256;
4. program revision 2 без переписування старого plan;
5. повне повторне читання planning/output stores з диска;
6. event session на revision 2 з обов'язковою підставою;
7. event prepared DOCX;
8. explicit manual conducted fact з фактичною датою і paper evidence note;
9. regular plan не закривається event-ом і як derived state стає overdue;
10. quarter view відкриває exact r1 для regular plan і exact r2 для event;
11. full workspace backup → restore у чистий root;
12. рівність planning state, prepared-output links, PaperDocuments records і SHA-256 файлів;
13. повтор того самого regular plan після restore не створює третій session/DOCX;
14. generated DOCX / paper_signed=false ніколи автоматично не створює conducted fact.

Реальна база власника не відкривалась.

## Приймання r5

- Prep: START #46063110841 — **1734/1734 PASS**; Windows #46063110844, Win7 #46063110813, macOS #46063111267 — SUCCESS; Defender/integrity PASS.
- Candidate #674 після двох службових identity fixes: START #46064508828 — **1735/1735 PASS**, 3/3 r5 controls; Windows #46064508796, Win7 #46064508832, macOS #46064508804 — SUCCESS; Defender/integrity PASS.
- Exact issued source після merge #674: `70bc3c6bf88f6edfd9f1ae1865c1efb3249ec2f3`.
- Exact-source CI: START #46065219246 — 1735/1735 PASS; Windows #46065219433, Win7 #46065219339, macOS #46065219355 — SUCCESS; Defender/integrity PASS.
- Release trigger #675 merged `2627a57d8d63313f9eaf500ef17c123d4b700f35`.
- Publisher #46065911225 — SUCCESS.
- Release `v10.25-r5`: 8 canonical assets, prerelease=true, draft=false, exact target `70bc3c6b…`.
- Stable/Latest лишається `v10.24-r9`.

## Що далі

**Issue #237 НЕ закривати до ручного owner UI acceptance.** Автоматичне virtual acceptance підтвердило дані, маршрути, пакети й backup/restore, але не підміняє ручне користування інтерфейсом.

Під час ручного приймання перевірити:
- «На цей квартал…» у реальному вікні;
- фільтри БДР/ОП, перемикання кварталу, exact revision;
- «Програми / план / друк…»;
- накопичувальний вибір працівників через пошук;
- нова програма / нова редакція / історія;
- «Підготувати DOCX» і зрозумілий статус prepared;
- «За подією…»;
- «Зафіксувати проведення…» з фактичною датою й paper evidence;
- «Історія…»;
- small-window / X / Закрити / Скасувати / повторне відкриття.

Лише після owner acceptance вирішувати, чи закривати #237 і переходити до наступного великого блоку — **єдиного сховища документів**.

Execution plan: `docs/planning/INSTRUCTIONS_10_25_EXECUTION_PLAN_2026-11-27.md`.

Recovery: `START_HERE.md → HANDOFF_CURRENT.md → PROJECT_STATE.md → private profile/taxo → live GitHub`.
