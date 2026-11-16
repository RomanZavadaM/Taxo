# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 16.11.2026.**

- Поточний `main`: `5e8b65e71ba502fc2116584027881fab099d79fe`.
- Завершений продуктовий checkpoint: **10.20-r6** (PR #466).
- Product merge r6: `aae93d168b0054cb106d8bfc9f58e1e766827f81`.
- Точне джерело Test prerelease r6: `5e2155e281f70dade77c5e4280a75b6634a31ffb`.
- [v10.20-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r6): Test prerelease, 4 portable + START + SHA256.
- **Stable/Latest: [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5)**.
- Точне джерело Stable r5: `8a56a2da438777e1fa4549ad2a63883a2ac67e31`; 8 release assets.
- PR #470 перевів r5 у Stable; PR #472 виправив підвищення portable-only prerelease до повного Stable. Workflow `43910071886` — SUCCESS.

## Інтегрований результат 10.20-r6

У звичайному вікні «Документи» для документа зі сховища є **«Скани…»**. Вікно показує вже прикріплені скани та дозволяє додати PDF/JPG/JPEG/PNG/TIFF. Великі файли копіюються у фоні. Після додавання список одразу оновлюється.

Скан лишається окремим вкладенням. Його наявність не означає, що документ підписано.

## Активна, але ще не інтегрована ревізія

**10.20-r7**, PR #471, head `bd2ff059f88f38a50e730705a785dce1bf91e962`.

Уже реалізовано явне відкриття вибраного скана після повторної перевірки цілісності. START, Windows, Windows 7 і macOS перевірки PR — SUCCESS. PR відкритий, draft і mergeable.

Цей стан **не вважається інтегрованим**, доки PR #471 не merged у main.

## Наступна дія

Після recovery/docs reconciliation повторно звірити PR #471 з live main та інтегрувати готову r7, якщо mergeability/CI лишаються зеленими. Далі — exact-main перевірки і Test prerelease за чинним правилом.

Межі r7: без КЕП, автоматичного «підписано», міграції старих документів і нових бізнес-статусів.

## Recovery

Читати START_HERE.md → HANDOFF_CURRENT.md → private profile `profile/taxo` → звірити live GitHub. Issue #61 — журнал змін; WORKLOG.md — історія.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
