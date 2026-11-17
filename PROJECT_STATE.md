# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 17.11.2026.**

- Перевірена база `main` перед цим docs-only checkpoint: `6aa04d1229f18b9ac67409b2af34d5868353f5ec`.
- Завершений продуктовий checkpoint: **10.20-r8**.
- Product PR #478 merged: `05e3132003f21054e63707ec231b017bba9ec7b1`.
- Final product head before merge: `5591f01459c17277cf486b04047c2dfe1babd5b6`.
- Exact immutable release source after PR #479: `5c8513af9ee6d919d5812ebc39ee9769a83b1c44`.
- Exact-source CI: START `44061025151` (**1414/1414**), Windows `44061025064`, Win7 `44061025223`, macOS Intel/ARM `44061025032` — SUCCESS.
- Windows Defender та post-build/post-scan integrity — PASS.
- Release-trigger PR #480 merged: `6aa04d1229f18b9ac67409b2af34d5868353f5ec`; publisher `44065537111` — SUCCESS.
- [v10.20-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r8): Test prerelease, 4 Portable + START + SHA256, exact target `5c8513af9ee6d919d5812ebc39ee9769a83b1c44`.
- **Stable/Latest: [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5)**, повний комплект із 8 файлів.
- Точне джерело Stable r5: `8a56a2da438777e1fa4549ad2a63883a2ac67e31`.

## Інтегрований результат 10.20-r8

- Вибраний скан можна явно прибрати з активного списку після підтвердження.
- Immutable-файл фізично не видаляється.
- Окремий history record зберігає дію; «Історія…» показує прибрані скани.
- Прибрані файли лишаються під integrity-контролем і входять у чинний повний backup/restore.
- Бізнес-статус документа не змінюється.
- КЕП/e-signature, auto «підписано», physical purge та migration старих документів не реалізовані.

## Активна кодова ревізія

Немає. **10.20-r9 ще не розпочата.**

## Наступна дозволена ревізія

**10.20-r9**, але лише після fresh GitHub verification та окремого визначення одного вузького slice. Номер r8, tag і release не перевикористовувати.

## Recovery

Читати `START_HERE.md` → `HANDOFF_CURRENT.md` → private profile `profile/taxo` → звірити live GitHub. Issue #61 — журнал змін; WORKLOG.md — історія.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
