# HANDOFF_CURRENT — Taxo

**Оновлено:** 06.11.2026 (після офіційного prerelease 10.11-r10)

## База
- **Stable / Latest:** [v10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) — підтверджена stable/rollback; без змін.
- **Поточний виданий кандидат:** [v10.11-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r10) — **prerelease**, exact issued source `b239bb0dda6a49878f5f06a0edd791710b62df9b`.
- Release містить **8 assets**: Windows Setup/Portable, Windows 7 Setup/Portable, macOS ARM64/Intel, START і SHA256SUMS.
- Tag/release `v10.11-r10` immutable: не пересувати, не переписувати і не перевикористовувати номер.
- Exact-source gate перед випуском: START + Windows + Windows 7 + macOS ARM64/Intel — **SUCCESS**; publisher відмовився б створити tag без усіх чотирьох successful runs для exact SHA.
- START/regression line на r10: **888 tests / OK**.
- Release-trigger PR #200 merged; trigger main `500a1ee559a02e39bb1b8e5874688749fd84aaa4`; tag target перевірено як exact source `b239bb0dda6a49878f5f06a0edd791710b62df9b`.
- **Наступна кодова ревізія:** **10.12-r1**.
- Google Drive: остання підтверджена recovery-copy наразі r9; r10 START recovery-copy ще треба додати окремим backup-кроком.
- CI optimization PR #142/#152 — окремий напрямок; не змішувати з UX/функціоналом/security.

## Що виправлено в 10.11-r10
- У «Табелі робочого часу всіх працівників» дві паралельні кнопки PDF/Excel зведено до одного вибору формату.
- Формати пояснюють призначення: «PDF — для друку» та «Excel — для редагування».
- Є одна дія «Зберегти…».
- Загальний звіт отримує однозначне ім'я `Табель_робочого_часу_YYYY-MM_усі-працівники.*`.
- Plan/fact, БД, маршрути, графіки та розрахунки табеля не змінювались.
- PR #198 та pre-release PR #199 пройшли Windows, Win7, macOS ARM64/Intel; exact-source release gate також пройдено.

## Стан аудиту Issue #175
Закрито:
- r3: захист існуючого факту від «План → факт»;
- r3: атомарне перепланування персоналу;
- r4: захист історії тахографічних контрольних протоколів;
- r5: dependency/security slice Pillow/pypdf + окрема Win7 mitigation;
- r6: atomic output / restore error reporting / backup disclosure;
- r7: загальний Win7 regression gate на CPython 3.8.10 перед packaging;
- r8: build/release hardcoding cleanup;
- r9: workflow supply-chain hardening / immutable action pins.

З основних findings повного code-review Issue #175 критичні stabilization/release-engineering пункти закриті. Залишаються:
- системний UX — Issue #164;
- архітектурний cleanup — поступово, окремими доменними slice;
- інші non-critical findings/maintenance — лише після повторної звірки Issue #175 і фактичного GitHub.

## Наступна безпечна дія
Після завершення r10 checkpoint наступний номер за правилом ревізій — **10.12-r1**. Перед новим кодом повторно звірити UX Issue #164 та фактичний GitHub і вибрати один вузький UX slice. Не змішувати з CI optimization #142/#152 або великим architecture cleanup.

## Recovery
`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md`. Деталі: `WORKLOG.md`, Issue #61, audit Issue #175, UX Issue #164.
