# HANDOFF_CURRENT — Taxo

**23.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r5 опублікована й перевірена.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, GitHub Latest.

**Current Test:** [10.24-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r5), exact source `6d697a641b4f546dc533c8f55379696ad827b278`, 8 assets, prerelease=true, draft=false. Publisher #45193506957 — SUCCESS. Stable/Latest лишається v10.24-r3.

## Що зроблено у 10.24-r5

- окремі логічні **справи/теми кореспонденції** зі stable `cc-...` ID;
- case-store зберігається окремо у `Data/CorrespondenceCases/cases.json`; strict `Data/Correspondence` не послаблено;
- справа містить лише ID вже зареєстрованих листів, назву/примітки та archive state — файли, скани й attachment bytes не копіюються;
- один лист у r5 належить максимум одній справі; переміщення між справами атомарне;
- архівована справа read-only до явного відновлення;
- existing `response_to_ids` / `related_ids` використовуються як thread-кандидати; «Додати пов'язані» працює лише після підтвердження користувача;
- UI: третя вкладка «Справи», «Справа…» у картці листа, browser справи/ланцюжка, відкриття листа назад у журнал і вилучення зі справи без видалення листа;
- повний backup/restore зберігає case-store і membership;
- case actions фізично доступні при 760×520; START package guard вимагає `correspondence_cases.py`.

## Перевірки 10.24-r5

Prep PR #625: START #45169334073, Windows #45169334161, Win7 #45169334164, macOS Intel/ARM #45169334069 — SUCCESS; Windows/Win7 Defender + integrity PASS.

Candidate PR #626: START #45190123472, Windows #45190123183, Win7 #45190124279, macOS Intel/ARM #45190123566 — SUCCESS; Windows/Win7 Defender + integrity PASS.

Exact source `6d697a641b4f546dc533c8f55379696ad827b278`: START #45191514761, Windows #45191514632, Win7 #45191514666, macOS Intel/ARM #45191514659 — SUCCESS; Windows/Win7 Defender + post-scan integrity PASS.

Release-trigger PR #627 merged as `53127f27929b7f1c72c6876ce4a048c9955d02de`; trigger checks START #45192571617, Windows #45192571441, Win7 #45192571278, macOS #45192571563 — SUCCESS; publisher #45193506957 — SUCCESS.

## Важливі межі

- Case membership не змінює registration number, sent/received, status, due date чи attachment history.
- Реєстрація/attachment як і раніше не створюють sent/received.
- Automatic e-mail, mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не входять у r5.
- Після recovery r5 наступний bounded correspondence slice визначити окремо зі свіжого плану; не починати зовнішні інтеграції автоматично.
- #553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF_CURRENT → PROJECT_STATE → private `profile/taxo` → live GitHub.
