# HANDOFF_CURRENT — Taxo

**Оновлено:** 06.11.2026 (після офіційного prerelease 10.11-r4)

## База
- **Stable / Latest:** [v10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) — підтверджена stable/rollback; без змін.
- **Поточний виданий кандидат:** [v10.11-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r4) — **prerelease**, exact issued source `c4e701585d5ba5e06401002842f235ed3c363816`.
- Release містить **8 assets**: Windows Setup/Portable, Windows 7 Setup/Portable, macOS ARM64/Intel, START і SHA256SUMS.
- Tag/release `v10.11-r4` immutable: не пересувати, не переписувати і не перевикористовувати номер.
- Exact-main перед випуском: START #42223328213, Windows #42223328267, Windows 7 #42223328554, macOS #42223328239 — **SUCCESS**.
- Publisher #42224658087 — **SUCCESS**. Release-trigger PR #180 merged; trigger main `51b17bc51986aa7cdf19092f538ad089e540e6c9`.
- **Наступна кодова ревізія:** **10.11-r5**.
- Google Drive backup підтверджений: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r4_2026-11-06_START.zip` (1 519 882 байт).
- CI optimization PR #142/#152 — окремий напрямок; не змішувати з UX/функціоналом.

## Що виправлено в 10.11-r4
- Збережений контрольний протокол тахографа тепер захищає вихідну тахокарту від видалення.
- Додано DB-level trigger: навіть прямий `DELETE FROM discs` не може каскадно стерти пов'язаний `control_protocols`.
- UI пояснює, що історичний протокол захищений, замість тихого видалення.
- Чернеткову тахокарту без збереженого протоколу, як і раніше, можна видалити разом із чернетковими інтервалами.
- Без перебудови таблиць і без переписування існуючих протоколів.
- Нові поведінкові SQLite regression tests додані; повний exact-PR suite: **862 tests / OK**.

## Стан аудиту Issue #175
Закрито:
- r3: захист існуючого факту від «План → факт»;
- r3: атомарне перепланування персоналу;
- r4: захист історії тахографічних контрольних протоколів.

Залишаються окремими роботами:
- dependency/security slice (Pillow/pypdf, окрема сумісність Win7);
- atomic output / restore error reporting / backup disclosure;
- Win7 regression gate і release/build hardcoding;
- workflow supply-chain hardening;
- системний UX — Issue #164;
- архітектурний cleanup — поступово, після стабілізації.

## Наступна безпечна дія
Починати **10.11-r5** окремим вузьким slice. Пріоритет — dependency/security findings з Issue #175, але без змішування з UX Issue #164 або CI PR #142/#152.

## Recovery
`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md`. Деталі: `WORKLOG.md`, Issue #61, audit Issue #175, UX Issue #164.
