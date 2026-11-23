# HANDOFF_CURRENT — Taxo

**23.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r4 опублікована й перевірена.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false.

**Current Test:** [10.24-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r4), exact source `e1616ea0063575b2c989d684934364f38f995966`, 8 assets, prerelease=true. Publisher #45162074730 — SUCCESS. GitHub Latest лишається v10.24-r3.

## Що зроблено у 10.24-r4

- явні фактичні дії «Отримано…» / «Надіслано…» з обов'язковою датою;
- реєстрація або attachment не створюють факту sent/received;
- safe forward-only state transitions;
- append-only history переходів з from/to/action_date/changed_at;
- fail-closed перевірка пошкодженого history chain;
- legacy registry v1 мігрує без втрати нумерації;
- due date → read-only overdue для відкритих записів; без автоматичної зміни статусу;
- UI: «Змінити стан…», «Історія…», overdue counter;
- 760×520 reachability виправлена без послаблення regression test: action rows винесені з resizable card-pane у постійну нижню панель.

Prep PR #619 після виправлення: START #45157632285, Windows #45157632313, Win7 #45157632280, macOS #45157632297 — SUCCESS.
Candidate PR #622: START #45159393780, Windows #45159393870, Win7 #45159393814, macOS #45159393725 — SUCCESS.
Exact source `e1616ea...`: START #45160194606, Windows #45160194713, Win7 #45160194576, macOS #45160194864 — SUCCESS; Defender/integrity PASS.
Release-trigger PR #623 merged as `ee4958f3cf1470f120e3b28f853640fea272c803`; publisher #45162074730 — SUCCESS.

## Межі й наступна робота

Без automatic e-mail. Cases/threads, OCR/AI APPLY і physical attachment purge не входять у r4.
AI-ready import r6–r10 завершений на REVIEW без APPLY; APPLY не починати без окремого рішення власника.
#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Після recovery r4 наступний bounded correspondence slice визначити зі свіжого плану/issue; не змішувати з APPLY чи e-mail.

Recovery: START_HERE → HANDOFF_CURRENT → PROJECT_STATE → private `profile/taxo` → live GitHub.
