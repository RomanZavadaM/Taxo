# HANDOFF_CURRENT — Taxo

**Оновлено:** 06.11.2026 (після офіційного prerelease 10.11-r5)

## База
- **Stable / Latest:** [v10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) — підтверджена stable/rollback; без змін.
- **Поточний виданий кандидат:** [v10.11-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r5) — **prerelease**, exact issued source `f2614caf60380c4898c1d042bd6c8d402edc38da`.
- Release містить **8 assets**: Windows Setup/Portable, Windows 7 Setup/Portable, macOS ARM64/Intel, START і SHA256SUMS.
- Tag/release `v10.11-r5` immutable: не пересувати, не переписувати і не перевикористовувати номер.
- Exact-main перед випуском: START #42230454712, Windows #42230454659, Windows 7 #42230454846, macOS #42230454687 — **SUCCESS**.
- START на exact source: **867 tests / OK**. Win7 exact-main окремо пройшов r5 security regression на CPython 3.8.10.
- Publisher #42231569758 — **SUCCESS**. Release-trigger PR #183 merged; trigger main `fae431708a66664b238b37bf979aa84481c33898`.
- **Наступна кодова ревізія:** **10.11-r6**.
- Google Drive backup підтверджений: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r5_2026-11-06_START.zip` (1 525 891 байт).
- CI optimization PR #142/#152 — окремий напрямок; не змішувати з UX/функціоналом/security.

## Що виправлено в 10.11-r5
- Основна Windows/macOS лінія: `Pillow 11.3.0 → 13.0.0`, `pypdf 6.19.0 → 6.21.4`.
- Win7 / Python 3.8 зберігає сумісні `Pillow 10.4.0` та `pypdf 5.9.0`.
- Для старого Win7 pypdf Taxo додає власний preflight page-tree budget перед flattening: entry budget, max nodes, max depth і cycle guard.
- Бланк підтвердження та PDF stamping проходять через захищений reader.
- Додано r5 behavioral security regression; Win7 workflow запускає його на реальному CPython 3.8.10 до packaging.

## Стан аудиту Issue #175
Закрито:
- r3: захист існуючого факту від «План → факт»;
- r3: атомарне перепланування персоналу;
- r4: захист історії тахографічних контрольних протоколів;
- r5: dependency/security slice Pillow/pypdf + окрема Win7 mitigation.

Залишаються окремими роботами:
- atomic output / restore error reporting / backup disclosure;
- Win7 загальний regression gate;
- build/release hardcoding;
- workflow supply-chain hardening;
- системний UX — Issue #164;
- архітектурний cleanup — поступово, після стабілізації.

## Наступна безпечна дія
Починати **10.11-r6** окремим вузьким slice. Пріоритет — output/restore/backup disclosure hardening з Issue #175. Не змішувати це з UX Issue #164 або CI PR #142/#152.

## Recovery
`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md`. Деталі: `WORKLOG.md`, Issue #61, audit Issue #175, UX Issue #164.
