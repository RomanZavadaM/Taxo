# HANDOFF_CURRENT — Taxo

**23.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r7 опублікована й перевірена.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, GitHub Latest.

**Current Test:** [10.24-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r7), exact source `4221b8baaeae4fad6ca8b6ebf4640a4a34050e2d`, 8 assets, prerelease=true, draft=false. Publisher #45220620129 — SUCCESS. Stable/Latest лишається v10.24-r3.

## Що зроблено у 10.24-r7

r7 не змінює бізнес-правила наказів. Це наскрізний контроль структурованого блоку **«Учасники / ТЗ»** поверх уже прийнятого механізму наказів.

- у Taxo тепер **58 strict live routes** загалом;
- correspondence-contract r6 лишається точним набором із **17 correspondence routes**;
- order participant block має 5 live routes: пошук/вибір, редагування ролі/примітки, додавання ТЗ, вилучення вибраних, live preview sync;
- add/edit/remove працівників і ТЗ автоматично оновлюють уже відкритий preview;
- історія редагування ролі/примітки фіксує зрозумілу подію;
- preview прямо пояснює, що структурований список учасників друкується окремою сторінкою;
- DOCX і PDF використовують той самий frozen participant snapshot;
- full workspace backup/restore зберігає entity identity, role, note, snapshot і sequence;
- live preservation guard включає «Змінити роль / примітку…».

## Перевірки 10.24-r7

Prep PR #630 final head `d252143339c5406264868bfe92f804a75d348fab`: START #45213479378, Windows #45213479658, Win7 #45213479371, macOS Intel/ARM #45213479464 — SUCCESS; Windows/Win7 Defender + integrity PASS. Prep merged у main як `31153fb3c706c746b711c5382c37edc2ecddab53`.

Candidate PR #634 exact head `a3889723b58bdbbf1fd174cb14024a3e3beaadb3`: START #45216365054, Windows #45216364728, Win7 #45216364723, macOS Intel/ARM #45216364729 — SUCCESS.

Merged candidate / exact issued source `4221b8baaeae4fad6ca8b6ebf4640a4a34050e2d`: START #45217452473, Windows #45217452461, Win7 #45217452456, macOS Intel/ARM #45217452990 — SUCCESS; Windows/Win7 Defender + integrity PASS.

Release-trigger PR #635 merged as `ee7bdbb5e50e3b47e42da46fc7b47eee2991523e`. Trigger: START #45218698014, Windows #45218698050, macOS #45218698263 — SUCCESS. Win7 #45218698024 first attempt hit one old catalog-reader timing failure; rerun of the same unchanged job/head passed full regression, build, Defender and integrity. Publisher #45220620129 — SUCCESS.

GitHub Release `v10.24-r7`: exact target `4221b8baaeae4fad6ca8b6ebf4640a4a34050e2d`, 8 canonical assets, prerelease=true, draft=false. Stable/Latest remains `v10.24-r3`.

## Що далі

- Спочатку закрити recovery r7 у public docs, private `profile/taxo`, Issue #61 і Google Drive.
- Після recovery звірити #553/#556 і вибрати один наступний bounded control slice; не змішувати кілька великих механізмів у r8.
- Automatic e-mail, mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не починати автоматично.
- Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF_CURRENT → PROJECT_STATE → private `profile/taxo` → live GitHub.
