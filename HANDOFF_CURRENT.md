# HANDOFF_CURRENT — Taxo

**Оновлено:** 06.11.2026 (після офіційного prerelease 10.11-r7)

## База
- **Stable / Latest:** [v10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) — підтверджена stable/rollback; без змін.
- **Поточний виданий кандидат:** [v10.11-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r7) — **prerelease**, exact issued source `3f3b28366ce7d453a70f5a2573eb676c0b503d2c`.
- Release містить **8 assets**: Windows Setup/Portable, Windows 7 Setup/Portable, macOS ARM64/Intel, START і SHA256SUMS.
- Tag/release `v10.11-r7` immutable: не пересувати, не переписувати і не перевикористовувати номер.
- Exact-main перед випуском: START #42273303324, Windows #42273303147, Windows 7 #42273303116, macOS #42273303128 — **SUCCESS**.
- START на exact source: **876 tests / OK**.
- Win7 exact-main: повний regression suite на **CPython 3.8.10** пройшов до Portable/Setup packaging.
- Publisher #42274663207 — **SUCCESS**. Release-trigger PR #189 merged; trigger main `0192e9c083c4a92ca6c5b9ec8b2df0609fce9dd9`.
- **Наступна кодова ревізія:** **10.11-r8**.
- Google Drive backup підтверджений: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r7_2026-11-06_START.zip` (1 534 531 байт).
- CI optimization PR #142/#152 — окремий напрямок; не змішувати з UX/функціоналом/security.

## Що виправлено в 10.11-r7
- Windows 7 більше не перевіряється лише вузькими r5/r6 smoke-тестами.
- Після compile-check workflow тимчасово відновлює legacy root-layout для історичних regression-тестів, як уже роблять Windows/macOS.
- На реальному CPython 3.8.10 запускається весь `unittest discover -s tests -v`; тільки після успіху дозволяється PyInstaller packaging.
- Історичні test-contract-и зроблено Python 3.8-сумісними без зміни runtime/business logic.
- Перші пробні прогони корисно виявили відсутнє legacy staging та 3.9-only `str.removeprefix()`; фінальний Win7 gate і весь platform CI — SUCCESS.

## Стан аудиту Issue #175
Закрито:
- r3: захист існуючого факту від «План → факт»;
- r3: атомарне перепланування персоналу;
- r4: захист історії тахографічних контрольних протоколів;
- r5: dependency/security slice Pillow/pypdf + окрема Win7 mitigation;
- r6: atomic output / restore error reporting / backup disclosure;
- r7: загальний Win7 regression gate на CPython 3.8.10 перед packaging.

Залишаються окремими роботами:
- build/release hardcoding;
- workflow supply-chain hardening;
- системний UX — Issue #164;
- архітектурний cleanup — поступово, після стабілізації.

## Наступна безпечна дія
Починати **10.11-r8** окремим вузьким slice. Пріоритет — **build/release hardcoding cleanup** з Issue #175: прибрати revision-specific назви з active platform workflows/installer і прибрати hardcoded `v10.10-r5` із promotion-to-stable. Не змішувати з workflow supply-chain hardening, UX Issue #164 або CI optimization PR #142/#152.

## Recovery
`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md`. Деталі: `WORKLOG.md`, Issue #61, audit Issue #175, UX Issue #164.
