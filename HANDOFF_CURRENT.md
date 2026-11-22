# HANDOFF_CURRENT — Taxo

**22.11.2026 — 10.24-r2 опубліковано як Test prerelease; Stable/Latest лишається 10.23-r4.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`, GitHub Latest.

**Current Test:** [10.24-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r2), exact source `d07f26d8e9e9db6d33278cac5a0199e2d8ae4b50`, 8 assets, prerelease. Publisher #45064537526 — SUCCESS.

Exact-source r2 CI: START #45063475205, Windows #45063475214, Win7 #45063475185, macOS Intel/ARM #45063475161 — SUCCESS. Windows і Win7 mandatory Microsoft Defender gates та post-scan integrity verification — SUCCESS.

## Що додає 10.24-r2

- окремий store `Data/CorrespondenceAttachments`, не послаблює r1 registry;
- immutable copied attachments зі stable ID `ca-...`, SHA256, MIME, size та original filename;
- content-addressed object storage: однакові байти фізично зберігаються один раз, але можуть бути явно прив'язані до різних листів;
- live `vault:vd-...` link лише на реально наявний DocumentVault без копіювання байтів;
- PDF/JPG/PNG/TIFF/DOCX із перевіркою фактичного вмісту;
- macro DOCX, symlink source, fake extension, unsafe archive paths, orphan/missing/tampered objects — fail-closed;
- active duplicate того самого SHA або vault-link у тому самому листі заборонено;
- `remove` створює історичну подію; immutable bytes фізично не видаляються;
- removed bytes продовжують проходити integrity verification;
- full workspace backup/restore зберігає registry, attachment index/history/bytes та наступні реєстраційні номери;
- attachment не змінює sent/received/delivered/signed/status.

## Наступний крок

**10.24-r3 — UI журналів і картка кореспонденції поверх уже перевірених r1+r2 API.**

Перший змістовний пакет r3:
- окреме вікно «Кореспонденція» з вкладками «Вхідні» / «Вихідні»;
- таблиці з номером, датою, кореспондентом, темою, строком, станом і наявністю вкладень;
- картка вибраного листа з усіма semantic dates, external number, summary, responsible, due/status, response/related links;
- зрозумілі дії: «Новий вхідний», «Новий вихідний», «Відповісти», «Вкладення…», «Відкрити документ», «Закрити»;
- фільтр/перехід по даті та пошук без введення дати по одному дню;
- вікно має нормально змінювати розмір і не губити кнопки;
- UI не має автоматично ставити sent/received або відкривати/надсилати e-mail;
- e-mail automation, OCR/AI і справи/ланцюжки — окремі пізніші ревізії.

Draft #543 лишається архітектурним планом. #553/#556/#562 залишаються відкритими. Draft #395 не закривати автоматично.

APPLY старих AI-import proposals не починати без окремого рішення власника.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.
