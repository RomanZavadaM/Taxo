# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 16.11.2026.**

- Завершений checkpoint: **10.20-r5** (PR #462).
- Product merge: `b569bb012981956389feb8e66bfbcd19359c5ea8`.
- Точне джерело релізу після PR #463: `8a56a2da438777e1fa4549ad2a63883a2ac67e31`.
- Test prerelease [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5): 4 portable + START + SHA256.
- Release-trigger PR #464 merged: `c0773f1cb88fb132fcda794cab727e70a618c7ca`.
- Publisher `43896901808` — SUCCESS.
- Stable/Latest: **v10.18-r3**, без змін.

## Результат

Taxo вже вміє безпечно зберігати скан паперового оригіналу як окреме незмінне вкладення до конкретного документа у сховищі. Підтримуються PDF, JPG/JPEG, PNG і TIFF. Для файла зберігаються ID, розмір і SHA-256; повторне додавання того самого файла блокується, підміна виявляється. Backup/restore зберігає вкладення.

Це поки основа без кнопки в інтерфейсі. Скан не означає «підписано».

## Перевірки

Джерело `8a56a2da438777e1fa4549ad2a63883a2ac67e31`: **1400/1400**; Windows, Win7, macOS Intel/ARM — SUCCESS; Defender/integrity PASS; backup→restore зі сканом PASS. Реліз v10.20-r5 — Test Portable. Stable/Latest — v10.18-r3.

## Наступна ревізія

**10.20-r6** — користувацька кнопка «Додати скан…» для документа у сховищі та read-only показ прикріплених сканів.

Межі:
- вибір PDF/JPG/JPEG/PNG/TIFF;
- додавання без блокування вікна;
- оновлення списку після успіху;
- показ назви/типу/розміру/контрольної суми;
- без КЕП, автоматичного «підписано», міграції старих документів і нових бізнес-статусів.

## Recovery

Читати START_HERE.md → HANDOFF_CURRENT.md → private profile `profile/taxo` → звірити live GitHub. Issue #61 — журнал змін; WORKLOG.md — історія.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
