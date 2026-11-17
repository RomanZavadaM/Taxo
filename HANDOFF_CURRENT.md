# HANDOFF_CURRENT — Taxo

**Підтверджено 17.11.2026 після звірки з live GitHub.**

## Поточний стан

- Перевірена продуктова/релізна база перед цим docs-only checkpoint: `6aa04d1229f18b9ac67409b2af34d5868353f5ec`; сам checkpoint змінює лише документацію.
- Завершена й опублікована тестова ревізія: **10.20-r8**.
- Product PR #478 merged: `05e3132003f21054e63707ec231b017bba9ec7b1`.
- Release-notes PR #479 merged; **точне джерело Test prerelease r8: `5c8513af9ee6d919d5812ebc39ee9769a83b1c44`**.
- Exact-source CI: START `44061025151` — SUCCESS, **1414/1414**; Windows `44061025064`; Windows 7 `44061025223`; macOS Intel/ARM `44061025032` — SUCCESS.
- Windows Defender та post-scan integrity — PASS.
- Release-trigger PR #480 merged: `6aa04d1229f18b9ac67409b2af34d5868353f5ec`; publisher `44065537111` — SUCCESS.
- [v10.20-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r8) — Test prerelease, рівно 6 файлів: 4 Portable + START + SHA256; tag target `5c8513af9ee6d919d5812ebc39ee9769a83b1c44`.
- **Stable / GitHub Latest: [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5)**, 8 файлів; без змін.

## Що завершено в 10.20-r8

У вікні «Скани паперових оригіналів» вибраний помилково прикріплений скан можна явно **«Прибрати»** після підтвердження.

Прибирання не стирає immutable-файл. Скан зникає з активного списку, а сам файл і запис дії лишаються у workspace та резервній копії. **«Історія…»** показує прибрані скани. Збережені байти лишаються під контролем SHA-256.

Наявність, відкриття або прибирання скана **не змінює статус документа і не означає «підписано»**. КЕП/e-signature validation, автоматичний статус підпису, фізичний purge і міграція старих документів не додавались.

## Важливий CI-факт

Перший r8 head `88b430e82dbd34b98e9fb8377fc6df9f8ac22d2d` виявив один legacy static regression r7 щодо форми керування кнопкою «Відкрити». Сумісну форму відновлено без зміни поведінки r8. Final product head `5591f01459c17277cf486b04047c2dfe1babd5b6` і exact release source `5c8513af...` повністю зелені.

## Що далі

- **10.20-r9 ще не розпочата.**
- Не перевикористовувати номер r8, tag або release.
- Наступний slice вибирати окремо після fresh GitHub verification; не додавати «заодно» КЕП, auto-signed status, міграцію або physical purge.

Незмінні правила: TemplateLibrary read-only; власні шаблони — CompanyTemplates; Stable/Latest змінюється тільки за прямою командою власника; executable не запускати вручну для перевірки безпеки.
