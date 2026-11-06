# HANDOFF_CURRENT — Taxo

**Оновлено:** 06.11.2026 (після офіційного prerelease 10.11-r6)

## База
- **Stable / Latest:** [v10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) — підтверджена stable/rollback; без змін.
- **Поточний виданий кандидат:** [v10.11-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r6) — **prerelease**, exact issued source `558158a9777b18a05a224136fec4deeef55b5950`.
- Release містить **8 assets**: Windows Setup/Portable, Windows 7 Setup/Portable, macOS ARM64/Intel, START і SHA256SUMS.
- Tag/release `v10.11-r6` immutable: не пересувати, не переписувати і не перевикористовувати номер.
- Exact-main перед випуском: START #42268068367, Windows #42268068515, Windows 7 #42268068378, macOS #42268068403 — **SUCCESS**.
- START на exact source: **872 tests / OK**.
- Publisher #42269285656 — **SUCCESS**. Release-trigger PR #186 merged; trigger main `7a0eb9fa47bdea341854959376b473b214d00475`.
- **Наступна кодова ревізія:** **10.11-r7**.
- Google Drive backup підтверджений: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r6_2026-11-06_START.zip` (1 531 200 байт).
- CI optimization PR #142/#152 — окремий напрямок; не змішувати з UX/функціоналом/security.

## Що виправлено в 10.11-r6
- Спільний writer PDF/XLSX/інших output-файлів тепер пише у sibling temp із тим самим розширенням і тільки після успіху робить атомарну заміну. Невдалий writer не псує попередній правильний файл.
- Restore main DB більше не приховує другу аварійну помилку: якщо не вдалося і відновлення, і повернення safety backup, повідомляється composite failure та точний шлях до страхової копії.
- Backup UI прямо показує, що `Data/EmployeeDocuments` входить **завжди**; базова назва ZIP більше не маскує такий backup як лише `db`.
- Оновлено ADMIN_GUIDE та regression-тести; stable і формат робочих даних не змінювались.

## Стан аудиту Issue #175
Закрито:
- r3: захист існуючого факту від «План → факт»;
- r3: атомарне перепланування персоналу;
- r4: захист історії тахографічних контрольних протоколів;
- r5: dependency/security slice Pillow/pypdf + окрема Win7 mitigation;
- r6: atomic output / restore error reporting / backup disclosure.

Залишаються окремими роботами:
- Win7 загальний regression gate;
- build/release hardcoding;
- workflow supply-chain hardening;
- системний UX — Issue #164;
- архітектурний cleanup — поступово, після стабілізації.

## Наступна безпечна дія
Починати **10.11-r7** окремим вузьким slice. Пріоритет — **Win7 загальний regression gate** з Issue #175. Не змішувати його з UX Issue #164 або CI optimization PR #142/#152; build/release hardcoding лишити наступним окремим slice.

## Recovery
`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md`. Деталі: `WORKLOG.md`, Issue #61, audit Issue #175, UX Issue #164.
