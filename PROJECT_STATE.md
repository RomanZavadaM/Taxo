# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 17.11.2026.**

- Перевірена база `main` перед цим docs-only checkpoint: `d16617ed7e094405ece7e8bb90eecd3bd778b429`.
- Завершений продуктовий checkpoint: **10.20-r9**.
- Product PR #482 merged: `3669470cd80304f0f82f6eb542664e59fbfcca1e`.
- Final product head before merge: `e490e1cdac9624d288ae38cceab08e306bafeb25`.
- Exact immutable release source after PR #483: `a607024d25557136b92c5de4a91ee1d6c7e8b1e1`.
- Exact-source CI: START `44074962416` (**1419/1419**), Windows `44074962450`, Win7 `44074962376`, macOS Intel/ARM `44074962435` — SUCCESS.
- Windows Defender та post-build/post-scan integrity — PASS.
- Release-trigger PR #484 merged: `d16617ed7e094405ece7e8bb90eecd3bd778b429`; publisher `44076489530` — SUCCESS.
- [v10.20-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r9): Test prerelease, 4 Portable + START + SHA256, exact target `a607024d25557136b92c5de4a91ee1d6c7e8b1e1`.
- **Stable/Latest: [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5)**, повний комплект із 8 файлів.
- Точне джерело Stable r5: `8a56a2da438777e1fa4549ad2a63883a2ac67e31`.

## Інтегрований результат 10.20-r9

- У каталозі «Документи» є окрема колонка «Скани».
- Для документа DocumentVault видно «Немає» або «Є: N» за активними сканами.
- Прибрані r8 скани не входять у лічильник.
- Помилка перевірки сканів не приховує каталог документів; стан явно показується користувачу.
- Бізнес-статус документа не змінюється.
- КЕП/e-signature, auto «підписано», physical purge, migration старих документів та нові формати зберігання не реалізовані.

## Активна кодова ревізія

Немає. **10.20-r10 ще не розпочата.**

## Наступна дозволена ревізія

**10.20-r10**, але лише після fresh GitHub verification та окремого визначення одного вузького slice з Issue #289. Номер r9, tag і release не перевикористовувати.

## Recovery

Читати `START_HERE.md` → `HANDOFF_CURRENT.md` → private profile `profile/taxo` → звірити live GitHub. Issue #61 — журнал змін; WORKLOG.md — історія.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
