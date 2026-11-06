# HANDOFF_CURRENT — Taxo

**Оновлено:** 06.11.2026 (після офіційного prerelease 10.11-r8)

## База
- **Stable / Latest:** [v10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) — підтверджена stable/rollback; без змін.
- **Поточний виданий кандидат:** [v10.11-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r8) — **prerelease**, exact issued source `f3e846c50e75bdc59560d10916cec90a7587cdac`.
- Release містить **8 assets**: Windows Setup/Portable, Windows 7 Setup/Portable, macOS ARM64/Intel, START і SHA256SUMS.
- Tag/release `v10.11-r8` immutable: не пересувати, не переписувати і не перевикористовувати номер.
- Exact-main перед випуском: START #42283491422, Windows #42283491587, Windows 7 #42283491399, macOS #42283491541 — **SUCCESS**.
- START на exact source: **881 tests / OK**.
- Publisher #42284631762 — **SUCCESS**. Release-trigger PR #193 merged; trigger main `cbe1e06552dc94ae78519072b3a2e57fb1ec25e3`.
- **Наступна кодова ревізія:** **10.11-r9**.
- Google Drive backup підтверджений: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r8_2026-11-06_START.zip` (1 538 476 байт).
- CI optimization PR #142/#152 — окремий напрямок; не змішувати з UX/функціоналом/security.

## Що виправлено в 10.11-r8
- `VERSION.txt` і `src/taxo/release_naming.py` є джерелом version/package tokens для active Windows, Windows 7 і macOS workflows.
- Portable/Setup/checksum names більше не треба вручну міняти між r7/r8/r9.
- `packaging/installer/Taxo.iss` не має fallback на конкретну ревізію; version/source/output явно передає build workflow.
- promotion-to-stable формує список 8 обов'язкових asset-ів з marker/version, а не з hardcoded `v10.10-r5`.
- CI реально перевірив r8-назви у Windows і Win7 artifact ZIP; macOS ARM64/Intel, Windows, Win7 — SUCCESS.
- Автоматичний publisher після merge PR #192 безпечно відмовився переписувати існуючий r7 tag; окремий PR #193 опублікував r8 від exact verified source.

## Стан аудиту Issue #175
Закрито:
- r3: захист існуючого факту від «План → факт»;
- r3: атомарне перепланування персоналу;
- r4: захист історії тахографічних контрольних протоколів;
- r5: dependency/security slice Pillow/pypdf + окрема Win7 mitigation;
- r6: atomic output / restore error reporting / backup disclosure;
- r7: загальний Win7 regression gate на CPython 3.8.10 перед packaging;
- r8: build/release hardcoding cleanup.

Залишаються окремими роботами:
- workflow supply-chain hardening;
- системний UX — Issue #164;
- архітектурний cleanup — поступово, після стабілізації.

## Наступна безпечна дія
Починати **10.11-r9** окремим вузьким slice. Пріоритет — **workflow supply-chain hardening** з Issue #175: pin official GitHub Actions до immutable commit SHA та зафіксувати regression/maintenance policy. Не змішувати з UX Issue #164 або CI optimization PR #142/#152.

## Recovery
`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md`. Деталі: `WORKLOG.md`, Issue #61, audit Issue #175, UX Issue #164.
