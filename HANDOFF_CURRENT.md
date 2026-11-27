# HANDOFF_CURRENT — Taxo

**27.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r9 опублікована й перевірена.**

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 assets, prerelease=false, GitHub Latest.

**Current Test:** [10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 assets, prerelease=true, draft=false. Publisher #46004721962 — SUCCESS. Stable/Latest лишається v10.24-r3.

## Що зроблено у 10.24-r9

r9 закриває підтверджену слабкість збереження копій документів транспортних засобів, яка існувала ще від першої реалізації цього механізму у 10.2-r1 (21.09.2026).

- новий або замінений файл документа ТЗ зберігається як власна керована копія Taxo у `Data/VehicleDocuments`;
- разом із копією зберігаються початковий шлях, розмір і SHA-256;
- інтерфейс більше не показує «Копія: Є» лише через непорожній шлях у БД: фактично розрізняються «Є», «Файл втрачено», «Копія пошкоджена», «Зовнішній файл» і «Немає»;
- відкриття копії перевіряє фактичний файл та його цілісність;
- архівування запису документа не видаляє й не відриває його копію;
- backup з відміткою «Копії документів транспортних засобів» перевіряє всі зареєстровані копії, включно з архівованими;
- legacy-запис із доступним зовнішнім файлом або збереженим source path може бути зібраний у самодостатню Taxo-копію всередині backup без зміни живої БД;
- restore backup, який заявляє включення документів ТЗ, повторно перевіряє DB → file.

Якщо старий скан уже фізично відсутній і у сховищі Taxo, і за старим шляхом, і в попередніх повних backup/перенесеннях, SQLite не містить його bytes і автоматично відтворити файл неможливо.

## Перевірки 10.24-r9

Candidate PR #643 final head `99f3fcf3b12214adf664e6d401735dd94f00d391`: START #46002324307, Windows #46002324733, Win7 #46002324330, macOS Intel/ARM #46002324335 — SUCCESS; Windows/Win7 Defender + integrity PASS.

Merged candidate / exact issued source `e3770aa72b0744eee192979a2e569651bac4f257`: START #46003120544, Windows #46003120782, Win7 #46003120506, macOS Intel/ARM #46003120628 — SUCCESS; Windows/Win7 Defender + integrity PASS.

Release-trigger PR #644 head `df993b869cc9fa518ede010da48a5cdd6927f81c`: START #46003987406, Windows #46003987089, Win7 #46003987064, macOS Intel/ARM #46003987034 — SUCCESS; Defender/integrity PASS. PR merged as `574f3acd2e078ffc1fd25a5690f5853cfe19c017`. Publisher #46004721962 — SUCCESS.

GitHub Release `v10.24-r9`: exact target `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=true, draft=false. Stable/Latest remains `v10.24-r3`.

## Що далі

- **Одна наступна дія:** вручну пройти реальне робоче сховище на r9: перевірити старі протоколи/документи ТЗ і створити backup з відміткою документів ТЗ. r9 покаже, які копії реально є, які можна забрати зі старого джерела, а які фізично втрачені.
- Issue #642 лишається відкритою до ручного приймання на реальних даних; не заявляти, що старі відсутні bytes уже відновлені.
- Наступна дозволена кодова ревізія — **10.24-r10**.
- #553/#556/#562 лишаються відкритими до відповідного ручного приймання.
- Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge не починати автоматично.
- Draft #543/#395 не закривати автоматично.

Recovery: START_HERE → HANDOFF_CURRENT → PROJECT_STATE → private `profile/taxo` → live GitHub.
