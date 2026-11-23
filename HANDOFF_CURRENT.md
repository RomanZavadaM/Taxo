# HANDOFF_CURRENT — Taxo

**23.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r6 опублікована й перевірена.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, GitHub Latest.

**Current Test:** [10.24-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r6), exact source `d713dd2b085216d8ec764fb16a3ab057f01f07ec`, 8 assets, prerelease=true, draft=false. Publisher #45209524416 — SUCCESS. Stable/Latest лишається v10.24-r3.

## Що зроблено у 10.24-r6

r6 не додає нової бізнес-логіки. Це контрольний пакет, який переводить критичні дії кореспонденції r1–r5 у strict executable live-control.

- у `function_registry.py` тепер **55 strict routes** загалом;
- **17 strict routes** належать кореспонденції;
- усі 17 correspondence routes мають `runtime_smoke=True`, mapping у `runtime_reachability.py` і живий Tk activation test;
- контролюються mapped + onscreen + usable + activation;
- захищено: центр кореспонденції, новий вхідний/вихідний, відповідь, вкладення, відкриття документа, фактичне отримано/надіслано, зміна стану, історія, створення/прив'язка/редагування/архів справи, додавання пов'язаних листів, відкриття й вилучення листа зі справи;
- `Відкрити документ` перевіряється через безпечний `order:` reference без запуску зовнішньої програми;
- data model registry/attachments/states/cases, sent/received, due/overdue, case membership і backup/restore не змінені.

## Перевірки 10.24-r6

Prep PR #629 final head `1d9a2f3de70eed3a27bf488cbbae7c6f29ddbecf`: START #45204102723, Windows #45204102869, Win7 #45204102379, macOS Intel/ARM #45204102369 — SUCCESS; Windows/Win7 Defender + integrity PASS.

Candidate PR #631 exact head `1824bf567e9e186f3b92a71d05b6c4e67a92153e`: START #45206383953, Windows #45206384077, Win7 #45206384595, macOS Intel/ARM #45206384273 — SUCCESS.

Merged candidate main/exact issued source `d713dd2b085216d8ec764fb16a3ab057f01f07ec`: START #45207404713, Windows #45207404491, Win7 #45207404242, macOS Intel/ARM #45207404447 — SUCCESS; Windows/Win7 Defender + integrity PASS.

Release-trigger PR #632 merged as `4dec0786d2dfc50e718f52901f8a012bf08d58e8`; trigger checks START #45208494055, Windows #45208494039, Win7 #45208494062, macOS #45208494429 — SUCCESS; publisher #45209524416 — SUCCESS.

## Що далі

- PR #630 **не входить у r6**. Це окремий пакет наскрізного контролю учасників наказу; його current head `97e09c8f8815e4f9183753a1607e3d24b919e707` був зелений на старій базі, але після r6 відстає від `main`.
- Після закриття recovery r6 перебазувати #630 на актуальний `main`, повторити повний CI і оформити як наступну ревізію, не змішуючи з r6.
- Automatic e-mail, mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не починати автоматично.
- #553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF_CURRENT → PROJECT_STATE → private `profile/taxo` → live GitHub.
