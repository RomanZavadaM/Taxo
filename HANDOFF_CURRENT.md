# HANDOFF_CURRENT — Taxo

**Оновлено:** 06.11.2026 (після офіційного prerelease 10.11-r3)

## База
- **Stable / Latest:** [v10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) — підтверджена stable/rollback; без змін.
- **Поточний виданий кандидат:** [v10.11-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r3) — **prerelease**, exact issued source `a82a3dc6f7ce63a62d7318c7f423b17599360797`.
- Release містить **8 assets**: Windows Setup/Portable, Windows 7 Setup/Portable, macOS ARM64/Intel, START і SHA256SUMS.
- Tag/release `v10.11-r3` immutable: не пересувати, не переписувати і не перевикористовувати номер.
- Exact-main перед випуском: START #42219595152, Windows #42219595132, Windows 7 #42219595055, macOS ARM64/Intel #42219595074 — **SUCCESS**.
- Publisher #42220584720 — **SUCCESS**. Release-trigger PR #177 merged; trigger main `0b2173ccc3f0942c2a364ddd95626f87e9ff2a2a`.
- **Наступна кодова ревізія:** **10.11-r4**.
- Google Drive backup підтверджений: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r3_2026-11-06_START.zip` (1 514 730 байт).
- CI optimization PR #142/#152 — окремий напрямок; не змішувати з UX/функціоналом.

## Що виправлено в 10.11-r3
- «План → факт» більше **не перезаписує існуючий факт**.
- Копіювання плану у факт вимагає явного підтвердження й працює лише там, де факт відсутній.
- Детальне перепланування персоналу стало атомарним: невдала вставка не може залишити день без старого плану.
- DB/constraint-помилка більше не маскується як звичайне «Пропущено»; batch відкочується з повідомленням.
- Додано 4 поведінкові regression tests; повний suite на exact source: **858 tests / OK**.
- Candidate/build identity синхронізовано на r3 до публікації.

## Повний code-review 06.11
Issue #175 містить повний аудит. Два найкритичніші дефекти цілісності даних закриті r3. Залишаються окремими наступними роботами:
- захист історії контрольних протоколів тахографа від каскадного видалення;
- dependency/security slice (Pillow/pypdf, окрема сумісність Win7);
- output/restore/backup disclosure hardening;
- Win7 regression gate і release/build hardcoding;
- системний UX — Issue #164;
- архітектурний cleanup — лише поступово після стабілізації.

## Наступна безпечна дія
Починати **10.11-r4** окремим вузьким slice. Пріоритет після r3 — захист історії тахографічних контрольних протоколів. Не змішувати це з dependency/security, UX Issue #164 або CI PR #142/#152.

## Recovery
`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md`. Деталі: `WORKLOG.md`, Issue #61, audit Issue #175, UX Issue #164.
