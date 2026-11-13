# HANDOFF_CURRENT — Taxo

**13.11.2026 — код 10.18-r8 інтегрований у `main`; GitHub Stable/Latest залишається `v10.18-r3`. Виконуваний r8 НЕ публікувати: SECURITY HOLD після Firefox / Google Safe Browsing malware warning. Нова функціональність призупинена до завершення security/release cleanup.**

## Перевірений live-стан

- **`main`:** `38f5de2b43571c5cb60291e378fa85e686f5f474`; `VERSION.txt = Version: 10.18-r8`.
- **Stable/Latest:** [v10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3), `prerelease=false`, 8 assets. Stable не змінювати.
- **r8 executable release:** відсутній. Власницький workflow [run 43495315686](https://github.com/RomanZavadaM/Taxo/actions/runs/43495315686) завершився FAILURE до створення release: publisher передав порожні run IDs у `gh run download`, завантажив однаковий Windows artifact у три platform directories і зупинився, коли знайшов 3 копії Windows Portable ZIP. Це release-workflow bug, не malware verdict.
- **PR #408 — publisher fix:** [fix/publisher-artifact-isolation](https://github.com/RomanZavadaM/Taxo/pull/408), exact head `943bbd1e2c460b0a2c7f6c0b7d83479cc8108ce6`, Draft, не merged. Windows `43498832731`, Win7 `43498832585`, macOS `43498832639` — SUCCESS. Перевірено numeric exact-head run IDs, повторну перевірку `head_sha`/success, platform isolation і явний блок r8.
- **PR #406 — security candidate r9:** [security/v10.18-r9-windows-binary-gate](https://github.com/RomanZavadaM/Taxo/pull/406), exact immutable head `7537478bd4e60237cc3fc5d5f15a971ada927bdf`, Draft, не merged. r9 уже використаний для тестування через START/BAT — head і номер не переписувати. Exact-head START/Windows/Win7/macOS CI пройшли; Defender scan виконується до upload.
- **PR #407 — supply-chain audit:** [audit/windows-supply-chain-post-r9](https://github.com/RomanZavadaM/Taxo/pull/407), exact head `33428445bb8ef4b6bccf44c960ce387b9d737e22`, Draft, не merged. START/macOS/Win7 SUCCESS; Windows `43497897278` FAILURE через Defender `0x80070652 — Another installation is already in progress` на етапі оновлення сигнатур. Malware scan не стартував; це transient update conflict, не malware detection.

## Firefox / Safe Browsing — що встановлено

- Точний текст Firefox **«This file contains a virus or malware» / «Цей файл містить вірус чи іншу небезпеку»** Mozilla документує як блокування механізмом Google Safe Browsing download protection.
- Це **не** те саме, що окреме попередження «This file is not commonly downloaded».
- На Windows application-reputation перевірка може використовувати URL/referrer/redirect metadata, SHA-256, розмір/назву файлу та Authenticode-відомості.
- Отже r8 warning треба вважати фактичним Safe Browsing malware verdict для того завантаження, але **не доказом реального зараження**. Не називати false positive без конкретної vendor reclassification.
- Defender PASS r9 не скасовує Safe Browsing verdict і не закриває інцидент.

Джерела: [Mozilla Downloads help](https://support.mozilla.org/en-US/kb/where-find-and-manage-downloaded-files-firefox), [Mozilla Phishing and Malware Protection](https://support.mozilla.org/en-US/kb/how-does-phishing-and-malware-protection-work), [Mozilla Application Reputation design](https://wiki.mozilla.org/Security/Features/Application_Reputation_Design_Doc).

## Security comparison / supply chain

- r8 source, r8 integration і r9 Windows Portable мають 1116 однакових шляхів; 1113 файлів однакові за SHA-256.
- Відрізняються лише `Taxo.exe`, `_internal/base_library.zip`, `_internal/numpy-2.5.4.dist-info/RECORD`.
- r8↔r8 `Taxo.exe`: 6 байтів; r8↔r9: 11 байтів, не всі в PE header. Не описувати всі r8↔r9 відмінності як timestamp.
- 154 розпаковані файли `base_library.zip` мають однаковий SHA-256.
- Ознак великої вставки payload між цими збірками не знайдено, але shared compromised dependency/toolchain теоретично не виключений.
- Supply-chain слабкі місця: неповний hash-lock transitive wheels та Inno Setup через Chocolatey без повного version+hash trust contract.

## Безпечний порядок cleanup

1. **Не публікувати r8 і не змінювати Stable/Latest.**
2. PR #408 є першим кандидатом на інтеграцію release plumbing, бо він блокує r8 і виправляє artifact isolation. Merge тільки після явного рішення власника.
3. PR #406 не переписувати: r9 immutable/used. PR #407 залишати окремим audit evidence.
4. Після інтеграції corrected publisher створити **новий security/build-only checkpoint 10.18-r10** (не нову функціональність) на актуальному `main`: перенести r9 hardening + portable-only test publishing, зберегти #408 isolation/r8 HOLD, додати bounded retry лише для Defender `0x80070652`; усі інші update/scan errors fail closed.
5. Для звичайних ручних функціональних перевірок використовувати унікальний START/BAT source ZIP. Online `pip` усе ще не supply-chain-independent; довгостроково потрібен reviewed wheelhouse/hash-lock.

## Одна наступна дія

**Явне рішення власника щодо інтеграції PR #408 у `main`.** До цього не merge/publish, не чіпати Stable і не починати нову функціональність.

## Recovery

`START_HERE.md` → цей файл → `PROJECT_RULES.md` / `PROJECT_STATE.md` → live GitHub `main` / PR #406 / #407 / #408 / CI / Releases → private Taxo-profile. GitHub має пріоритет над документацією; після обриву STOP→READ→VERIFY→RECONCILE→CONTINUE.
