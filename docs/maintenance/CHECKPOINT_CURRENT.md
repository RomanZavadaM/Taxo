# Поточна контрольна точка Taxo

**22.11.2026 — Stable/Latest 10.23-r4; Current Test 10.24-r2.**

## Stable

- Release: [v10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4)
- Exact source: `a919ced6bc8665ced70ebb4d897808e4e2618667`
- 8 assets; owner manual acceptance 20.11.2026; stable promotion #44811800328 SUCCESS.
- 37 strict live UI routes.

## Test

- Release: [v10.24-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r2)
- Exact source: `d07f26d8e9e9db6d33278cac5a0199e2d8ae4b50`
- 8 assets; prerelease; publisher #45064537526 SUCCESS.
- START #45063475205, Windows #45063475214, Win7 #45063475185, macOS Intel/ARM #45063475161 — SUCCESS.
- Windows/Win7 mandatory Microsoft Defender malware gates + post-scan package integrity — SUCCESS.
- r1 = correspondence registry; r2 = controlled immutable attachments + live DocumentVault links + history-only remove + backup/restore.
- Attachment presence does not imply sent/received/delivered/signed.
- Stable/Latest не змінено.

## Наступний напрям

**10.24-r3 — UI журналів і картка кореспонденції.**

Потрібен один змістовний пакет: окреме resizable вікно «Кореспонденція», вкладки Вхідні/Вихідні, таблиця з номером/датою/кореспондентом/темою/строком/станом/вкладеннями, пошук і швидкий перехід по даті, детальна картка листа, Новий вхідний/Новий вихідний/Відповісти/Вкладення/Відкрити документ, явні Закрити/Скасувати. Жодного автоматичного sent/received або e-mail automation.

E-mail/OCR/AI і справи/ланцюжки — окремими пізнішими ревізіями. APPLY старого AI-import cycle не починати без окремого рішення власника.

#553/#556/#562 не закривати автоматично; draft #543/#395 не чіпати.

Актуальний стан: [PROJECT_STATE](../../PROJECT_STATE.md) · [HANDOFF](../../HANDOFF_CURRENT.md) · [WORKLOG](../../WORKLOG.md).
