# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 16.11.2026.**

- Завершений checkpoint: **10.20-r6** (PR #466).
- Product merge: `aae93d168b0054cb106d8bfc9f58e1e766827f81`.
- Точне джерело релізу після PR #467: `5e2155e281f70dade77c5e4280a75b6634a31ffb`.
- Test prerelease [v10.20-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r6): 4 portable + START + SHA256.
- Release-trigger PR #468 merged: `60078a8193efc309e0ff509cef64b7452d452796`.
- Publisher `43904948481` — SUCCESS.
- Stable/Latest: **v10.18-r3**, без змін.

## Результат

У звичайному вікні «Документи» для документа зі сховища є **«Скани…»**. Вікно показує вже прикріплені скани та дозволяє додати PDF/JPG/JPEG/PNG/TIFF. Великі файли копіюються у фоні. Після додавання список одразу оновлюється.

Скан лишається окремим вкладенням. Його наявність не означає, що документ підписано.

## Перевірки

Джерело `5e2155e281f70dade77c5e4280a75b6634a31ffb`: **1404/1404**; Windows, Win7, macOS Intel/ARM — SUCCESS; Defender/integrity PASS. Реліз v10.20-r6 — Test Portable. Stable/Latest — v10.18-r3.

## Наступна ревізія

**10.20-r7** — явне відкриття вибраного скана з вікна вкладень.

Межі:
- кнопка «Відкрити» активна лише при вибраному скані;
- перед відкриттям файл повторно перевіряється;
- відкриття лише за дією користувача, ніколи автоматично;
- без КЕП, автоматичного «підписано», міграції старих документів і нових бізнес-статусів.

## Recovery

Читати START_HERE.md → HANDOFF_CURRENT.md → private profile `profile/taxo` → звірити live GitHub. Issue #61 — журнал змін; WORKLOG.md — історія.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
