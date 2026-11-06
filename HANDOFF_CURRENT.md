# HANDOFF_CURRENT — Taxo

**Оновлено:** 06.11.2026 (після офіційного prerelease 10.11-r9)

## База
- **Stable / Latest:** [v10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) — підтверджена stable/rollback; без змін.
- **Поточний виданий кандидат:** [v10.11-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r9) — **prerelease**, exact issued source `8f97218927b3ba6bc14aca465de4a196e2b19ba2`.
- Release містить **8 assets**: Windows Setup/Portable, Windows 7 Setup/Portable, macOS ARM64/Intel, START і SHA256SUMS.
- Tag/release `v10.11-r9` immutable: не пересувати, не переписувати і не перевикористовувати номер.
- Exact-main перед випуском: START #42286505119, Windows #42286505164, Windows 7 #42286505171, macOS #42286505215 — **SUCCESS**.
- START на exact source: **885 tests / OK**.
- Publisher #42287707654 — **SUCCESS**. Release-trigger PR #196 merged; trigger main `14d6a615f06ebb23254c46ef291c34f0f9fcc795`.
- **Наступна кодова ревізія:** **10.11-r10**.
- Google Drive backup підтверджений: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r9_2026-11-06_START.zip` (1 542 152 байт).
- CI optimization PR #142/#152 — окремий напрямок; не змішувати з UX/функціоналом/security.

## Що виправлено в 10.11-r9
- У п'яти active GitHub Actions workflows `actions/checkout`, `actions/setup-python`, `actions/upload-artifact` більше не використовують рухомі `@v4/@v5`.
- Action refs pinned до конкретних 40-символьних commit SHA, звірених з офіційними major refs GitHub 06.11.2026.
- Поруч із SHA лишено коментарі `# v4` / `# v5` для контрольованого maintenance.
- `tests/test_v10_11_r9.py` забороняє повернення moving refs і перевіряє allowlist pinned SHA.
- Historical workflows у `docs/history/workflows/` не переписуються.
- Runtime/business logic, БД, UX і build naming не змінювались.
- PR-head і exact-main пройшли Windows, Win7 із повним Python 3.8 suite, macOS ARM64/Intel та START.

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
Перед **10.11-r10** повторно прочитати Issue #175 та UX Issue #164 і вибрати один вузький slice. Не починати автоматично великий architecture cleanup. Пріоритет після stabilization — системний UX Issue #164, якщо власник не задасть інший напрямок.

## Recovery
`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md`. Деталі: `WORKLOG.md`, Issue #61, audit Issue #175, UX Issue #164.
