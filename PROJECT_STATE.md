# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 15.11.2026.**

- Завершений product checkpoint: **10.19-r10** (PR #443).
- Exact product/release source SHA `ff93ab2ddfe92f4eb8079d890ad8e7ffd7fe03e2`.
- Test prerelease [v10.19-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r10), publisher `43758634481` SUCCESS; 4 portable + START + SHA256.
- Stable/Latest: **v10.18-r3** unchanged.
- Release PR #444 merged as `dade651e451f6ba89de7580348cad705ea8e170e`.

## Функціональний результат

r10 закриває два практичні місця документного шляху. `company.name` більше не треба дублювати вручну, якщо назва підприємства є у робочій БД: форма чернетки підставляє її як editable default, не змінюючи read-only TemplateLibrary чи власний CompanyTemplates.

Для вибраної контрольованої prepared Word-редакції додано окремий PDF/print path. PDF створюється як output-копія з конкретної r1/r2/r3…, після чого відкривається існуючим переглядачем Taxo. DOCX, catalog revision history і статус документа залишаються незмінними.

Якщо Word-файл містить embedded image, r10 fail-closed: неповний PDF не створюється мовчки. Точніший image/layout перенос — окремий наступний slice.

## CI та security gates

Exact-main: START `43757634383`, Windows `43757634381`, Win7 `43757634387`, macOS Intel/ARM `43757634384` — всі SUCCESS. START: 1362/1362. Windows/Win7 Defender і post-scan integrity PASS. Publisher `43758634481` SUCCESS; release target — exact product SHA, 6 assets. GitHub Latest/Stable підтверджено як v10.18-r3.

## Наступна ревізія

Після `10.19-r10` наступний кодовий номер — **10.20-r1**. Найближчий slice: підтримка embedded images у prepared DOCX → PDF/print із fail-closed поведінкою для ще непідтриманого складного Word layout. DocumentVault, скани/оригінали та signature/business status не змішувати з цим кроком.

## Recovery

Читати START_HERE.md → HANDOFF_CURRENT.md → private profile `profile/taxo` → звірити live GitHub. Issue #61 — журнал змін; `WORKLOG.md` — історія.

## Історичний якір (збережено)

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
